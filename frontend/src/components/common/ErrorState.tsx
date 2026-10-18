import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '@/ui/button';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  isRetrying?: boolean;
}

/**
 * ErrorState - Display expected errors (API failures, network issues)
 * Use this for handling errors from data fetching, not component crashes
 */
export const ErrorState = ({ 
  title = 'Something went wrong',
  message, 
  onRetry,
  isRetrying = false 
}: ErrorStateProps) => {
  return (
    <div className="flex min-h-[400px] items-center justify-center">
      <div className="text-center space-y-4 max-w-md">
        <AlertTriangle className="h-12 w-12 text-destructive mx-auto" />
        <div>
          <h3 className="text-xl font-semibold mb-2">{title}</h3>
          <p className="text-muted-foreground text-sm">{message}</p>
        </div>
        {onRetry && (
          <Button 
            onClick={onRetry} 
            disabled={isRetrying}
            variant="outline"
            className="gap-2"
          >
            {isRetrying ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                Retrying...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4" />
                Try Again
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
};
