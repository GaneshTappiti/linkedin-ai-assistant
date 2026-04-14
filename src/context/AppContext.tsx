import React, { createContext, useContext, useState, ReactNode } from "react";

export interface UserProfile {
  name: string;
  bio: string;
  skills: string;
  tone: string;
  pastPosts: string;
}

export interface GeneratedOutput {
  hooks: string[];
  post: string;
  hashtags: string[];
  imagePrompt: string;
}

interface AppState {
  profile: UserProfile;
  setProfile: (p: UserProfile) => void;
  output: GeneratedOutput | null;
  setOutput: (o: GeneratedOutput | null) => void;
  isGenerating: boolean;
  setIsGenerating: (v: boolean) => void;
}

const defaultProfile: UserProfile = {
  name: "",
  bio: "",
  skills: "",
  tone: "professional",
  pastPosts: "",
};

const AppContext = createContext<AppState | null>(null);

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [profile, setProfile] = useState<UserProfile>(() => {
    const saved = localStorage.getItem("linkedin-profile");
    return saved ? JSON.parse(saved) : defaultProfile;
  });
  const [output, setOutput] = useState<GeneratedOutput | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleSetProfile = (p: UserProfile) => {
    setProfile(p);
    localStorage.setItem("linkedin-profile", JSON.stringify(p));
  };

  return (
    <AppContext.Provider value={{ profile, setProfile: handleSetProfile, output, setOutput, isGenerating, setIsGenerating }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
};
