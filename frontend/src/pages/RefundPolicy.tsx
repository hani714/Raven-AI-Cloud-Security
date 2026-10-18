import PolicyPageLayout from "@/components/legal/PolicyPageLayout";

const RefundPolicy = () => {
  return (
    <PolicyPageLayout title="Refund Policy" lastUpdated="March 29, 2026">
      <section>
        <h2 className="text-xl font-semibold text-foreground">1. Overview</h2>
        <p className="mt-3">
          This Refund Policy applies to subscriptions purchased for RAVEN through Paddle, our merchant of record.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">2. Eligibility</h2>
        <ul className="mt-3 list-disc pl-6 space-y-2">
          <li>First-time subscription purchases are eligible for a refund request within 14 days of payment.</li>
          <li>Renewal charges are generally non-refundable once the renewal period begins.</li>
          <li>Duplicate or incorrect charges are eligible for full refund review.</li>
        </ul>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">3. How to Request a Refund</h2>
        <p className="mt-3">
          Submit your request with account email, order reference, and reason for refund to
          <a className="ml-1 text-primary-landing hover:underline" href="mailto:billing@ravensecurity.app">
            billing@ravensecurity.app
          </a>
          .
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">4. Processing Time</h2>
        <p className="mt-3">
          Approved refunds are processed back to the original payment method. Timing depends on payment method and
          banking provider.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">5. Cancellation</h2>
        <p className="mt-3">
          You can cancel your subscription at any time. Cancellation stops future renewals and takes effect at the end
          of the current billing period unless required otherwise by applicable law.
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-foreground">6. Statutory Rights</h2>
        <p className="mt-3">
          This policy does not limit non-waivable consumer rights that apply under local law.
        </p>
      </section>
    </PolicyPageLayout>
  );
};

export default RefundPolicy;
