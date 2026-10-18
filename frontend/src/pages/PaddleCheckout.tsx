import { initializePaddle } from "@paddle/paddle-js";
import { useEffect, useMemo, useState } from "react";
import { Link, useLocation } from "react-router-dom";

type CheckoutState = "loading" | "opened" | "error";

const HARDCODED_PADDLE_CLIENT_TOKEN = "test_eba79469ff7451d7681e585594d";
const PADDLE_ENV: "sandbox" | "production" = "sandbox";

const PaddleCheckout = () => {
  const location = useLocation();
  const [state, setState] = useState<CheckoutState>("loading");
  const [error, setError] = useState<string | null>(null);

  const transactionId = useMemo(() => {
    const params = new URLSearchParams(location.search);
    return params.get("_ptxn");
  }, [location.search]);

  useEffect(() => {
    let cancelled = false;

    const openCheckout = async () => {
      if (!transactionId) {
        setState("error");
        setError("Missing transaction id in URL (_ptxn). Please create a new transaction.");
        return;
      }

      const token = HARDCODED_PADDLE_CLIENT_TOKEN;
      const environment = PADDLE_ENV;

      try {
        const paddle = await initializePaddle({
          environment,
          token,
        });

        if (!paddle) {
          throw new Error("Paddle initialization returned empty client");
        }

        paddle.Checkout.open({
          transactionId,
        });

        if (!cancelled) {
          setState("opened");
        }
      } catch (err) {
        if (!cancelled) {
          setState("error");
          setError(err instanceof Error ? err.message : "Failed to open Paddle checkout");
        }
      }
    };

    void openCheckout();

    return () => {
      cancelled = true;
    };
  }, [transactionId]);

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center px-6">
      <div className="w-full max-w-xl rounded-xl border border-border-landing/60 bg-card-landing/30 p-8">
        <h1 className="text-2xl font-semibold">Checkout</h1>

        {state === "loading" && (
          <p className="mt-4 text-muted-foreground-landing">Preparing secure checkout...</p>
        )}

        {state === "opened" && (
          <p className="mt-4 text-muted-foreground-landing">
            Checkout launched. If no popup appears, allow popups and refresh this page.
          </p>
        )}

        {state === "error" && (
          <div className="mt-4 space-y-2">
            <p className="text-red-400">Unable to open checkout.</p>
            <p className="text-sm text-muted-foreground-landing">{error}</p>
          </div>
        )}

        <div className="mt-6">
          <Link to="/" className="text-sm text-primary-landing hover:underline">
            Back to home
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PaddleCheckout;
