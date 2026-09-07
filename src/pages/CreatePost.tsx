import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { useApp } from "@/context/AppContext";
import { OutputDisplay } from "@/components/OutputDisplay";
import { Sparkles } from "lucide-react";
import { toast } from "sonner";
import { generateLinkedinOutput } from "@/lib/localAgent";

const tones = [
  { value: "professional", label: "Professional" },
  { value: "founder", label: "Founder / Storytelling" },
  { value: "educational", label: "Educational" },
  { value: "inspirational", label: "Inspirational" },
  { value: "controversial", label: "Bold / Controversial" },
  { value: "casual", label: "Casual" },
];

const CreatePost = () => {
  const [topic, setTopic] = useState("");
  const [context, setContext] = useState("");
  const [tone, setTone] = useState("professional");
  const { profile, setOutput, isGenerating, setIsGenerating, output } = useApp();
  const navigate = useNavigate();

  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast.error("Please enter a topic");
      return;
    }
    if (!profile.name) {
      toast.error("Set up your profile first for personalized results");
      navigate("/profile");
      return;
    }

    setIsGenerating(true);
    try {
      const generated = await generateLinkedinOutput(profile, "manual", {
        topic,
        context,
        tone,
      });

      setOutput(generated);
      toast.success("Post template ready. Waiting for custom content...");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      toast.error(`Failed to generate post: ${message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Create Post from Idea</h1>
        <p className="text-muted-foreground text-sm mt-1">Enter your topic and let AI craft a LinkedIn-ready post.</p>
      </div>

      <Card className="p-6 space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Topic *</label>
          <Input
            placeholder="e.g. Why AI will replace 50% of marketing jobs"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Context (optional)</label>
          <Textarea
            placeholder="Add any specific details, data points, or personal experiences to include…"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            rows={4}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Tone</label>
          <Select value={tone} onValueChange={setTone}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {tones.map((t) => (
                <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Button onClick={handleGenerate} disabled={isGenerating} className="w-full gap-2">
          <Sparkles className="h-4 w-4" />
          {isGenerating ? "Generating…" : "Generate Post"}
        </Button>
      </Card>

      <OutputDisplay />
    </div>
  );
};

export default CreatePost;
