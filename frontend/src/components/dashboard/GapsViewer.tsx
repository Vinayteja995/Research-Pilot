"use client";

import { Gap } from "@/lib/api";
import { AlertTriangle, Lightbulb, Target } from "lucide-react";

interface GapsViewerProps {
  gapsData?: { gaps: Gap[] };
}

export default function GapsViewer({ gapsData }: GapsViewerProps) {
  const gaps = gapsData?.gaps || [];

  if (!gaps.length) {
    return (
      <div className="glass-card rounded-2xl p-8 text-center border border-slate-900">
        <p className="text-slate-400 text-sm">No research gaps have been identified for this topic yet.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Target className="w-5 h-5 text-indigo-400" />
        <h3 className="text-lg font-bold text-white font-outfit">Identified Research Gaps & Open Problems</h3>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {gaps.map((gap, idx) => (
          <div
            key={idx}
            className="glass-card rounded-2xl p-6 flex flex-col justify-between border border-slate-900/60 shadow-lg relative overflow-hidden group hover:border-indigo-500/20 transition-all duration-300"
          >
            {/* Ambient visual background glow on hover */}
            <div className="absolute -right-16 -top-16 w-32 h-32 bg-indigo-500/5 rounded-full blur-2xl group-hover:bg-indigo-500/10 transition-all duration-300"></div>

            <div className="flex flex-col gap-4">
              {/* Gap Header Badge */}
              <div className="flex items-center justify-between">
                <span className="px-3 py-1 rounded-full text-[10px] font-bold bg-indigo-950/40 text-indigo-300 border border-indigo-900/40 tracking-wider uppercase">
                  Research Gap #{idx + 1}
                </span>
              </div>

              {/* Title & Description */}
              <div className="flex flex-col gap-2">
                <h4 className="text-base font-bold text-white tracking-tight leading-snug font-outfit">
                  {gap.title}
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed font-sans">
                  {gap.description}
                </p>
              </div>

              {/* Section Breakdown Grid */}
              <div className="flex flex-col gap-3 mt-2">
                {/* Implications */}
                <div className="flex gap-2.5 items-start p-3 rounded-xl bg-slate-950/20 border border-slate-900/40">
                  <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                  <div className="flex flex-col gap-0.5">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Implications</span>
                    <span className="text-xs text-slate-300 font-sans leading-relaxed">{gap.implications}</span>
                  </div>
                </div>

                {/* Proposed Approach */}
                <div className="flex gap-2.5 items-start p-3 rounded-xl bg-indigo-950/10 border border-indigo-950/30">
                  <Lightbulb className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
                  <div className="flex flex-col gap-0.5">
                    <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">Proposed Approach</span>
                    <span className="text-xs text-slate-300 font-sans leading-relaxed">{gap.proposed_approach}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
