import asyncio
import csv
import io
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aioboto3
from botocore.exceptions import ClientError

from app.database.mongodb import get_database
from app.modules.iam.models import IAMEnumerationResult
from app.utils import normalize_for_mongo

logger = logging.getLogger(__name__)

ROOT_USERNAMES = {"<root_account>", "root"}
ROOT_ARN_SUFFIX = ":root"

CONTROL_META = {
    "IAM.1": {
        "title": "IAM policies should not allow full \"$1\" administrative privileges",
        "severity": "high",
    },
    "IAM.2": {
        "title": "IAM users should not have IAM policies attached",
        "severity": "low",
    },
    "IAM.3": {
        "title": "IAM users' access keys should be rotated every 90 days or less",
        "severity": "medium",
    },
    "IAM.4": {
        "title": "IAM root user access key should not exist",
        "severity": "critical",
    },
    "IAM.5": {
        "title": "MFA should be enabled for all IAM users that have a console password",
        "severity": "medium",
    },
    "IAM.6": {
        "title": "Hardware MFA should be enabled for the root user",
        "severity": "critical",
    },
    "IAM.7": {
        "title": "Password policies for IAM users should have strong configurations",
        "severity": "medium",
    },
    "IAM.8": {
        "title": "Unused IAM user credentials should be removed",
        "severity": "medium",
    },
    "IAM.9": {
        "title": "MFA should be enabled for the root user",
        "severity": "critical",
    },
    "IAM.10": {
        "title": "Password policies for IAM users should have strong configurations",
        "severity": "medium",
    },
    "IAM.11": {
        "title": "Ensure IAM password policy requires at least one uppercase letter",
        "severity": "medium",
    },
    "IAM.12": {
        "title": "Ensure IAM password policy requires at least one lowercase letter",
        "severity": "medium",
    },
    "IAM.13": {
        "title": "Ensure IAM password policy requires at least one symbol",
        "severity": "medium",
    },
    "IAM.14": {
        "title": "Ensure IAM password policy requires at least one number",
        "severity": "medium",
    },
    "IAM.15": {
        "title": "Ensure IAM password policy requires minimum password length of 14 or greater",
        "severity": "medium",
    },
    "IAM.16": {
        "title": "Ensure IAM password policy prevents password reuse",
        "severity": "low",
    },
    "IAM.17": {
        "title": "Ensure IAM password policy expires passwords within 90 days or less",
        "severity": "low",
    },
    "IAM.18": {
        "title": "Ensure a support role has been created to manage incidents with AWS Support",
        "severity": "low",
    },
    "IAM.19": {
        "title": "MFA should be enabled for all IAM users",
        "severity": "medium",
    },
    "IAM.20": {
        "title": "Avoid the use of the root user",
        "severity": "low",
    },
    "IAM.21": {
        "title": "IAM customer managed policies that you create should not allow wildcard actions for services",
        "severity": "low",
    },
    "IAM.22": {
        "title": "IAM user credentials unused for 45 days should be removed",
        "severity": "medium",
    },
    "IAM.23": {
        "title": "IAM Access Analyzer analyzers should be tagged",
        "severity": "low",
    },
    "IAM.24": {
        "title": "IAM roles should be tagged",
        "severity": "low",
    },
    "IAM.25": {
        "title": "IAM users should be tagged",
        "severity": "low",
    },
    "IAM.26": {
        "title": "Expired SSL/TLS certificates managed in IAM should be removed",
        "severity": "medium",
    },
    "IAM.27": {
        "title": "IAM identities should not have the AWSCloudShellFullAccess policy attached",
        "severity": "medium",
    },
    "IAM.28": {
        "title": "IAM Access Analyzer external access analyzer should be enabled",
        "severity": "high",
    },
}

SERVICE_WILDCARD_RE = re.compile(r"^[a-z0-9-]+:\\*$", re.IGNORECASE)

AWS_CLOUDSHELL_POLICY_ARNS = {
    "arn:aws:iam::aws:policy/AWSCloudShellFullAccess",
    "arn:aws-cn:iam::aws:policy/AWSCloudShellFullAccess",
    "arn:aws-us-gov:iam::aws:policy/AWSCloudShellFullAccess",
}

AWS_SUPPORT_POLICY_ARN = "arn:aws:iam::aws:policy/AWSSupportAccess"

ROOT_USAGE_FILTER_PATTERN = (
    "{$.userIdentity.type=\"Root\" && $.userIdentity.invokedBy NOT EXISTS "
    "&& $.eventType !=\"AwsServiceEvent\"}"
)


def _build_aiosession(session) -> aioboto3.Session:
    creds = session.get_credentials() if session else None
    frozen = creds.get_frozen_credentials() if creds else None
    return aioboto3.Session(
        aws_access_key_id=frozen.access_key if frozen else None,
        aws_secret_access_key=frozen.secret_key if frozen else None,
        aws_session_token=frozen.token if frozen else None,
        region_name=session.region_name if session else None,
    )


def _ensure_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _parse_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    lowered = value.strip().lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    return None


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    lowered = value.strip().lower()
    if lowered in {"n/a", "no_information", "not_supported", "none"}:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _days_since(now: datetime, then: Optional[datetime]) -> Optional[int]:
    if not then:
        return None
    return (now - then).days


def _is_root_record(record: Dict[str, str]) -> bool:
    user = record.get("user", "")
    return user in ROOT_USERNAMES


def _is_root_user(user: Optional[Dict[str, Any]]) -> bool:
    if not user:
        return False
    username = user.get("UserName") or ""
    arn = user.get("Arn") or ""
    return username in ROOT_USERNAMES or arn.endswith(ROOT_ARN_SUFFIX)


def _get_required_tag_keys() -> List[str]:
    raw = os.getenv("IAM_REQUIRED_TAG_KEYS", "")
    return [key.strip() for key in raw.split(",") if key.strip()]


def _iter_statements(policy_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    statements = policy_doc.get("Statement", [])
    if isinstance(statements, dict):
        return [statements]
    if isinstance(statements, list):
        return statements
    return []


def _action_has_service_wildcard(actions: List[str]) -> bool:
    for action in actions:
        if SERVICE_WILDCARD_RE.match(action):
            return True
    return False


def _has_admin_access(statement: Dict[str, Any]) -> bool:
    if statement.get("Effect") != "Allow":
        return False
    actions = [str(a).lower() for a in _ensure_list(statement.get("Action"))]
    resources = [str(r) for r in _ensure_list(statement.get("Resource"))]
    return "*" in actions and "*" in resources


def _has_service_wildcard(statement: Dict[str, Any]) -> bool:
    if statement.get("Effect") != "Allow":
        return False
    actions = [str(a).lower() for a in _ensure_list(statement.get("Action"))]
    not_actions = [str(a).lower() for a in _ensure_list(statement.get("NotAction"))]
    return _action_has_service_wildcard(actions) or _action_has_service_wildcard(not_actions)


class IAMControlEvaluator:
    def __init__(self, scan_id: str, session, iam_result: IAMEnumerationResult):
        self.scan_id = str(scan_id)
        self.session = session
        self.aiosession = _build_aiosession(session)
        self.iam_result = iam_result
        self.now = datetime.now(timezone.utc)
        self.required_tag_keys = _get_required_tag_keys()
        self._credential_report: Optional[List[Dict[str, str]]] = None
        self._password_policy: Optional[Dict[str, Any]] = None
        self._local_policies: Optional[List[Dict[str, Any]]] = None
        self._virtual_mfa_devices: Optional[List[Dict[str, Any]]] = None
        self._support_entities: Optional[Dict[str, Any]] = None
        self._server_certs: Optional[List[Dict[str, Any]]] = None
        self._analyzers: Optional[List[Dict[str, Any]]] = None
        self._data_errors: Dict[str, str] = {}

    def _meta(self, control_id: str) -> Dict[str, str]:
        meta = CONTROL_META.get(control_id, {})
        return {
            "title": meta.get("title", control_id),
            "severity": meta.get("severity", "unknown"),
        }

    def _add_finding(
        self,
        findings: List[Dict[str, Any]],
        control_id: str,
        status: str,
        resource_type: str,
        resource_id: str,
        reason: str,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> None:
        meta = self._meta(control_id)
        findings.append(
            {
                "scan_id": self.scan_id,
                "control_id": control_id,
                "title": meta["title"],
                "severity": meta["severity"],
                "status": status,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "reason": reason,
                "evidence": evidence or {},
                "created_at": self.now.isoformat(),
            }
        )

    async def _fetch_credential_report(self) -> Optional[List[Dict[str, str]]]:
        if self._credential_report is not None:
            return self._credential_report

        try:
            async with self.aiosession.client("iam") as iam:
                for _ in range(3):
                    response = await iam.generate_credential_report()
                    if response.get("State") == "COMPLETE":
                        break
                    await asyncio.sleep(1)
                report = await iam.get_credential_report()
        except ClientError as exc:
            self._data_errors["credential_report"] = str(exc)
            self._credential_report = None
            return None

        content = report.get("Content")
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        if not content:
            self._credential_report = None
            return None

        reader = csv.DictReader(io.StringIO(content))
        self._credential_report = [row for row in reader]
        return self._credential_report

    async def _fetch_password_policy(self) -> Optional[Dict[str, Any]]:
        if self._password_policy is not None:
            return self._password_policy

        try:
            async with self.aiosession.client("iam") as iam:
                response = await iam.get_account_password_policy()
            self._password_policy = response.get("PasswordPolicy")
            return self._password_policy
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "NoSuchEntity":
                self._password_policy = None
                return None
            self._data_errors["password_policy"] = str(exc)
            self._password_policy = None
            return None

    async def _fetch_local_policies(self) -> Optional[List[Dict[str, Any]]]:
        if self._local_policies is not None:
            return self._local_policies

        policies: List[Dict[str, Any]] = []
        try:
            async with self.aiosession.client("iam") as iam:
                paginator = iam.get_paginator("list_policies")
                async for page in paginator.paginate(Scope="Local"):
                    for policy in page.get("Policies", []):
                        try:
                            version_id = policy.get("DefaultVersionId")
                            version = await iam.get_policy_version(
                                PolicyArn=policy["Arn"],
                                VersionId=version_id,
                            )
                            policies.append(
                                {
                                    "policy_name": policy.get("PolicyName"),
                                    "policy_arn": policy.get("Arn"),
                                    "document": version.get("PolicyVersion", {}).get("Document", {}),
                                    "permissions_boundary_usage": policy.get(
                                        "PermissionsBoundaryUsageCount", 0
                                    ),
                                }
                            )
                        except ClientError as exc:
                            logger.warning("Failed to read policy %s: %s", policy.get("Arn"), str(exc))
                            continue
        except ClientError as exc:
            self._data_errors["local_policies"] = str(exc)
            self._local_policies = None
            return None

        self._local_policies = policies
        return policies

    async def _fetch_virtual_mfa_devices(self) -> Optional[List[Dict[str, Any]]]:
        if self._virtual_mfa_devices is not None:
            return self._virtual_mfa_devices

        devices: List[Dict[str, Any]] = []
        try:
            async with self.aiosession.client("iam") as iam:
                paginator = iam.get_paginator("list_virtual_mfa_devices")
                async for page in paginator.paginate():
                    devices.extend(page.get("VirtualMFADevices", []))
        except ClientError as exc:
            self._data_errors["virtual_mfa"] = str(exc)
            self._virtual_mfa_devices = None
            return None

        self._virtual_mfa_devices = devices
        return devices

    async def _fetch_support_entities(self) -> Optional[Dict[str, Any]]:
        if self._support_entities is not None:
            return self._support_entities

        try:
            async with self.aiosession.client("iam") as iam:
                response = await iam.list_entities_for_policy(
                    PolicyArn=AWS_SUPPORT_POLICY_ARN
                )
        except ClientError as exc:
            self._data_errors["support_entities"] = str(exc)
            self._support_entities = None
            return None

        self._support_entities = response
        return response

    async def _fetch_server_certs(self) -> Optional[List[Dict[str, Any]]]:
        if self._server_certs is not None:
            return self._server_certs

        certs: List[Dict[str, Any]] = []
        try:
            async with self.aiosession.client("iam") as iam:
                paginator = iam.get_paginator("list_server_certificates")
                async for page in paginator.paginate():
                    certs.extend(page.get("ServerCertificateMetadataList", []))
        except ClientError as exc:
            self._data_errors["server_certs"] = str(exc)
            self._server_certs = None
            return None

        self._server_certs = certs
        return certs

    async def _fetch_access_analyzers(self) -> Optional[List[Dict[str, Any]]]:
        if self._analyzers is not None:
            return self._analyzers

        analyzers: List[Dict[str, Any]] = []
        try:
            async with self.aiosession.client("accessanalyzer") as analyzer:
                paginator = analyzer.get_paginator("list_analyzers")
                async for page in paginator.paginate():
                    for item in page.get("analyzers", []):
                        tags = await analyzer.list_tags_for_resource(resourceArn=item["arn"])
                        analyzers.append(
                            {
                                "arn": item.get("arn"),
                                "name": item.get("name"),
                                "type": item.get("type"),
                                "status": item.get("status"),
                                "tags": tags.get("tags", {}),
                            }
                        )
        except ClientError as exc:
            self._data_errors["access_analyzers"] = str(exc)
            self._analyzers = None
            return None

        self._analyzers = analyzers
        return analyzers

    def _get_root_record(self, report: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
        for record in report:
            if _is_root_record(record):
                return record
        return None

    def _get_non_root_records(self, report: List[Dict[str, str]]) -> List[Dict[str, str]]:
        return [record for record in report if not _is_root_record(record)]

    async def evaluate_all(self) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []

        await self._evaluate_iam_1(findings)
        await self._evaluate_iam_2(findings)
        await self._evaluate_iam_3(findings)
        await self._evaluate_iam_4(findings)
        await self._evaluate_iam_5(findings)
        await self._evaluate_iam_6(findings)
        await self._evaluate_iam_7(findings)
        await self._evaluate_iam_8(findings)
        await self._evaluate_iam_9(findings)
        await self._evaluate_iam_10(findings)
        await self._evaluate_iam_11(findings)
        await self._evaluate_iam_12(findings)
        await self._evaluate_iam_13(findings)
        await self._evaluate_iam_14(findings)
        await self._evaluate_iam_15(findings)
        await self._evaluate_iam_16(findings)
        await self._evaluate_iam_17(findings)
        await self._evaluate_iam_18(findings)
        await self._evaluate_iam_19(findings)
        await self._evaluate_iam_20(findings)
        await self._evaluate_iam_21(findings)
        await self._evaluate_iam_22(findings)
        await self._evaluate_iam_23(findings)
        await self._evaluate_iam_24(findings)
        await self._evaluate_iam_25(findings)
        await self._evaluate_iam_26(findings)
        await self._evaluate_iam_27(findings)
        await self._evaluate_iam_28(findings)

        return findings

    async def save_findings(self, findings: List[Dict[str, Any]]) -> int:
        if not findings:
            return 0

        db = await get_database()
        collection = db["iam_controls"]
        docs = [normalize_for_mongo(finding) for finding in findings]
        result = await collection.insert_many(docs, ordered=False)
        return len(result.inserted_ids)

    async def _evaluate_iam_1(self, findings: List[Dict[str, Any]]) -> None:
        policies = await self._fetch_local_policies()
        if policies is None:
            self._add_finding(
                findings,
                "IAM.1",
                "NO_DATA",
                "AWS::IAM::Policy",
                "account",
                "Unable to load customer managed policies.",
                {"error": self._data_errors.get("local_policies")},
            )
            return

        for policy in policies:
            if policy.get("permissions_boundary_usage", 0) > 0:
                continue
            for statement in _iter_statements(policy.get("document", {})):
                if _has_admin_access(statement):
                    self._add_finding(
                        findings,
                        "IAM.1",
                        "FAILED",
                        "AWS::IAM::Policy",
                        policy.get("policy_arn", "unknown"),
                        "Policy allows full administrative access.",
                        {
                            "policy_name": policy.get("policy_name"),
                            "statement": statement,
                        },
                    )
                    break

    async def _evaluate_iam_2(self, findings: List[Dict[str, Any]]) -> None:
        if not self.iam_result:
            self._add_finding(
                findings,
                "IAM.2",
                "NO_DATA",
                "AWS::IAM::User",
                "account",
                "IAM users were not enumerated.",
            )
            return

        for user in self.iam_result.users:
            if user.managed_policies or user.inline_policies:
                self._add_finding(
                    findings,
                    "IAM.2",
                    "FAILED",
                    "AWS::IAM::User",
                    user.username,
                    "User has policies attached directly.",
                    {
                        "managed_policies": [p.get("policy_name") for p in user.managed_policies],
                        "inline_policies": [p.get("policy_name") for p in user.inline_policies],
                    },
                )

    async def _evaluate_iam_3(self, findings: List[Dict[str, Any]]) -> None:
        if not self.iam_result:
            self._add_finding(
                findings,
                "IAM.3",
                "NO_DATA",
                "AWS::IAM::User",
                "account",
                "IAM users were not enumerated.",
            )
            return

        for user in self.iam_result.users:
            aged_keys = []
            for key in user.access_keys:
                status = (key.get("status") or "").lower()
                if status != "active":
                    continue
                created_at = _parse_datetime(key.get("create_date"))
                age_days = _days_since(self.now, created_at)
                if age_days is not None and age_days > 90:
                    aged_keys.append({
                        "access_key_id": key.get("access_key_id"),
                        "age_days": age_days,
                    })

            if aged_keys:
                self._add_finding(
                    findings,
                    "IAM.3",
                    "FAILED",
                    "AWS::IAM::User",
                    user.username,
                    "Active access keys exceed 90 days.",
                    {"keys": aged_keys},
                )

    async def _evaluate_iam_4(self, findings: List[Dict[str, Any]]) -> None:
        report = await self._fetch_credential_report()
        if not report:
            self._add_finding(
                findings,
                "IAM.4",
                "NO_DATA",
                "AWS::IAM::User",
                "root",
                "Credential report unavailable.",
                {"error": self._data_errors.get("credential_report")},
            )
            return

        root = self._get_root_record(report)
        if not root:
            self._add_finding(
                findings,
                "IAM.4",
                "NO_DATA",
                "AWS::IAM::User",
                "root",
                "Root credential record missing.",
            )
            return

        key_1 = _parse_bool(root.get("access_key_1_active"))
        key_2 = _parse_bool(root.get("access_key_2_active"))

        if key_1 or key_2:
            self._add_finding(
                findings,
                "IAM.4",
                "FAILED",
                "AWS::IAM::User",
                "root",
                "Root access key is active.",
                {"access_key_1_active": key_1, "access_key_2_active": key_2},
            )

    async def _evaluate_iam_5(self, findings: List[Dict[str, Any]]) -> None:
        report = await self._fetch_credential_report()
        if not report:
            self._add_finding(
                findings,
                "IAM.5",
                "NO_DATA",
                "AWS::IAM::User",
                "account",
                "Credential report unavailable.",
                {"error": self._data_errors.get("credential_report")},
            )
            return

        for record in self._get_non_root_records(report):
            password_enabled = _parse_bool(record.get("password_enabled"))
            mfa_active = _parse_bool(record.get("mfa_active"))
            if password_enabled and not mfa_active:
                self._add_finding(
                    findings,
                    "IAM.5",
                    "FAILED",
                    "AWS::IAM::User",
                    record.get("user", "unknown"),
                    "User has console password without MFA.",
                    {"password_enabled": password_enabled, "mfa_active": mfa_active},
                )

    async def _evaluate_iam_6(self, findings: List[Dict[str, Any]]) -> None:
        report = await self._fetch_credential_report()
        devices = await self._fetch_virtual_mfa_devices()
        if not report or devices is None:
            self._add_finding(
                findings,
                "IAM.6",
                "NO_DATA",
                "AWS::IAM::User",
                "root",
                "Root MFA device data unavailable.",
                {
                    "credential_report_error": self._data_errors.get("credential_report"),
                    "virtual_mfa_error": self._data_errors.get("virtual_mfa"),
                },
            )
            return

        root = self._get_root_record(report)
        if not root:
            self._add_finding(
                findings,
                "IAM.6",
                "NO_DATA",
                "AWS::IAM::User",
                "root",
                "Root credential record missing.",
            )
            return

        mfa_active = _parse_bool(root.get("mfa_active"))
        if not mfa_active:
            self._add_finding(
                findings,
                "IAM.6",
                "FAILED",
                "AWS::IAM::User",
                "root",
                "Root user has no MFA device.",
            )
            return

        root_has_virtual = any(_is_root_user(device.get("User")) for device in devices)
        if root_has_virtual:
            self._add_finding(
                findings,
                "IAM.6",
                "FAILED",
                "AWS::IAM::User",
                "root",
                "Root user uses virtual MFA instead of hardware MFA.",
            )

    async def _evaluate_iam_7(self, findings: List[Dict[str, Any]]) -> None:
        policy = await self._fetch_password_policy()
        if policy is None:
            if "password_policy" in self._data_errors:
                self._add_finding(
                    findings,
                    "IAM.7",
                    "NO_DATA",
                    "AWS::IAM::Account",
                    "account",
                    "Unable to read account password policy.",
                    {"error": self._data_errors.get("password_policy")},
                )
            else:
                self._add_finding(
                    findings,
                    "IAM.7",
                    "FAILED",
                    "AWS::IAM::Account",
                    "account",
                    "Account password policy is not configured.",
                )
            return

        failures = []
        if not policy.get("RequireUppercaseCharacters", False):
            failures.append("RequireUppercaseCharacters")
        if not policy.get("RequireLowercaseCharacters", False):
            failures.append("RequireLowercaseCharacters")
        if not policy.get("RequireSymbols", False):
            failures.append("RequireSymbols")
        if not policy.get("RequireNumbers", False):
            failures.append("RequireNumbers")
        if policy.get("MinimumPasswordLength", 0) < 8:
            failures.append("MinimumPasswordLength")

        if failures:
            self._add_finding(
                findings,
                "IAM.7",
                "FAILED",
                "AWS::IAM::Account",
                "account",
                "Password policy does not meet IAM.7 requirements.",
                {"missing": failures},
            )

    async def _evaluate_iam_8(self, findings: List[Dict[str, Any]]) -> None:
        await self._evaluate_unused_credentials(findings, "IAM.8", 90)

    async def _evaluate_iam_9(self, findings: List[Dict[str, Any]]) -> None:
        report = await self._fetch_credential_report()
        if not report:
            self._add_finding(
                findings,
                "IAM.9",
                "NO_DATA",
                "AWS::IAM::User",
                "root",
                "Credential report unavailable.",
                {"error": self._data_errors.get("credential_report")},
            )
            return

        root = self._get_root_record(report)
        if not root:
            self._add_finding(
                findings,
                "IAM.9",
                "NO_DATA",
                "AWS::IAM::User",
                "root",
                "Root credential record missing.",
            )
            return

        mfa_active = _parse_bool(root.get("mfa_active"))
        if not mfa_active:
            self._add_finding(
                findings,
                "IAM.9",
                "FAILED",
                "AWS::IAM::User",
                "root",
                "Root user does not have MFA enabled.",
            )

    async def _evaluate_iam_10(self, findings: List[Dict[str, Any]]) -> None:
        policy = await self._fetch_password_policy()
        if policy is None:
            if "password_policy" in self._data_errors:
                self._add_finding(
                    findings,
                    "IAM.10",
                    "NO_DATA",
                    "AWS::IAM::Account",
                    "account",
                    "Unable to read account password policy.",
                    {"error": self._data_errors.get("password_policy")},
                )
            else:
                self._add_finding(
                    findings,
                    "IAM.10",
                    "FAILED",
                    "AWS::IAM::Account",
                    "account",
                    "Account password policy is not configured.",
                )
            return

        failures = []
        if not policy.get("RequireUppercaseCharacters", False):
            failures.append("RequireUppercaseCharacters")
        if not policy.get("RequireLowercaseCharacters", False):
            failures.append("RequireLowercaseCharacters")
        if not policy.get("RequireNumbers", False):
            failures.append("RequireNumbers")
        if policy.get("MinimumPasswordLength", 0) < 7:
            failures.append("MinimumPasswordLength")
        if policy.get("PasswordReusePrevention", 0) < 4:
            failures.append("PasswordReusePrevention")
        if policy.get("MaxPasswordAge", 0) > 90:
            failures.append("MaxPasswordAge")

        if failures:
            self._add_finding(
                findings,
                "IAM.10",
                "FAILED",
                "AWS::IAM::Account",
                "account",
                "Password policy does not meet IAM.10 requirements.",
                {"missing": failures},
            )

    async def _evaluate_iam_11(self, findings: List[Dict[str, Any]]) -> None:
        await self._evaluate_password_flag(
            findings,
            "IAM.11",
            "RequireUppercaseCharacters",
            True,
            "Password policy does not require uppercase characters.",
        )

    async def _evaluate_iam_12(self, findings: List[Dict[str, Any]]) -> None:
        await self._evaluate_password_flag(
            findings,
            "IAM.12",
            "RequireLowercaseCharacters",
            True,
            "Password policy does not require lowercase characters.",
        )

    async def _evaluate_iam_13(self, findings: List[Dict[str, Any]]) -> None:
        await self._evaluate_password_flag(
            findings,
            "IAM.13",
            "RequireSymbols",
            True,
            "Password policy does not require symbols.",
        )

    async def _evaluate_iam_14(self, findings: List[Dict[str, Any]]) -> None:
        await self._evaluate_password_flag(
            findings,
            "IAM.14",
            "RequireNumbers",
            True,
            "Password policy does not require numbers.",
        )

    async def _evaluate_iam_15(self, findings: List[Dict[str, Any]]) -> None:
        policy = await self._fetch_password_policy()
        if policy is None:
            await self._add_password_policy_no_data(findings, "IAM.15")
            return

        if policy.get("MinimumPasswordLength", 0) < 14:
            self._add_finding(
                findings,
                "IAM.15",
                "FAILED",
                "AWS::IAM::Account",
                "account",
                "Password policy minimum length is less than 14.",
                {"MinimumPasswordLength": policy.get("MinimumPasswordLength")},
            )

    async def _evaluate_iam_16(self, findings: List[Dict[str, Any]]) -> None:
        policy = await self._fetch_password_policy()
        if policy is None:
            await self._add_password_policy_no_data(findings, "IAM.16")
            return

        reuse_prevention = policy.get("PasswordReusePrevention", 0)
        if reuse_prevention <= 0:
            self._add_finding(
                findings,
                "IAM.16",
                "FAILED",
                "AWS::IAM::Account",
                "account",
                "Password policy does not prevent reuse.",
                {"PasswordReusePrevention": reuse_prevention},
            )

    async def _evaluate_iam_17(self, findings: List[Dict[str, Any]]) -> None:
        policy = await self._fetch_password_policy()
        if policy is None:
            await self._add_password_policy_no_data(findings, "IAM.17")
            return

        max_age = policy.get("MaxPasswordAge", 0)
        if max_age <= 0 or max_age > 90:
            self._add_finding(
                findings,
                "IAM.17",
                "FAILED",
                "AWS::IAM::Account",
                "account",
                "Password policy expiration exceeds 90 days.",
                {"MaxPasswordAge": max_age},
            )

    async def _evaluate_iam_18(self, findings: List[Dict[str, Any]]) -> None:
        entities = await self._fetch_support_entities()
        if entities is None:
            self._add_finding(
                findings,
                "IAM.18",
                "NO_DATA",
                "AWS::IAM::Role",
                "account",
                "Unable to read policy attachments for AWSSupportAccess.",
                {"error": self._data_errors.get("support_entities")},
            )
            return

        has_entity = any(
            entities.get(key) for key in ("PolicyUsers", "PolicyGroups", "PolicyRoles")
        )
        if not has_entity:
            self._add_finding(
                findings,
                "IAM.18",
                "FAILED",
                "AWS::IAM::Role",
                "account",
                "AWSSupportAccess policy is not attached to any IAM identity.",
            )

    async def _evaluate_iam_19(self, findings: List[Dict[str, Any]]) -> None:
        report = await self._fetch_credential_report()
        if not report:
            self._add_finding(
                findings,
                "IAM.19",
                "NO_DATA",
                "AWS::IAM::User",
                "account",
                "Credential report unavailable.",
                {"error": self._data_errors.get("credential_report")},
            )
            return

        for record in self._get_non_root_records(report):
            mfa_active = _parse_bool(record.get("mfa_active"))
            if not mfa_active:
                self._add_finding(
                    findings,
                    "IAM.19",
                    "FAILED",
                    "AWS::IAM::User",
                    record.get("user", "unknown"),
                    "User does not have MFA enabled.",
                    {"mfa_active": mfa_active},
                )

    async def _evaluate_iam_20(self, findings: List[Dict[str, Any]]) -> None:
        try:
            async with self.aiosession.client("cloudtrail") as cloudtrail:
                trail_response = await cloudtrail.describe_trails(includeShadowTrails=False)
            trails = trail_response.get("trailList", [])
        except ClientError as exc:
            self._add_finding(
                findings,
                "IAM.20",
                "NO_DATA",
                "AWS::CloudTrail::Trail",
                "account",
                "Unable to read CloudTrail trails.",
                {"error": str(exc)},
            )
            return

        trail = None
        for candidate in trails:
            if candidate.get("IsMultiRegionTrail") and candidate.get("IncludeGlobalServiceEvents"):
                trail = candidate
                break

        if not trail:
            self._add_finding(
                findings,
                "IAM.20",
                "FAILED",
                "AWS::CloudTrail::Trail",
                "account",
                "No multi-Region CloudTrail with global service events found.",
            )
            return

        log_group_arn = trail.get("CloudWatchLogsLogGroupArn")
        if not log_group_arn:
            self._add_finding(
                findings,
                "IAM.20",
                "FAILED",
                "AWS::Logs::LogGroup",
                trail.get("TrailARN", "unknown"),
                "CloudTrail trail is not configured with a CloudWatch Logs group.",
            )
            return

        log_group_name = log_group_arn.split(":log-group:")[-1].split(":*")[0]

        try:
            async with self.aiosession.client("logs") as logs:
                filters_response = await logs.describe_metric_filters(logGroupName=log_group_name)
            metric_filters = filters_response.get("metricFilters", [])
        except ClientError as exc:
            self._add_finding(
                findings,
                "IAM.20",
                "NO_DATA",
                "AWS::Logs::MetricFilter",
                log_group_name,
                "Unable to read metric filters for the CloudTrail log group.",
                {"error": str(exc)},
            )
            return

        target_filter = None
        for metric_filter in metric_filters:
            if metric_filter.get("filterPattern") == ROOT_USAGE_FILTER_PATTERN:
                target_filter = metric_filter
                break

        if not target_filter:
            self._add_finding(
                findings,
                "IAM.20",
                "FAILED",
                "AWS::Logs::MetricFilter",
                log_group_name,
                "Root usage metric filter is missing.",
            )
            return

        metric_transforms = target_filter.get("metricTransformations", [])
        if not metric_transforms:
            self._add_finding(
                findings,
                "IAM.20",
                "FAILED",
                "AWS::CloudWatch::Alarm",
                log_group_name,
                "Metric filter has no metric transformations.",
            )
            return

        alarm_actions = []
        try:
            async with self.aiosession.client("cloudwatch") as cloudwatch:
                for transform in metric_transforms:
                    alarms = await cloudwatch.describe_alarms_for_metric(
                        MetricName=transform.get("metricName"),
                        Namespace=transform.get("metricNamespace"),
                    )
                    for alarm in alarms.get("MetricAlarms", []):
                        alarm_actions.extend(alarm.get("AlarmActions", []))
        except ClientError as exc:
            self._add_finding(
                findings,
                "IAM.20",
                "NO_DATA",
                "AWS::CloudWatch::Alarm",
                log_group_name,
                "Unable to read CloudWatch alarms for metric filter.",
                {"error": str(exc)},
            )
            return

        sns_topics = [action for action in alarm_actions if action.startswith("arn:aws:sns")]
        if not sns_topics:
            self._add_finding(
                findings,
                "IAM.20",
                "FAILED",
                "AWS::CloudWatch::Alarm",
                log_group_name,
                "No CloudWatch alarm with SNS action found for root usage metric.",
            )
            return

        for topic_arn in sns_topics:
            try:
                async with self.aiosession.client("sns") as sns:
                    subs = await sns.list_subscriptions_by_topic(TopicArn=topic_arn)
                if subs.get("Subscriptions"):
                    return
            except ClientError:
                continue

        self._add_finding(
            findings,
            "IAM.20",
            "FAILED",
            "AWS::SNS::Topic",
            sns_topics[0],
            "SNS topic has no subscriptions for root usage alarms.",
        )

    async def _evaluate_iam_21(self, findings: List[Dict[str, Any]]) -> None:
        policies = await self._fetch_local_policies()
        if policies is None:
            self._add_finding(
                findings,
                "IAM.21",
                "NO_DATA",
                "AWS::IAM::Policy",
                "account",
                "Unable to load customer managed policies.",
                {"error": self._data_errors.get("local_policies")},
            )
            return

        for policy in policies:
            if policy.get("permissions_boundary_usage", 0) > 0:
                continue
            for statement in _iter_statements(policy.get("document", {})):
                if _has_service_wildcard(statement):
                    self._add_finding(
                        findings,
                        "IAM.21",
                        "FAILED",
                        "AWS::IAM::Policy",
                        policy.get("policy_arn", "unknown"),
                        "Policy allows wildcard actions for a service.",
                        {
                            "policy_name": policy.get("policy_name"),
                            "statement": statement,
                        },
                    )
                    break

    async def _evaluate_iam_22(self, findings: List[Dict[str, Any]]) -> None:
        await self._evaluate_unused_credentials(findings, "IAM.22", 45)

    async def _evaluate_iam_23(self, findings: List[Dict[str, Any]]) -> None:
        analyzers = await self._fetch_access_analyzers()
        if analyzers is None:
            self._add_finding(
                findings,
                "IAM.23",
                "NO_DATA",
                "AWS::AccessAnalyzer::Analyzer",
                "account",
                "Unable to read Access Analyzer analyzers.",
                {"error": self._data_errors.get("access_analyzers")},
            )
            return

        if not analyzers:
            self._add_finding(
                findings,
                "IAM.23",
                "NO_DATA",
                "AWS::AccessAnalyzer::Analyzer",
                "account",
                "No Access Analyzer analyzers found.",
            )
            return

        for analyzer in analyzers:
            tags = analyzer.get("tags", {})
            non_system_keys = [k for k in tags.keys() if not k.lower().startswith("aws:")]
            if self.required_tag_keys:
                missing = [k for k in self.required_tag_keys if k not in tags]
                if missing:
                    self._add_finding(
                        findings,
                        "IAM.23",
                        "FAILED",
                        "AWS::AccessAnalyzer::Analyzer",
                        analyzer.get("arn", "unknown"),
                        "Access Analyzer is missing required tag keys.",
                        {"missing": missing},
                    )
            else:
                if not non_system_keys:
                    self._add_finding(
                        findings,
                        "IAM.23",
                        "FAILED",
                        "AWS::AccessAnalyzer::Analyzer",
                        analyzer.get("arn", "unknown"),
                        "Access Analyzer has no non-system tags.",
                    )

    async def _evaluate_iam_24(self, findings: List[Dict[str, Any]]) -> None:
        if not self.iam_result:
            self._add_finding(
                findings,
                "IAM.24",
                "NO_DATA",
                "AWS::IAM::Role",
                "account",
                "IAM roles were not enumerated.",
            )
            return

        for role in self.iam_result.roles:
            tag_keys = [tag.get("Key") for tag in role.tags if tag.get("Key")]
            if self.required_tag_keys:
                missing = [k for k in self.required_tag_keys if k not in tag_keys]
                if missing:
                    self._add_finding(
                        findings,
                        "IAM.24",
                        "FAILED",
                        "AWS::IAM::Role",
                        role.role_name,
                        "Role is missing required tag keys.",
                        {"missing": missing},
                    )
            else:
                if not tag_keys:
                    self._add_finding(
                        findings,
                        "IAM.24",
                        "FAILED",
                        "AWS::IAM::Role",
                        role.role_name,
                        "Role has no tags.",
                    )

    async def _evaluate_iam_25(self, findings: List[Dict[str, Any]]) -> None:
        if not self.iam_result:
            self._add_finding(
                findings,
                "IAM.25",
                "NO_DATA",
                "AWS::IAM::User",
                "account",
                "IAM users were not enumerated.",
            )
            return

        for user in self.iam_result.users:
            tag_keys = [tag.get("Key") for tag in user.tags if tag.get("Key")]
            if self.required_tag_keys:
                missing = [k for k in self.required_tag_keys if k not in tag_keys]
                if missing:
                    self._add_finding(
                        findings,
                        "IAM.25",
                        "FAILED",
                        "AWS::IAM::User",
                        user.username,
                        "User is missing required tag keys.",
                        {"missing": missing},
                    )
            else:
                if not tag_keys:
                    self._add_finding(
                        findings,
                        "IAM.25",
                        "FAILED",
                        "AWS::IAM::User",
                        user.username,
                        "User has no tags.",
                    )

    async def _evaluate_iam_26(self, findings: List[Dict[str, Any]]) -> None:
        certs = await self._fetch_server_certs()
        if certs is None:
            self._add_finding(
                findings,
                "IAM.26",
                "NO_DATA",
                "AWS::IAM::ServerCertificate",
                "account",
                "Unable to read IAM server certificates.",
                {"error": self._data_errors.get("server_certs")},
            )
            return

        for cert in certs:
            expiration = cert.get("Expiration")
            if isinstance(expiration, str):
                expiration = _parse_datetime(expiration)
            if isinstance(expiration, datetime) and expiration < self.now:
                self._add_finding(
                    findings,
                    "IAM.26",
                    "FAILED",
                    "AWS::IAM::ServerCertificate",
                    cert.get("Arn", cert.get("ServerCertificateName", "unknown")),
                    "Server certificate is expired.",
                    {"expiration": expiration.isoformat()},
                )

    async def _evaluate_iam_27(self, findings: List[Dict[str, Any]]) -> None:
        if not self.iam_result:
            self._add_finding(
                findings,
                "IAM.27",
                "NO_DATA",
                "AWS::IAM::Policy",
                "account",
                "IAM identities were not enumerated.",
            )
            return

        for user in self.iam_result.users:
            if self._has_cloudshell_policy(user.managed_policies):
                self._add_finding(
                    findings,
                    "IAM.27",
                    "FAILED",
                    "AWS::IAM::User",
                    user.username,
                    "User has AWSCloudShellFullAccess attached.",
                )

        for role in self.iam_result.roles:
            if self._has_cloudshell_policy(role.managed_policies):
                self._add_finding(
                    findings,
                    "IAM.27",
                    "FAILED",
                    "AWS::IAM::Role",
                    role.role_name,
                    "Role has AWSCloudShellFullAccess attached.",
                )

        for group in self.iam_result.groups:
            if self._has_cloudshell_policy(group.managed_policies):
                self._add_finding(
                    findings,
                    "IAM.27",
                    "FAILED",
                    "AWS::IAM::Group",
                    group.group_name,
                    "Group has AWSCloudShellFullAccess attached.",
                )

    async def _evaluate_iam_28(self, findings: List[Dict[str, Any]]) -> None:
        analyzers = await self._fetch_access_analyzers()
        if analyzers is None:
            self._add_finding(
                findings,
                "IAM.28",
                "NO_DATA",
                "AWS::AccessAnalyzer::Analyzer",
                "account",
                "Unable to read Access Analyzer analyzers.",
                {"error": self._data_errors.get("access_analyzers")},
            )
            return

        active = [a for a in analyzers if a.get("status") == "ACTIVE"]
        if not active:
            self._add_finding(
                findings,
                "IAM.28",
                "FAILED",
                "AWS::AccessAnalyzer::Analyzer",
                "account",
                "No active Access Analyzer found in this Region.",
            )

    async def _evaluate_password_flag(
        self,
        findings: List[Dict[str, Any]],
        control_id: str,
        field_name: str,
        expected_value: Any,
        reason: str,
    ) -> None:
        policy = await self._fetch_password_policy()
        if policy is None:
            await self._add_password_policy_no_data(findings, control_id)
            return

        if policy.get(field_name) != expected_value:
            self._add_finding(
                findings,
                control_id,
                "FAILED",
                "AWS::IAM::Account",
                "account",
                reason,
                {field_name: policy.get(field_name)},
            )

    async def _add_password_policy_no_data(
        self, findings: List[Dict[str, Any]], control_id: str
    ) -> None:
        if "password_policy" in self._data_errors:
            self._add_finding(
                findings,
                control_id,
                "NO_DATA",
                "AWS::IAM::Account",
                "account",
                "Unable to read account password policy.",
                {"error": self._data_errors.get("password_policy")},
            )
        else:
            self._add_finding(
                findings,
                control_id,
                "FAILED",
                "AWS::IAM::Account",
                "account",
                "Account password policy is not configured.",
            )

    def _has_cloudshell_policy(self, policies: List[Dict[str, Any]]) -> bool:
        for policy in policies:
            if policy.get("policy_arn") in AWS_CLOUDSHELL_POLICY_ARNS:
                return True
        return False

    async def _evaluate_unused_credentials(
        self,
        findings: List[Dict[str, Any]],
        control_id: str,
        max_age_days: int,
    ) -> None:
        report = await self._fetch_credential_report()
        if not report:
            self._add_finding(
                findings,
                control_id,
                "NO_DATA",
                "AWS::IAM::User",
                "account",
                "Credential report unavailable.",
                {"error": self._data_errors.get("credential_report")},
            )
            return

        for record in self._get_non_root_records(report):
            user = record.get("user", "unknown")
            violations = []

            password_enabled = _parse_bool(record.get("password_enabled"))
            if password_enabled:
                last_used = _parse_datetime(record.get("password_last_used"))
                age_days = _days_since(self.now, last_used)
                if age_days is None or age_days > max_age_days:
                    violations.append({
                        "credential": "password",
                        "age_days": age_days,
                    })

            for key_index in ("1", "2"):
                active = _parse_bool(record.get(f"access_key_{key_index}_active"))
                if not active:
                    continue
                last_used = _parse_datetime(record.get(f"access_key_{key_index}_last_used_date"))
                age_days = _days_since(self.now, last_used)
                if age_days is None or age_days > max_age_days:
                    violations.append({
                        "credential": f"access_key_{key_index}",
                        "age_days": age_days,
                    })

            if violations:
                self._add_finding(
                    findings,
                    control_id,
                    "FAILED",
                    "AWS::IAM::User",
                    user,
                    "User credentials are unused beyond the allowed age.",
                    {"violations": violations, "max_age_days": max_age_days},
                )


async def evaluate_iam_controls(
    scan_id: str, session, iam_result: IAMEnumerationResult
) -> Dict[str, Any]:
    evaluator = IAMControlEvaluator(scan_id=scan_id, session=session, iam_result=iam_result)
    findings = await evaluator.evaluate_all()
    saved = await evaluator.save_findings(findings)
    return {"findings": len(findings), "saved": saved}
