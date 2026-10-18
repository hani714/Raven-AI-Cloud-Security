import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/ui/button';
import { Input } from '@/ui/input';
import { Label } from '@/ui/label';
import { useToast } from '@/hooks/use-toast';
import { authService } from '@/services/authService';
import { passwordResetSchema } from '@/lib/validation';
import { AuthLayout } from '@/components/auth/AuthLayout';

const ResetPassword = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const resetToken = (location.state as { resetToken?: string })?.resetToken;

  useEffect(() => {
    if (!resetToken) {
      navigate('/forgot-password');
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      passwordResetSchema.parse({ newPassword, confirmPassword });
    } catch (error: any) {
      const message = error.errors?.[0]?.message || 'Validation failed';
      toast({ title: 'Validation Error', description: message, variant: 'destructive' });
      return;
    }

    try {
      setLoading(true);
      await authService.resetPassword({ newPassword, resetToken: resetToken! });
      toast({ title: 'Password Reset', description: 'Your password has been reset successfully. Please sign in.' });
      navigate('/login');
    } catch (error: any) {
      toast({ title: 'Error', description: error.message || 'Failed to reset password', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const inputCls =
    'border-[#21262D] bg-[#161B22] font-mono text-sm text-[#E6EDF3] placeholder:text-[#7D8590] focus-visible:ring-[#E5173F] focus-visible:ring-offset-[#0D1117]';
  const labelCls = 'font-mono text-xs uppercase tracking-wider text-[#7D8590]';

  return (
    <AuthLayout
      title="Set New Password"
      subtitle="Enter your new password below. It must be at least 8 characters."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="newPassword" className={labelCls}>New Password</Label>
          <Input id="newPassword" type="password" placeholder="••••••••" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required className={inputCls} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="confirmPassword" className={labelCls}>Confirm New Password</Label>
          <Input id="confirmPassword" type="password" placeholder="••••••••" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required className={inputCls} />
        </div>
        <Button
          type="submit"
          disabled={loading}
          className="w-full bg-[#E5173F] font-mono text-sm uppercase tracking-widest text-white shadow-[0_0_24px_-4px_rgba(229,23,63,0.6)] hover:bg-[#FF2D55] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Resetting...' : 'Reset Password →'}
        </Button>
      </form>
    </AuthLayout>
  );
};

export default ResetPassword;
