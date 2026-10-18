import type { ReactNode } from "react";
import { Link } from "react-router-dom";

import Navbar from "@/components/landing/Navbar";
import Footer from "@/components/landing/Footer";

interface PolicyPageLayoutProps {
  title: string;
  lastUpdated: string;
  children: ReactNode;
}

const PolicyPageLayout = ({ title, lastUpdated, children }: PolicyPageLayoutProps) => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="pt-28 pb-16">
        <div className="container mx-auto px-6 max-w-4xl">
          <div className="mb-8">
            <p className="text-xs uppercase tracking-[0.16em] text-primary-landing">Legal</p>
            <h1 className="mt-2 text-3xl md:text-4xl font-semibold text-foreground">{title}</h1>
            <p className="mt-3 text-sm text-muted-foreground-landing">Last updated: {lastUpdated}</p>
          </div>

          <article className="space-y-8 text-sm md:text-base leading-7 text-muted-foreground-landing">
            {children}
          </article>

          <div className="mt-10 rounded-lg border border-border-landing/60 bg-card-landing/30 p-4 text-sm text-muted-foreground-landing">
            Questions about these policies? Contact us at
            <a className="ml-1 text-primary-landing hover:underline" href="mailto:privacy@ravensecurity.app">
              privacy@ravensecurity.app
            </a>
            .
          </div>

          <div className="mt-8 flex flex-wrap items-center gap-4 text-sm">
            <Link className="text-primary-landing hover:underline" to="/terms-of-service">
              Terms of Service
            </Link>
            <Link className="text-primary-landing hover:underline" to="/privacy-policy">
              Privacy Policy
            </Link>
            <Link className="text-primary-landing hover:underline" to="/refund-policy">
              Refund Policy
            </Link>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default PolicyPageLayout;
