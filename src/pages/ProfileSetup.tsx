import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { useApp } from "@/context/AppContext";
import { Save, User } from "lucide-react";
import { toast } from "sonner";

const toneOptions = [
  { value: "professional", label: "Professional" },
  { value: "founder", label: "Founder / Storytelling" },
  { value: "educational", label: "Educational" },
  { value: "inspirational", label: "Inspirational" },
  { value: "casual", label: "Casual" },
];

const ProfileSetup = () => {
  const { profile, setProfile } = useApp();
  const [form, setForm] = useState(profile);

  const handleSave = () => {
    if (!form.name.trim()) {
      toast.error("Name is required");
      return;
    }
    setProfile(form);
    toast.success("Profile saved! Your AI identity is ready.");
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Your AI Profile</h1>
        <p className="text-muted-foreground text-sm mt-1">This is your AI identity brain. The more detail you provide, the better your posts will match your voice.</p>
      </div>

      <Card className="p-6 space-y-5">
        <div className="h-16 w-16 rounded-2xl bg-accent flex items-center justify-center">
          <User className="h-7 w-7 text-accent-foreground" />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Name *</label>
          <Input
            placeholder="Your name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Bio / Headline</label>
          <Textarea
            placeholder="e.g. Founder @ TechCo | Building AI tools for creators | Ex-Google"
            value={form.bio}
            onChange={(e) => setForm({ ...form, bio: e.target.value })}
            rows={2}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Skills / Expertise</label>
          <Input
            placeholder="e.g. AI, Startups, Product Management, Growth"
            value={form.skills}
            onChange={(e) => setForm({ ...form, skills: e.target.value })}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Default Writing Tone</label>
          <Select value={form.tone} onValueChange={(v) => setForm({ ...form, tone: v })}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {toneOptions.map((t) => (
                <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Past Posts (optional)</label>
          <Textarea
            placeholder="Paste 2-3 of your best LinkedIn posts here so the AI can learn your style…"
            value={form.pastPosts}
            onChange={(e) => setForm({ ...form, pastPosts: e.target.value })}
            rows={5}
          />
          <p className="text-xs text-muted-foreground">This helps the AI match your unique writing style.</p>
        </div>

        <Button onClick={handleSave} className="w-full gap-2">
          <Save className="h-4 w-4" />
          Save Profile
        </Button>
      </Card>
    </div>
  );
};

export default ProfileSetup;
