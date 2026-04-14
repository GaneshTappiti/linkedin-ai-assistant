import { Link } from "react-router-dom";
import { PenTool, Globe, User, ArrowRight, Sparkles } from "lucide-react";
import { Card } from "@/components/ui/card";
import { useApp } from "@/context/AppContext";
import { OutputDisplay } from "@/components/OutputDisplay";

const Dashboard = () => {
  const { profile, output } = useApp();
  const hasProfile = profile.name.length > 0;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl md:text-4xl font-extrabold text-foreground">
          LinkedIn AI Agent
        </h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          Generate high-performing LinkedIn posts from ideas or URLs. Powered by AI, personalized to your voice.
        </p>
      </div>

      {!hasProfile && (
        <Card className="p-5 border-primary/30 bg-accent/30">
          <div className="flex items-start gap-3">
            <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
              <User className="h-4 w-4 text-primary" />
            </div>
            <div className="space-y-1">
              <p className="font-semibold text-foreground">Set up your profile first</p>
              <p className="text-sm text-muted-foreground">Your profile helps the AI match your voice and expertise.</p>
              <Link to="/profile" className="text-sm text-primary font-medium inline-flex items-center gap-1 mt-1 hover:underline">
                Set up profile <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </div>
        </Card>
      )}

      {/* Action Cards */}
      <div className="grid md:grid-cols-2 gap-4">
        <Link to="/create">
          <Card className="p-6 hover:shadow-lg transition-all group cursor-pointer border-transparent hover:border-primary/20">
            <div className="space-y-3">
              <div className="h-11 w-11 rounded-xl gradient-primary flex items-center justify-center">
                <PenTool className="h-5 w-5 text-primary-foreground" />
              </div>
              <h3 className="font-bold text-lg text-foreground">Create from Idea</h3>
              <p className="text-sm text-muted-foreground">Enter a topic and context, get a polished LinkedIn post with hooks and hashtags.</p>
              <span className="text-primary text-sm font-medium inline-flex items-center gap-1 group-hover:gap-2 transition-all">
                Start writing <ArrowRight className="h-3.5 w-3.5" />
              </span>
            </div>
          </Card>
        </Link>

        <Link to="/url">
          <Card className="p-6 hover:shadow-lg transition-all group cursor-pointer border-transparent hover:border-primary/20">
            <div className="space-y-3">
              <div className="h-11 w-11 rounded-xl bg-accent flex items-center justify-center">
                <Globe className="h-5 w-5 text-accent-foreground" />
              </div>
              <h3 className="font-bold text-lg text-foreground">Convert from URL</h3>
              <p className="text-sm text-muted-foreground">Paste an article URL and get a unique LinkedIn post with your personal angle.</p>
              <span className="text-primary text-sm font-medium inline-flex items-center gap-1 group-hover:gap-2 transition-all">
                Paste a link <ArrowRight className="h-3.5 w-3.5" />
              </span>
            </div>
          </Card>
        </Link>
      </div>

      {/* Recent Output */}
      {output && (
        <div className="space-y-3">
          <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" /> Latest Result
          </h2>
          <OutputDisplay />
        </div>
      )}
    </div>
  );
};

export default Dashboard;
