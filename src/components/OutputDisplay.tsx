import { useApp } from "@/context/AppContext";
import { Copy, RefreshCw, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useState } from "react";
import { toast } from "sonner";

export const OutputDisplay = () => {
  const { output, isGenerating } = useApp();
  const [copied, setCopied] = useState<string | null>(null);

  if (isGenerating) {
    return (
      <div className="space-y-4 animate-fade-in">
        <div className="text-center py-16 space-y-3">
          <div className="h-10 w-10 mx-auto rounded-full gradient-primary animate-pulse-soft" />
          <p className="text-muted-foreground font-medium">Generating high-performing post…</p>
          <p className="text-sm text-muted-foreground">Analyzing content & crafting your post</p>
        </div>
      </div>
    );
  }

  if (!output) return null;

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopied(label);
    toast.success(`${label} copied!`);
    setTimeout(() => setCopied(null), 2000);
  };

  const CopyBtn = ({ text, label }: { text: string; label: string }) => (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => copyToClipboard(text, label)}
      className="h-8 gap-1.5 text-muted-foreground hover:text-foreground"
    >
      {copied === label ? <Check className="h-3.5 w-3.5 text-success" /> : <Copy className="h-3.5 w-3.5" />}
      <span className="text-xs">Copy</span>
    </Button>
  );

  const copyAll = () => {
    const full = `${output.hooks.join("\n\n")}\n\n${output.post}\n\n${output.hashtags.join(" ")}`;
    copyToClipboard(full, "All");
  };

  return (
    <div className="space-y-4 animate-slide-up">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-foreground">Your Generated Post</h2>
        <Button onClick={copyAll} size="sm" className="gap-1.5">
          <Copy className="h-3.5 w-3.5" />
          Copy All
        </Button>
      </div>

      {/* Hooks */}
      <Card className="p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-foreground">🔥 Hooks</h3>
          <CopyBtn text={output.hooks.join("\n\n")} label="Hooks" />
        </div>
        <div className="space-y-2">
          {output.hooks.map((hook, i) => (
            <p key={i} className="text-sm text-foreground bg-accent/50 rounded-lg p-3 font-medium">{hook}</p>
          ))}
        </div>
      </Card>

      {/* Post */}
      <Card className="p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-foreground">🧠 Post</h3>
          <CopyBtn text={output.post} label="Post" />
        </div>
        <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">{output.post}</p>
      </Card>

      {/* Hashtags */}
      <Card className="p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-foreground">🏷️ Hashtags</h3>
          <CopyBtn text={output.hashtags.join(" ")} label="Hashtags" />
        </div>
        <div className="flex flex-wrap gap-2">
          {output.hashtags.map((tag, i) => (
            <button
              key={i}
              onClick={() => copyToClipboard(tag, tag)}
              className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium hover:bg-primary/20 transition-colors"
            >
              {tag}
            </button>
          ))}
        </div>
      </Card>

      {/* Image Prompt */}
      <Card className="p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-foreground">🎨 Image Prompt</h3>
          <CopyBtn text={output.imagePrompt} label="Image Prompt" />
        </div>
        <p className="text-sm text-muted-foreground italic">{output.imagePrompt}</p>
      </Card>
    </div>
  );
};
