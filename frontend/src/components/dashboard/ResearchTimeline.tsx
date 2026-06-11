"use client";

import { CheckCircle2, Loader2, Circle, AlertCircle } from "lucide-react";

interface TimelineStep {
  key: string;
  label: string;
  description: string;
  triggerStatuses: string[];
}

const TIMELINE_STEPS: TimelineStep[] = [
  {
    key: "searching",
    label: "Academic arXiv Search",
    description: "Formulating semantic search terms and querying arXiv databases...",
    triggerStatuses: ["searching"],
  },
  {
    key: "retrieving",
    label: "Document Processing & Indexing",
    description: "Downloading paper PDFs, extracting text structures, and compiling vector collections...",
    triggerStatuses: ["retrieving"],
  },
  {
    key: "summarizing",
    label: "Paper Summarization",
    description: "Reading abstracts and text chunks to generate structured objective-methodology-metric data...",
    triggerStatuses: ["summarizing"],
  },
  {
    key: "criticizing",
    label: "Multi-Agent Critique Synthesis",
    description: "Analyzing academic agreements, contradictions, and methodological flaws...",
    triggerStatuses: ["criticizing"],
  },
  {
    key: "gaps",
    label: "Research Gap Discovery",
    description: "Translating critical reviews into actionable open problems and future approaches...",
    triggerStatuses: ["gaps"],
  },
  {
    key: "roadmap",
    label: "Technical Syllabus Compilation",
    description: "Creating Beginner -> Advanced curriculum and reproduction projects roadmap...",
    triggerStatuses: ["roadmap", "reporting"],
  },
  {
    key: "completed",
    label: "PDF Survey Generation",
    description: "Synthesizing full literature review markdown and compiling professional ReportLab PDFs...",
    triggerStatuses: ["completed"],
  },
];

interface ResearchTimelineProps {
  currentStatus: string;
}

export default function ResearchTimeline({ currentStatus }: ResearchTimelineProps) {
  const getStepState = (stepIndex: number) => {
    if (currentStatus === "failed") {
      return "failed";
    }
    
    // Find active step index
    const activeStepIndex = TIMELINE_STEPS.findIndex((step) =>
      step.triggerStatuses.includes(currentStatus)
    );

    if (currentStatus === "completed") {
      return "completed";
    }

    if (activeStepIndex === -1) {
      return "queued";
    }

    if (stepIndex < activeStepIndex) {
      return "completed";
    } else if (stepIndex === activeStepIndex) {
      return "active";
    } else {
      return "queued";
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1">
        <h3 className="text-base font-bold text-white font-outfit">Research Execution Pipeline</h3>
        <p className="text-xs text-slate-400">Real-time status updates from the multi-agent engine</p>
      </div>

      <div className="relative pl-8 flex flex-col gap-8">
        {/* Vertical Connector Line */}
        <div className="absolute left-3.5 top-2 bottom-2 w-0.5 bg-slate-800"></div>

        {TIMELINE_STEPS.map((step, idx) => {
          const state = getStepState(idx);
          
          return (
            <div key={step.key} className="relative flex flex-col gap-1 transition-all duration-300">
              {/* State Indicator Icon */}
              <div className="absolute -left-8 top-0.5 flex items-center justify-center bg-[#070911]">
                {state === "completed" && (
                  <CheckCircle2 className="w-7 h-7 text-emerald-400 fill-emerald-950/30" />
                )}
                {state === "active" && (
                  <div className="relative flex items-center justify-center">
                    <span className="absolute w-8 h-8 rounded-full bg-teal-400/20 animate-ping"></span>
                    <Loader2 className="w-6 h-6 text-teal-400 animate-spin" />
                  </div>
                )}
                {state === "queued" && (
                  <Circle className="w-5 h-5 text-slate-700 bg-[#070911] p-0.5" />
                )}
                {state === "failed" && (
                  <AlertCircle className="w-6 h-6 text-rose-500 fill-rose-950/20" />
                )}
              </div>

              {/* Text Meta */}
              <div className="flex flex-col">
                <span
                  className={`text-sm font-semibold tracking-wide ${
                    state === "completed"
                      ? "text-emerald-400"
                      : state === "active"
                      ? "text-teal-300"
                      : "text-slate-500"
                  }`}
                >
                  {step.label}
                </span>
                <p
                  className={`text-xs ${
                    state === "active" ? "text-slate-300 font-medium" : "text-slate-500"
                  }`}
                >
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
