import { Button } from "@/ui/button";
import { Input } from "@/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/ui/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import type { CreateCredentialRequest } from "@/interfaces/environment";

const credentialFormSchema = z.object({
  name: z.string().min(1, "Name is required").max(100),
  accessKey: z.string().min(16, "Access key must be at least 16 characters"),
  secretAccessKey: z.string().min(32, "Secret key must be at least 32 characters"),
  region: z.string().optional(),
});

interface AddCredentialDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: CreateCredentialRequest) => void;
  isCreating: boolean;
}

export const AddCredentialDialog = ({
  open,
  onOpenChange,
  onSubmit,
  isCreating,
}: AddCredentialDialogProps) => {
  const form = useForm<CreateCredentialRequest>({
    resolver: zodResolver(credentialFormSchema),
    defaultValues: {
      name: "",
      accessKey: "",
      secretAccessKey: "",
      region: "us-east-1",
    },
  });

  const handleSubmit = (data: CreateCredentialRequest) => {
    onSubmit(data);
    form.reset();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] glass-card">
        <DialogHeader>
          <DialogTitle>Add AWS Credentials</DialogTitle>
          <DialogDescription>
            Enter your AWS IAM access key and secret key
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Environment Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Production Environment" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="accessKey"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Access Key ID</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="AKIAIOSFODNN7EXAMPLE"
                      className="font-mono"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="secretAccessKey"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Secret Access Key</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCY..."
                      className="font-mono"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="region"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Default Region (Optional)</FormLabel>
                  <FormControl>
                    <Input placeholder="us-east-1" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isCreating}>
                {isCreating ? "Adding..." : "Add Credentials"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};
