import { FormEvent, useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { CompetitorCreate } from "@/api/client";

interface CompetitorFormProps {
  isSubmitting: boolean;
  onSubmit: (payload: CompetitorCreate) => void;
}

export function CompetitorForm({ isSubmitting, onSubmit }: CompetitorFormProps) {
  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [description, setDescription] = useState("");
  const [keywords, setKeywords] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit({
      name,
      industry,
      description,
      keywords: keywords
        .split(",")
        .map((keyword) => keyword.trim())
        .filter(Boolean),
      enabled: true,
    });
    setName("");
    setIndustry("");
    setDescription("");
    setKeywords("");
  }

  return (
    <form className="grid gap-3 md:grid-cols-[1fr_1fr_1.4fr_1fr_auto]" onSubmit={handleSubmit}>
      <Input required placeholder="竞品名称" value={name} onChange={(event) => setName(event.target.value)} />
      <Input required placeholder="行业" value={industry} onChange={(event) => setIndustry(event.target.value)} />
      <Input
        placeholder="描述"
        value={description}
        onChange={(event) => setDescription(event.target.value)}
      />
      <Input placeholder="关键词，用逗号分隔" value={keywords} onChange={(event) => setKeywords(event.target.value)} />
      <Button type="submit" disabled={isSubmitting}>
        <Plus className="h-4 w-4" />
        添加
      </Button>
    </form>
  );
}
