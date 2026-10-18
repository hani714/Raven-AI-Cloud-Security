import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Eye, EyeOff } from "lucide-react";
import { Button } from "@/ui/button";
import { Input } from "@/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/ui/select";
import type {
  ByokProvider,
  ByokProviderModelOption,
  ByokProviderOption,
  CreateByokKeyRequest,
} from "@/interfaces/byok";
import { useByokModels } from "@/hooks/useByok";

const schema = z.object({
  provider: z.string().min(1, "Provider is required"),
  model: z.string().trim().min(1, "Model is required"),
  apiKey: z.string().trim().min(1, "API key is required"),
  label: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface ByokFormProps {
  onSubmit: (data: CreateByokKeyRequest) => void;
  isCreating: boolean;
  providers: ByokProviderOption[];
}

export const ByokForm = ({ onSubmit, isCreating, providers }: ByokFormProps) => {
  const [showKey, setShowKey] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { provider: "", model: "", apiKey: "", label: "" },
  });

  const provider = form.watch("provider");
  const currentModel = form.watch("model");
  const { data: models = [], isLoading: isModelsLoading } = useByokModels(provider);

  useEffect(() => {
    if (providers.length === 0) return;
    const current = providers.find((p) => p.value === provider);
    if (!current) {
      form.setValue("provider", providers[0].value);
    }
  }, [providers, provider, form]);

  useEffect(() => {
    if (!provider || isModelsLoading) return;
    if (models.length === 0) {
      if (currentModel) form.setValue("model", "");
      return;
    }

    const defaultModel =
      models.find((m: ByokProviderModelOption) => m.isDefault)?.value ?? models[0].value;
    const hasCurrent = models.some((m) => m.value === currentModel);
    if (!currentModel || !hasCurrent) {
      form.setValue("model", defaultModel);
    }
  }, [provider, models, isModelsLoading, currentModel, form]);

  const handleSubmit = (values: FormValues) => {
    onSubmit({
      provider: values.provider as ByokProvider,
      model: values.model,
      apiKey: values.apiKey,
      label: values.label || undefined,
    });
    form.reset({ provider: values.provider, model: values.model, apiKey: "", label: "" });
    setShowKey(false);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <FormField
            control={form.control}
            name="provider"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Provider</FormLabel>
                <Select value={field.value} onValueChange={field.onChange} disabled={providers.length === 0}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder={providers.length === 0 ? "Loading providers..." : "Select provider"} />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {providers.length > 0 ? (
                      providers.map((p) => (
                        <SelectItem key={p.value} value={p.value}>
                          {p.label}
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="__loading" disabled>
                        Loading providers...
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="model"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Model</FormLabel>
                <Select
                  value={field.value}
                  onValueChange={field.onChange}
                  disabled={!provider || isModelsLoading || models.length === 0}
                >
                  <FormControl>
                    <SelectTrigger className="font-mono">
                      <SelectValue
                        placeholder={
                          !provider
                            ? "Select provider first"
                            : isModelsLoading
                              ? "Loading models..."
                              : models.length === 0
                                ? "No models available"
                                : "Select model"
                        }
                      />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {isModelsLoading ? (
                      <SelectItem value="__loading" disabled>
                        Loading models...
                      </SelectItem>
                    ) : models.length > 0 ? (
                      models.map((m) => (
                        <SelectItem key={m.value} value={m.value}>
                          {m.value}
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="__empty" disabled>
                        No models available
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="apiKey"
          render={({ field }) => (
            <FormItem>
              <FormLabel>API Key</FormLabel>
              <FormControl>
                <div className="relative">
                  <Input
                    type={showKey ? "text" : "password"}
                    placeholder="sk-..."
                    className="font-mono pr-10"
                    autoComplete="off"
                    {...field}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => setShowKey((s) => !s)}
                    className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 text-muted-foreground hover:text-primary hover:bg-primary/10"
                  >
                    {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="label"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Label (optional)</FormLabel>
              <FormControl>
                <Input placeholder="e.g. Production OpenAI" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-end">
          <Button type="submit" disabled={isCreating || providers.length === 0 || isModelsLoading || models.length === 0}>
            {isCreating ? "Saving..." : "Save Key"}
          </Button>
        </div>
      </form>
    </Form>
  );
};
