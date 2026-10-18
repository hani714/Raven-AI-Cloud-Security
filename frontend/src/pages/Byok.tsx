import { useState } from "react";
import { Card } from "@/ui/card";
import { PageHeader } from "@/components/common/PageHeader";
import { LoadingState } from "@/components/common/LoadingState";
import { useByok } from "@/hooks/useByok";
import { ByokForm } from "@/components/byok/ByokForm";
import { ByokKeysTable } from "@/components/byok/ByokKeysTable";
import { DeleteByokDialog } from "@/components/byok/DeleteByokDialog";

const Byok = () => {
  const { keys, providers, isLoading, isProvidersLoading, createKey, deleteKey, isCreating } = useByok();
  const [deleteId, setDeleteId] = useState<string | null>(null);

  if (isLoading || isProvidersLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <LoadingState message="Loading BYOK data..." />
      </div>
    );
  }

  const handleConfirmDelete = () => {
    if (deleteId) {
      deleteKey(deleteId);
      setDeleteId(null);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="w-full py-8 px-6 lg:px-8">
        <PageHeader
          label="byok"
          title="Bring Your Own Key"
          description="Manage API keys for external model providers."
        />

        <Card className="glass-card mb-6">
          <div className="p-6">
            <h2 className="font-display text-xl font-semibold mb-4">Add a new key</h2>
            <ByokForm onSubmit={createKey} isCreating={isCreating} providers={providers} />
          </div>
        </Card>

        <Card className="glass-card">
          <div className="p-6">
            <h2 className="font-display text-xl font-semibold mb-4">Saved Keys</h2>
            <ByokKeysTable keys={keys || []} onDelete={(id) => setDeleteId(id)} providers={providers} />
          </div>
        </Card>

        <DeleteByokDialog
          open={!!deleteId}
          onOpenChange={(o) => !o && setDeleteId(null)}
          onConfirm={handleConfirmDelete}
        />
      </div>
    </div>
  );
};

export default Byok;