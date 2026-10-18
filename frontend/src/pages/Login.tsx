import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/ui/button';
import { Input } from '@/ui/input';
import { Label } from '@/ui/label';
import { useToast } from '@/hooks/use-toast';
import { authService } from '@/services/authService';
import { authSchema } from '@/lib/validation';
import { AuthLayout } from '@/components/auth/AuthLayout';

const Login = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      authSchema.parse({ email, password });
      setLoading(true);
      await authService.login({ email, password });
      toast({ title: 'Success', description: 'Logged in successfully!' });
      navigate('/dashboard');
    } catch (error: any) {
      toast({ title: 'Error', description: error.message || 'Failed to sign in', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Welcome Back"
      subtitle="Sign in to your Raven account"
      footer={
        <div className="flex items-center justify-between">
          <span>
            Don't have an account?{' '}
            <Link to="/register" className="text-[#E5173F] hover:text-[#FF2D55] hover:underline">Sign up</Link>
          </span>
          <Link to="/forgot-password" className="text-[#E5173F] hover:text-[#FF2D55] hover:underline">Forgot?</Link>
        </div>
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
        <div className="space-y-2">
          <Label htmlFor="password" className="font-mono text-xs uppercase tracking-wider text-[#7D8590]">Password</Label>
          <Input
            id="password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="border-[#21262D] bg-[#161B22] font-mono text-sm text-[#E6EDF3] placeholder:text-[#7D8590] focus-visible:ring-[#E5173F] focus-visible:ring-offset-[#0D1117]"
          />
        </div>
        <Button
          type="submit"
          disabled={loading}
          className="group relative w-full overflow-hidden bg-[#E5173F] font-mono text-sm uppercase tracking-widest text-white shadow-[0_0_24px_-4px_rgba(229,23,63,0.6)] hover:bg-[#FF2D55] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Authenticating...' : 'Sign In →'}
        </Button>
      </form>
    </AuthLayout>
  );
};

export default Login;
