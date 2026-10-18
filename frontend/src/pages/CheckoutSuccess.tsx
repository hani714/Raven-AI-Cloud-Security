import { Link } from "react-router-dom";

const CheckoutSuccess = () => {
  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center px-6">
      <div className="w-full max-w-xl rounded-xl border border-border-landing/60 bg-card-landing/30 p-8">
        <h1 className="text-2xl font-semibold">Payment Successful</h1>
        <p className="mt-4 text-muted-foreground-landing">
          Your payment was completed. You can return to your dashboard and continue using the platform.
        </p>
        <div className="mt-6">
          <Link to="/dashboard" className="text-sm text-primary-landing hover:underline">
            Go to dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};

export default CheckoutSuccess;
