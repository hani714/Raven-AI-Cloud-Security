import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

/**
 * LoadingState - Raven-themed loading indicator.
 */
export const LoadingState = ({ message = 'Loading...' }: LoadingStateProps) => {
  return (
    <div className="flex min-h-[400px] items-center justify-center">
      <div className="text-center space-y-4">
        <div className="relative mx-auto h-12 w-12">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
          <div className="absolute inset-0 rounded-full bg-primary/10 blur-xl" />
        </div>
        <p className="font-mono text-xs uppercase tracking-[0.25em] text-muted-foreground">
          {message}
        </p>
      </div>
    </div>
  );
};
