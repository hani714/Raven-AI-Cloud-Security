import PolicyPageLayout from "@/components/legal/PolicyPageLayout";

const PrivacyPolicy = () => {
  return (
    <PolicyPageLayout title="Privacy Policy" lastUpdated="March 29, 2026">
      <section>
        <h2 className="text-xl font-semibold text-foreground">1. Overview</h2>
        <p className="mt-3">
          This Privacy Policy explains how RAVEN collects, uses, stores, and protects personal and account-related data
          when you use our cloud security platform.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">2. Data We Collect</h2>
        <ul className="mt-3 list-disc pl-6 space-y-2">
          <li>Account data: email address, authentication records, and account verification metadata.</li>
          <li>Subscription and billing data: billing events and transaction metadata from Paddle.</li>
          <li>AWS environment data: environment names, regions, encrypted credential material, and scan metadata.</li>
          <li>Security scan output: IAM, S3, Lambda, and related configuration findings tied to your account.</li>
          <li>Operational telemetry: request logs, audit traces, and service diagnostics.</li>
        </ul>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">3. How We Use Data</h2>
        <ul className="mt-3 list-disc pl-6 space-y-2">
          <li>Provide authentication, account management, and subscription services.</li>
          <li>Run security scans and generate analysis, findings, and remediation guidance.</li>
          <li>Maintain platform reliability, detect abuse, and investigate incidents.</li>
          <li>Meet legal, tax, accounting, and compliance obligations.</li>
        </ul>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">4. Security Safeguards</h2>
        <p className="mt-3">
          Our data protection controls are designed using risk-based practices aligned with NIST CSF and ISO/IEC 27001
          and 27701 principles. These controls include least-privilege access, encryption in transit, encryption at
          rest for sensitive data, secure credential handling, centralized logging, and incident response workflows.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">5. Data Sharing</h2>
        <p className="mt-3">We share data only when required to operate the Service:</p>
        <ul className="mt-2 list-disc pl-6 space-y-2">
          <li>Paddle for payment processing and merchant-of-record services.</li>
          <li>Infrastructure and communication providers under contractual confidentiality obligations.</li>
          <li>Authorities when disclosure is required by law.</li>
        </ul>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">6. Data Retention</h2>
        <p className="mt-3">
          We retain data only for as long as needed for service delivery, security operations, dispute resolution,
          legal obligations, and legitimate business purposes. We delete or anonymize data when no longer required.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">7. Your Rights</h2>
        <p className="mt-3">Subject to applicable law, you may request access, correction, deletion, or export of your personal data.</p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">8. International Processing</h2>
        <p className="mt-3">
          Data may be processed in multiple jurisdictions where our providers operate. We apply contractual and
          technical safeguards for cross-border data handling.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">9. Policy Updates</h2>
        <p className="mt-3">
          We may update this policy to reflect legal, operational, or security changes. Material updates will be
          posted on this page with a revised date.
        </p>
      </section>
    </PolicyPageLayout>
  );
};

export default PrivacyPolicy;
