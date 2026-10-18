# Design Section

## 1. System Architecture Overview
The system was designed as a two-tier web application that separated a React-based client from a FastAPI backend. The backend was planned to orchestrate AWS enumeration, normalize scan artifacts, and optionally trigger multi-stage analysis, while the frontend was planned to provide scan management and result visualization. The architecture was centered on a scan pipeline that collected AWS IAM, S3, and Lambda data through AWS APIs, persisted structured artifacts to MongoDB, and stored user, environment, scan metadata, and billing data in PostgreSQL.

[Insert Diagram: System Architecture Overview — use attached architecture diagram]

Mermaid (optional regenerate):
```mermaid
flowchart LR
  subgraph Frontend[Frontend (React + Vite)]
    UI[Visualization and Analysis Views]
  end

  subgraph Backend[FastAPI Backend]
    Core[Core Engine]
    Enum[Enumeration Layer]
    Norm[Normalization Layer]
    Reason[Reasoning Layer (GenAI)]
    Exploit[Command Generation]
  end

  AWS[(AWS APIs)]
  PG[(PostgreSQL)]
  MDB[(MongoDB)]
  LLM[(Gemini API)]

  UI -->|REST| Core
  Core --> Enum --> AWS
  Enum --> Norm --> MDB
  Core --> Reason --> LLM
  Reason --> Exploit
  Core --> PG
```

## 2. Component / Module Breakdown
The backend was planned as layered modules with routing, service orchestration, and data access separation. The scan flow was centered on a `ScanService` that validated user access, created a scan record, and called the enumerators. The enumerators were split by AWS service to isolate concerns and simplify testing.

- **Routers**: `/auth`, `/environments`, `/scans`, `/genai`, `/dashboard`, `/payment`, `/subscription` were defined to partition authentication, environment management, scanning, analysis, dashboards, and billing.
- **Services**: authentication and OTP verification, environment lifecycle, scan orchestration, AI analysis, dashboards, payments, and subscription changes were implemented as dedicated service classes.
- **Enumerators**: IAM (users/roles/groups, policies, tags, keys), S3 (buckets, policy, encryption, versioning, tags), and Lambda (functions, layers, configuration) were implemented as separate enumerators called in parallel.
- **Analysis Pipeline**: preprocessing, deterministic risk scoring, and multi-stage Gemini prompts (triage, deep analysis, command generation) were designed as isolated stages.

The frontend was planned as a React SPA with page-level routes for scans, environments, subscriptions, and analysis, backed by TanStack Query for API state management.

## 3. Database Schema Design
The data layer was split to keep relational metadata in PostgreSQL and high-volume scan artifacts in MongoDB. PostgreSQL stored users, environments, scans, plans, subscriptions, and payment-related entities. MongoDB stored enumeration outputs (IAM, S3, Lambda) and analysis artifacts.

[Insert Diagram: Database Schema — use attached ER diagram]

Mermaid (high-level ERD):
```mermaid
erDiagram
  USERS ||--|| SUBSCRIPTIONS : has
  USERS ||--o{ ENVIRONMENTS : owns
  ENVIRONMENTS ||--o{ SCANS : runs
  PLANS ||--o{ SUBSCRIPTIONS : defines
  PLANS ||--o{ PLAN_PADDLE_PRICES : maps
  USERS ||--o{ PAYMENT_TRANSACTIONS : pays
  SUBSCRIPTIONS ||--o{ BILLING_LEDGER : records
  PAYMENT_TRANSACTIONS ||--o{ BILLING_LEDGER : records

  USERS {
    uuid id
    string email
    string password
    bool verified
  }
  ENVIRONMENTS {
    uuid id
    string name
    string access_key
    string secret_access_key
    string region
    uuid user_id
  }
  SCANS {
    uuid id
    string scan_name
    string status
    enum mode
    uuid environment_id
  }
```

MongoDB collections were planned for `iam_users`, `iam_roles`, `iam_groups`, `s3_buckets`, `lambda_functions`, `lambda_layers`, and `attack_analysis`, with an additional `iam_controls` collection for control findings.

## 4. Use Case & Flow Diagrams
The design formalized flows for registration/login, environment management, scan creation, enumeration, and optional analysis generation. The scan flow was intentionally asynchronous, allowing enumeration to complete before AI analysis stages.

[Insert Diagram: Use Case Diagram — use attached use case diagram]

Mermaid (optional use-case flow):
```mermaid
flowchart LR
  Analyst[Security Analyst]
  Analyst --> Auth[Register / Login]
  Analyst --> Env[Manage Environments]
  Analyst --> Scan[Create Scan]
  Scan --> Enum[IAM/S3/Lambda Enumeration]
  Enum --> Results[Store Results]
  Results --> Analysis[Optional GenAI Analysis]
  Analysis --> View[View Results]
```

## 5. Technology / Tool Selection with Justification
- **FastAPI + Uvicorn** were selected for async HTTP handling and clear router/service boundaries.
- **SQLAlchemy (async)** was selected to model relational entities and support PostgreSQL constraints.
- **MongoDB (motor)** was selected to store nested enumeration artifacts without rigid schema changes.
- **aioboto3 / boto3** were selected to access AWS IAM, S3, and Lambda APIs asynchronously.
- **Gemini API** was selected to support multi-stage analysis and command generation.
- **React + Vite + TailwindCSS + Radix UI** were selected to build a responsive, componentized SPA.
- **Prometheus instrumentation and structured logging** were selected for observability and operational insights.
- **Paddle SDK and Resend** were selected for billing workflows and OTP email delivery.

## 6. API Structure Planning
The API was designed to be resource-oriented and scoped to user ownership.

- `POST /auth/*` handled registration, login, OTP verification, password reset, and logout.
- `GET/POST/DELETE /environments` managed AWS credential environments.
- `GET/POST /scans` created scans and listed history; `GET /scans/{id}/results` returned artifacts.
- `GET /genai/{scan_id}` returned analysis results.
- `GET /dashboard/*` returned summary analytics.
- `POST /payment/*` and `POST /subscription/*` managed plans and billing workflows.
- `/health` and `/metrics` exposed operational health and telemetry.

## 7. Security Design Decisions
Security controls were planned around identity verification, credential isolation, and least-privilege access.

- **Authentication** used JWT tokens and a token blacklist for logout invalidation.
- **OTP verification** enforced resend limits, expiration, and lockout to reduce abuse.
- **Password storage** used server-side hashing via passlib.
- **Credential isolation** was enforced by scoping all environment and scan access to the authenticated user.
- **CORS** was restricted to explicit frontend origins.
- **STS validation** was used to test AWS credentials before scans.
- **Operational safeguards** included rate-limited error handling, structured logs, and metrics.

5. IMPLEMENTATION
5.1 IMPLEMENTATION OVERVIEW
The implementation focused on delivering a complete, end-to-end user experience rather than isolated features. The system was built to guide a user through account creation, environment setup, scan execution, and results review in a way that remained clear and predictable. This approach ensured that the working product aligned with the goals defined during planning and provided a consistent experience across multiple scan types.

5.2 MODULE DEVELOPMENT
The working system was organized into functional parts that matched the user journey. Account access and verification were implemented as a single, consistent flow, environment management was implemented to store and validate connected targets, and scan execution was implemented to collect and organize findings. Separate areas were implemented for dashboards, billing workflows, and optional deeper analysis so that each area could evolve without disturbing the core scan path.

5.3 CORE LOGIC AND DECISION RULES
The core logic enforced ownership checks before any scan ran, and it ensured that each scan produced a structured set of findings. A scoring step summarized overall risk, and optional deeper analysis used this summary to decide whether more detailed output was needed. These decision rules kept the system consistent across different scan depths while keeping the outcomes understandable for the user.

5.4 RUNTIME INTERACTION
At runtime, a scan request initiated data collection, saved the results, and updated the scan status so progress could be shown. When analysis was enabled, a separate analysis record was created and linked to the scan so users could review both raw findings and interpreted results. The user interface then loaded these records on demand to keep the experience responsive.

5.5 CHALLENGES AND RESOLUTIONS
Several practical challenges were encountered, including long-running scans, partial data availability, and the need for clear feedback when something failed. These were addressed by allowing scans to run in the background, by presenting partial results when safe to do so, and by providing plain error messages that explained what happened and what could be done next. Ownership checks and validation were emphasized to prevent incorrect scans and protect sensitive environments.

5.6 EXTERNAL INTEGRATIONS
The system integrated external services only where they clearly improved the user experience and system completeness. These integrations supported cloud access, account verification, subscription handling, and automated analysis, while keeping the core scan workflow independent and reliable.

5.7 DATA RECORDS AND COLLECTIONS CREATED
The implementation created dedicated records for users, environments, scans, plans, subscriptions, payment transactions, subscription change requests, billing ledger entries, webhook events, verification codes, and revoked tokens. Scan artifacts were stored in separate collections named iam_users, iam_roles, iam_groups, s3_buckets, lambda_functions, lambda_layers, attack_analysis, and iam_controls to support growth of findings without complicating user account data.

5.8 KEY CODE SNIPPETS (SYSTEM BACKBONE)
The following excerpts represent the core runtime flow that drives scans and analysis in the system. They demonstrate how user requests trigger enumeration, how service data is gathered, and how analysis is generated and stored.

Scan creation and orchestration:
```python
  async def create_scan(self, scan_data, current_user: CurrentUser):
    active_scans.inc()
    start_time = time.time()
    scan = None
        
    try:
      sub = await self.sub_repo.get_subscription_by_user(current_user.id)
      if sub.current_scans_per_month >= current_user.max_scans_per_month:
        raise HTTPException(
          status_code=status.HTTP_403_FORBIDDEN, 
          detail="Scan limit reached for the current subscription."
        )
            
      environment = await self.env_repo.get_by_id(scan_data.environment_id)
      if not environment:
        raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail="Environment not found",
        )
      if str(environment.user_id) != str(current_user.id):
        raise HTTPException(
          status_code=status.HTTP_403_FORBIDDEN,
          detail="Unauthorized access to environment",
        )
            
      scan = await self.scan_repo.create(scan_data, status="running")
      results = await self.enum.run_enumeration(scan.id, environment)

      if scan_data.mode == ScanMode.analysis:
        scan_results = await self.get_scan_results(str(scan.id), current_user.id)
        await self.genai_service.attack_path(str(scan.id), current_user, scan_results)

      await self.scan_repo.update_status(scan.id, "completed")
      await self.user_repo.increment_scans_per_month(current_user.id)
      scans_total.labels(status='completed').inc()

      return scan
    except Exception as e:
      if scan:
        await self.scan_repo.update_status(scan.id, "failed")
      scans_total.labels(status='failed').inc()
      logging.error(f"Scan creation failed: {str(e)}")
      raise
    finally:
      duration = time.time() - start_time
      scan_duration_seconds.labels(scan_type=scan_data.mode.value).observe(duration)
      active_scans.dec()
```

Parallel service enumeration coordination:
```python
  async def run_enumeration(self, scan_id: str, environment):

    session = AWSCredentialManager(
      access_key_id=environment.access_key,
      secret_access_key=environment.secret_access_key,
      region=environment.region
    ).create_session()

    try:
      iam_data, s3_data, lambda_data = await asyncio.gather(
        get_iam_data(scan_id, session=session),
        get_s3_data(scan_id, session=session),
        get_lambda_data(scan_id, session=session),
      )

    except Exception as e:
      raise RuntimeError(f"Enumeration failed: {str(e)}")

    return {
      "iam": iam_data,
      "s3": s3_data,
      "lambda": lambda_data
    }
```

IAM enumeration with persistence and controls evaluation:
```python
    result = await enumerator.enumerate_all(
      scan_id=scan_id,
      exclude_service_roles=True
    )
        
    resource_mappings = {
      "users": "users",
      "roles": "roles",
      "groups": "groups"
    }
        
    db_save_summary = await save_snapshot(
      service_name="iam",
      result=result,
      resource_mappings=resource_mappings
    )

    controls_summary = await evaluate_iam_controls(
      scan_id=scan_id,
      session=session,
      iam_result=result,
    )
```

Analysis pipeline and result storage:
```python
      enum_data = convert_dataclasses_to_dict(scan_results)
      processed_data = self.preprocessor.preprocess_enumeration_data(enum_data)
      risk_summary = self.risk_analyzer.analyze(processed_data)

      triage_result = None
      analysis_result = None
      commands_result = None

      if analysis_level in {'triage', 'deep', 'exploit'}:
        triage_result = await self.gemini.triage(risk_summary)
                
      severity = triage_result.get('severity', 'low') if triage_result else 'low'
      requires_deep = triage_result.get('requires_deep_analysis', False) if triage_result else False
                
      if severity in ['critical', 'high'] or requires_deep:
        if analysis_level in {'deep', 'exploit'}:
          analysis_result = await self.gemini.deep_analysis(processed_data, triage_result)
                    
        if analysis_level == 'exploit':
          attack_paths = analysis_result.get('attack_paths', [])
          commands_result = await self.gemini.generate_commands(attack_paths)

      ap = AttackPath(
        scan_id=scan_id,
        severity=severity,
        triage=triage_result,
        analysis=analysis_result,
        commands=commands_result,
        risk_summary=risk_summary
      )

      result_id = await store_result(
        "attack_analysis",
        ap
      )
```

6. FUTURE WORK
The next phase of development will broaden AWS coverage beyond IAM, S3, and Lambda so the platform reflects how modern cloud environments are actually structured. Extending enumeration and control evaluation to EC2, RDS, VPC, CloudTrail, CloudWatch, EKS/ECS, KMS, and Secrets Manager will enable richer cross-service reasoning and remove blind spots that currently limit risk interpretation. This expansion also allows the analysis layer to correlate identity, network, data, and compute findings in a single narrative rather than isolated service reports.

Another priority is moving from analysis-only outputs to fully automated, authorized execution flows. The intent is not to run unsafe actions by default, but to introduce a controlled mode where users explicitly approve each action and the system applies safety guardrails, validation, and rollback-aware steps. This approach provides practical exploit validation in permitted environments while preserving accountability and preventing accidental changes.

Command generation will also be improved so that the output is precise, context-aware, and consistently valid. Future work will enforce stricter output schemas, add deterministic validation on generated commands, and incorporate environment-specific parameters where available. The goal is to reduce ambiguity and ensure that each command can be executed with minimal modification while still being tailored to the target context.

Compliance mapping will be extended to additional AWS services and benchmark families to make the platform useful for audit preparation as well as technical remediation. By aligning findings with recognized controls across more services, users can move from raw findings to evidence-based compliance reporting in a single workflow.

Ultimately, the long-term vision is to evolve the system into a unified platform that combines vulnerability assessment, compliance auditing, and authorized penetration testing. This direction emphasizes end-to-end security lifecycle support, where discovery, analysis, validation, and reporting are integrated rather than fragmented across separate tools.


