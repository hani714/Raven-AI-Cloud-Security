import { useState } from "react";
import { Card } from "@/ui/card";
import { useEnvironments } from "@/hooks/useEnvironments";
import { PageHeader } from "@/components/common/PageHeader";
import { LoadingState } from "@/components/common/LoadingState";
import { CredentialsTable } from "@/components/environments/CredentialsTable";
import { AddCredentialDialog } from "@/components/environments/AddCredentialDialog";
import { DeleteCredentialDialog } from "@/components/environments/DeleteCredentialDialog";
import { CredentialsActions } from "@/components/environments/CredentialsActions";
import type { CreateCredentialRequest } from "@/interfaces/environment";

const Environments = () => {
  const {
    credentials,
    isLoading,
    createCredential,
    deleteCredential,
    importCredentials,
    testCredential,
    isCreating,
    testingId,
  } = useEnvironments();

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const handleAddCredential = (data: CreateCredentialRequest) => {
    createCredential(data);
    setIsAddDialogOpen(false);
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) importCredentials(file);
  };

  const handleDeleteConfirm = () => {
    if (deleteId) {
      deleteCredential(deleteId);
      setDeleteId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <LoadingState message="Loading environments..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="w-full py-8 px-6 lg:px-8">
        <PageHeader
          label="aws_credentials"
          title="AWS Environments"
          description="Manage your AWS IAM credentials and access keys securely"
        />

        <CredentialsActions
          onAdd={() => setIsAddDialogOpen(true)}
          onImport={handleImport}
        />

        <Card className="glass-card">
          <div className="p-6">
            <h2 className="font-display text-xl font-semibold mb-4">Stored Credentials</h2>
            <CredentialsTable
              credentials={credentials || []}
              onDelete={(id) => setDeleteId(id)}
              onTest={testCredential}
              testingId={testingId}
            />
          </div>
        </Card>

        <AddCredentialDialog
          open={isAddDialogOpen}
          onOpenChange={setIsAddDialogOpen}
          onSubmit={handleAddCredential}
          isCreating={isCreating}
        />

        <DeleteCredentialDialog
          open={!!deleteId}
          onOpenChange={(open) => !open && setDeleteId(null)}
          onConfirm={handleDeleteConfirm}
        />
      </div>
    </div>
  );
};

export default Environments;
