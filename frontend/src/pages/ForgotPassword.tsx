import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/ui/button';
import { Input } from '@/ui/input';
import { Label } from '@/ui/label';
import { useToast } from '@/hooks/use-toast';
import { authService } from '@/services/authService';
import { AuthLayout } from '@/components/auth/AuthLayout';

const ForgotPassword = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      await authService.sendOtp({ email });
      toast({ title: 'OTP Sent', description: `A password reset code has been sent to ${email}` });
      navigate('/verify-reset-otp', { state: { email } });
    } catch (error: any) {
      toast({ title: 'Error', description: error.message || 'Failed to send reset code', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Forgot Password"
      subtitle="Enter your email and we'll send you a verification code."
      footer={
        <span>
          Remember your password?{' '}
          <Link to="/login" className="text-[#E5173F] hover:text-[#FF2D55] hover:underline">Sign in</Link>
        </span>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email" className="font-mono text-xs uppercase tracking-wider text-[#7D8590]">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="operator@raven.dev"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="border-[#21262D] bg-[#161B22] font-mono text-sm text-[#E6EDF3] placeholder:text-[#7D8590] focus-visible:ring-[#E5173F] focus-visible:ring-offset-[#0D1117]"
          />
        </div>
        <Button
          type="submit"
          disabled={loading}
          className="w-full bg-[#E5173F] font-mono text-sm uppercase tracking-widest text-white shadow-[0_0_24px_-4px_rgba(229,23,63,0.6)] hover:bg-[#FF2D55] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Sending code...' : 'Send Reset Code →'}
        </Button>
      </form>
    </AuthLayout>
  );
};

export default ForgotPassword;
