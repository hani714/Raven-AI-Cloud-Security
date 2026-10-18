import PolicyPageLayout from "@/components/legal/PolicyPageLayout";

const TermsOfService = () => {
  return (
    <PolicyPageLayout title="Terms of Service" lastUpdated="March 29, 2026">
      <section>
        <h2 className="text-xl font-semibold text-foreground">1. Agreement and Scope</h2>
        <p className="mt-3">
          These Terms govern use of the RAVEN cloud security platform, including account access, AWS environment
          onboarding, security scans, risk analysis, and related reports. By using the Service, you agree to these
          Terms.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">2. Service Description</h2>
        <p className="mt-3">
          RAVEN provides automated AWS security assessment features, including IAM, S3, and Lambda enumeration,
          vulnerability analysis, and AI-assisted remediation guidance. You are responsible for ensuring you are
          authorized to test all cloud assets connected to your account.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">3. Account and Security Responsibilities</h2>
        <p className="mt-3">You agree to:</p>
        <ul className="mt-2 list-disc pl-6 space-y-2">
          <li>Provide accurate registration information and maintain account security.</li>
          <li>Use strong credentials and protect access tokens and API credentials.</li>
          <li>Promptly notify us of unauthorized access or suspected compromise.</li>
        </ul>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">4. Data Handling and Security</h2>
        <p className="mt-3">
          Our security program is designed using risk-based controls aligned with NIST Cybersecurity Framework
          practices and ISO/IEC 27001 and 27701 principles. Controls include encryption in transit, encryption at
          rest for sensitive secrets, role-based access restrictions, audit logging, and incident response procedures.
          This statement does not represent a certification claim unless explicitly stated in a separate agreement.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">5. Billing and Subscriptions</h2>
        <p className="mt-3">
          Paid subscriptions are processed by Paddle as merchant of record. Subscription terms, taxes, and invoicing
          are handled during checkout. Plan limits such as number of environments and scan volume may apply.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">6. Acceptable Use</h2>
        <p className="mt-3">You must not use the Service to:</p>
        <ul className="mt-2 list-disc pl-6 space-y-2">
          <li>Perform scans on infrastructure you do not own or have explicit permission to assess.</li>
          <li>Violate law, contract, or third-party rights.</li>
          <li>Attempt to disrupt, abuse, or reverse engineer the platform.</li>
        </ul>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">7. Availability and Changes</h2>
        <p className="mt-3">
          We may improve, modify, or discontinue features from time to time. We aim for reliable operation but do not
          guarantee uninterrupted availability.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">8. Limitation of Liability</h2>
        <p className="mt-3">
          To the maximum extent permitted by law, the Service is provided on an as-available basis, and we are not
          liable for indirect, incidental, special, consequential, or punitive damages arising from use of the Service.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">9. Termination</h2>
        <p className="mt-3">
          You may cancel your subscription at any time. We may suspend or terminate accounts that violate these Terms
          or create security or legal risk.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">10. Related Policies</h2>
        <p className="mt-3">
          Your use of the Service is also subject to our Privacy Policy and Refund Policy.
        </p>
      </section>
    </PolicyPageLayout>
  );
};

export default TermsOfService;
