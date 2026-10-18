import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/ui/button';
import { Input } from '@/ui/input';
import { Label } from '@/ui/label';
import { useToast } from '@/hooks/use-toast';
import { authService } from '@/services/authService';
import { registerSchema } from '@/lib/validation';
import { AuthLayout } from '@/components/auth/AuthLayout';

const Register = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      registerSchema.parse({ email, password, confirmPassword });
      setLoading(true);
      await authService.register({ email, password, confirmPassword });
      toast({ title: 'Success', description: 'Account created successfully! Please verify your email with the OTP.' });
      navigate('/verify-otp', { state: { email } });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create account';
      toast({ title: 'Error', description: errorMessage, variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const inputCls =
    'border-[#21262D] bg-[#161B22] font-mono text-sm text-[#E6EDF3] placeholder:text-[#7D8590] focus-visible:ring-[#E5173F] focus-visible:ring-offset-[#0D1117]';
  const labelCls = 'font-mono text-xs uppercase tracking-wider text-[#7D8590]';

  return (
    <AuthLayout
      title="Create Account"
      subtitle="Begin your security assessment"
      footer={
        <span>
          Already have an account?{' '}
          <Link to="/login" className="text-[#E5173F] hover:text-[#FF2D55] hover:underline">Sign in</Link>
        </span>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email" className={labelCls}>Email</Label>
          <Input id="email" type="email" placeholder="operator@raven.dev" value={email} onChange={(e) => setEmail(e.target.value)} required className={inputCls} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password" className={labelCls}>Password</Label>
          <Input id="password" type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required className={inputCls} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="confirmPassword" className={labelCls}>Confirm Password</Label>
          <Input id="confirmPassword" type="password" placeholder="••••••••" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required className={inputCls} />
        </div>
        <Button
          type="submit"
          disabled={loading}
          className="w-full bg-[#E5173F] font-mono text-sm uppercase tracking-widest text-white shadow-[0_0_24px_-4px_rgba(229,23,63,0.6)] hover:bg-[#FF2D55] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Creating account...' : 'Create Account →'}
        </Button>
      </form>
    </AuthLayout>
  );
};

export default Register;
