"use client";

import { Roadmap } from "@/lib/api";
import { BookOpen, GraduationCap, Code, Layers } from "lucide-react";
import { useState } from "react";

interface SyllabusRoadmapProps {
  roadmap?: Roadmap;
}

export default function SyllabusRoadmap({ roadmap }: SyllabusRoadmapProps) {
  const [activeTier, setActiveTier] = useState<"beginner" | "intermediate" | "advanced">("beginner");

  if (!roadmap) {
    return (
      <div className="glass-card rounded-2xl p-8 text-center border border-slate-900">
        <p className="text-slate-400 text-sm">No mastery roadmap has been compiled for this topic yet.</p>
      </div>
    );
  }

  const tiers = [
    { key: "beginner", label: "Foundational (Beginner)", colorClass: "text-teal-400", borderClass: "border-teal-500/20", bgClass: "bg-teal-950/10" },
    { key: "intermediate", label: "Core Research (Intermediate)", colorClass: "text-indigo-400", borderClass: "border-indigo-500/20", bgClass: "bg-indigo-950/10" },
    { key: "advanced", label: "State of the Art (Advanced)", colorClass: "text-fuchsia-400", borderClass: "border-fuchsia-500/20", bgClass: "bg-fuchsia-950/10" },
  ] as const;

  const activeData = roadmap[activeTier] || { concepts: [], reading: [], projects: [] };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <GraduationCap className="w-5 h-5 text-teal-400" />
        <h3 className="text-lg font-bold text-white font-outfit">Tiered Mastery Syllabus & Roadmap</h3>
      </div>

      {/* Tier Tabs Navigation */}
      <div className="flex rounded-xl bg-slate-950/40 p-1 border border-slate-900">
        {tiers.map((tier) => (
          <button
            key={tier.key}
            onClick={() => setActiveTier(tier.key)}
            className={`flex-1 text-center py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all duration-300 ${
              activeTier === tier.key
                ? "bg-slate-900 text-white shadow-md border-b border-slate-800"
                : "text-slate-500 hover:text-slate-300"
            }`}
          >
            {tier.label}
          </button>
        ))}
      </div>

      {/* active Tier Syllabus Content */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* column 1: Concepts */}
        <div className="glass-card rounded-2xl p-5 border border-slate-900 flex flex-col gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-teal-950/30 border border-teal-900/30 flex items-center justify-center">
              <Layers className="w-4 h-4 text-teal-400" />
            </div>
            <h4 className="text-sm font-bold text-white font-outfit">Core Concepts to Master</h4>
          </div>
          <ul className="flex flex-col gap-2.5">
            {activeData.concepts?.map((c, i) => (
              <li key={i} className="flex gap-2 items-start text-xs text-slate-300 leading-relaxed font-sans">
                <span className="w-1.5 h-1.5 rounded-full bg-teal-400 mt-1.5 shrink-0"></span>
                <span>{c}</span>
              </li>
            ))}
            {!activeData.concepts?.length && (
              <li className="text-xs text-slate-500 italic">No concepts specified.</li>
            )}
          </ul>
        </div>

        {/* column 2: Literature / Readings */}
        <div className="glass-card rounded-2xl p-5 border border-slate-900 flex flex-col gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-950/30 border border-indigo-900/30 flex items-center justify-center">
              <BookOpen className="w-4 h-4 text-indigo-400" />
            </div>
            <h4 className="text-sm font-bold text-white font-outfit">Required Readings & Literature</h4>
          </div>
          <ul className="flex flex-col gap-2.5">
            {activeData.reading?.map((r, i) => (
              <li key={i} className="flex gap-2 items-start text-xs text-slate-300 leading-relaxed font-sans">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0"></span>
                <span>{r}</span>
              </li>
            ))}
            {!activeData.reading?.length && (
              <li className="text-xs text-slate-500 italic">No readings specified.</li>
            )}
          </ul>
        </div>

        {/* column 3: Hands-On Projects */}
        <div className="glass-card rounded-2xl p-5 border border-slate-900 flex flex-col gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-fuchsia-950/30 border border-fuchsia-900/30 flex items-center justify-center">
              <Code className="w-4 h-4 text-fuchsia-400" />
            </div>
            <h4 className="text-sm font-bold text-white font-outfit">Reproduction Projects & Labs</h4>
          </div>
          <ul className="flex flex-col gap-2.5">
            {activeData.projects?.map((p, i) => (
              <li key={i} className="flex gap-2 items-start text-xs text-slate-300 leading-relaxed font-sans">
                <span className="w-1.5 h-1.5 rounded-full bg-fuchsia-400 mt-1.5 shrink-0"></span>
                <span>{p}</span>
              </li>
            ))}
            {!activeData.projects?.length && (
              <li className="text-xs text-slate-500 italic">No projects specified.</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
