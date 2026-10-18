import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/ui/button';
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@/ui/input-otp';
import { useToast } from '@/hooks/use-toast';
import { authService } from '@/services/authService';
import { AuthLayout } from '@/components/auth/AuthLayout';

const ResetOtpVerify = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [otp, setOtp] = useState('');

  const email = (location.state as { email?: string })?.email;

  useEffect(() => {
    if (!email) {
      navigate('/forgot-password');
    }
  }, []);

  const handleResend = async () => {
    if (!email) return;
    try {
      setSending(true);
      await authService.sendOtp({ email });
      toast({ title: 'OTP Sent', description: `A new code has been sent to ${email}` });
    } catch (error: any) {
      toast({ title: 'Error', description: error.message || 'Failed to resend code', variant: 'destructive' });
    } finally {
      setSending(false);
    }
  };

  const handleVerify = async () => {
    if (!email || otp.length !== 6) return;
    try {
      setLoading(true);
      const { access_token } = await authService.verifyResetOtp({ email, code: otp });
      toast({ title: 'Verified', description: 'OTP verified. Please set your new password.' });
      navigate('/reset-password', { state: { resetToken: access_token } });
    } catch (error: any) {
      toast({ title: 'Error', description: error.message || 'OTP verification failed', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Enter Reset Code"
      subtitle={
        <>
          Enter the 6-digit code sent to{' '}
          <span className="font-mono text-[#E6EDF3]">{email}</span>
        </>
      }
      footer={
        <span>
          Didn't receive a code?{' '}
          <button
            type="button"
            className="text-[#E5173F] hover:text-[#FF2D55] hover:underline disabled:opacity-50"
            onClick={handleResend}
            disabled={sending}
          >
            {sending ? 'Sending...' : 'Resend Code'}
          </button>
        </span>
      }
    >
      <div className="space-y-6">
        <div className="flex justify-center [&_input]:border-[#21262D] [&_input]:bg-[#161B22] [&_input]:font-mono [&_input]:text-[#E6EDF3] [&_input]:focus-visible:ring-[#E5173F]">
          <InputOTP maxLength={6} value={otp} onChange={setOtp}>
            <InputOTPGroup>
              <InputOTPSlot index={0} />
              <InputOTPSlot index={1} />
              <InputOTPSlot index={2} />
              <InputOTPSlot index={3} />
              <InputOTPSlot index={4} />
              <InputOTPSlot index={5} />
            </InputOTPGroup>
          </InputOTP>
        </div>
        <Button
          className="w-full bg-[#E5173F] font-mono text-sm uppercase tracking-widest text-white shadow-[0_0_24px_-4px_rgba(229,23,63,0.6)] hover:bg-[#FF2D55] disabled:cursor-not-allowed disabled:opacity-60"
          disabled={loading || otp.length !== 6}
          onClick={handleVerify}
        >
          {loading ? 'Verifying...' : 'Verify Code →'}
        </Button>
      </div>
    </AuthLayout>
  );
};

export default ResetOtpVerify;
