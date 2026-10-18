import { Toaster } from "@/ui/toaster";
import { TooltipProvider } from "@/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/context/theme-provider";
import DashboardLayout from "@/layout/DashboardLayout";

import {
  Login,
  Register,
  VerifyOtp,
  Dashboard,
  Environments,
  Scans,
  NotFound,
  Landing,
  ForgotPassword,
  ResetOtpVerify,
  ResetPassword,
  PaddleCheckout,
  CheckoutSuccess,
  TermsOfService,
  PrivacyPolicy,
  RefundPolicy,
  Subscriptions,
  Byok,
} from "./pages";
import ScanDetails from "@/components/scans/ScanDetails";
import AnalysisDetails from "@/components/scans/AnalysisDetails";

import { ErrorBoundary, ProtectedRoute } from './components';

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
      <TooltipProvider>
        <Toaster />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/verify-otp" element={<VerifyOtp />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/verify-reset-otp" element={<ResetOtpVerify />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/checkout" element={<PaddleCheckout />} />
            <Route path="/checkout/success" element={<CheckoutSuccess />} />
            <Route path="/terms-of-service" element={<TermsOfService />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/refund-policy" element={<RefundPolicy />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <ErrorBoundary>
                      <Routes>
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/environments" element={<Environments />} />
                        <Route path="/scans" element={<Scans />} />
                        <Route path="/scans/:scanId" element={<ScanDetails />} />
                        <Route path="/scans/:scanId/analysis" element={<AnalysisDetails />} />
                        <Route path="/subscriptions" element={<Subscriptions />} />
                        <Route path="/byok" element={<Byok />} />
                        <Route path="*" element={<NotFound />} />
                      </Routes>
                    </ErrorBoundary>
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
