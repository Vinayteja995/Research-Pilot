"use client";

import { useEffect, useState, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { startResearch, uploadPdfsAndResearch, getResearchStatus } from "@/lib/api";
import ResearchTimeline from "@/components/dashboard/ResearchTimeline";
import { Compass, Upload, FileText, AlertCircle, Trash2, ArrowRight } from "lucide-react";

function NewResearchInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // URL params tracking for live polling mode
  const activeJobId = searchParams.get("job_id");
  const activeTopic = searchParams.get("topic");

  const [topic, setTopic] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  // Polling state
  const [polledStatus, setPolledStatus] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Poll status when activeJobId is present in URL
  useEffect(() => {
    if (!activeJobId) return;

    setLoading(true);
    setPolledStatus("searching"); // Initial assumed state

    const interval = setInterval(async () => {
      try {
        const res = await getResearchStatus(activeJobId);
        setPolledStatus(res.status);
        
        if (res.status === "completed") {
          clearInterval(interval);
          router.push(`/report/${activeJobId}`);
        } else if (res.status === "failed") {
          clearInterval(interval);
          setLoading(false);
          setError("Autonomous research agent workflow encountered a compilation error.");
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [activeJobId, router]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const addedFiles: File[] = [];
      for (let i = 0; i < e.dataTransfer.files.length; i++) {
        const file = e.dataTransfer.files[i];
        if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
          addedFiles.push(file);
        }
      }
      setFiles((prev) => [...prev, ...addedFiles]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const addedFiles: File[] = [];
      for (let i = 0; i < e.target.files.length; i++) {
        addedFiles.push(e.target.files[i]);
      }
      setFiles((prev) => [...prev, ...addedFiles]);
    }
  };

  const removeFile = (idx: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!topic.trim()) {
      setError("Please input a valid research topic.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      
      let jobId = "";
      
      if (files.length > 0) {
        // Upload local PDFs research route
        const res = await uploadPdfsAndResearch(topic, files);
        jobId = res.job_id;
      } else {
        // Direct arXiv search research route
        const res = await startResearch(topic);
        jobId = res.job_id;
      }
      
      // Update URL parameters to switch page view to active polling mode
      router.push(`/new-research?job_id=${jobId}&topic=${encodeURIComponent(topic)}`);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to launch research mission. Check backend status.");
      setLoading(false);
    }
  };

  // 1. LIVE POLLING STATE VIEW
  if (activeJobId) {
    return (
      <div className="max-w-2xl mx-auto flex flex-col gap-10 py-6">
        <div className="flex flex-col gap-1.5 text-center">
          <h2 className="text-2xl font-extrabold text-white font-outfit uppercase tracking-wider">
            Autonomous Research Session Active
          </h2>
          <p className="text-xs text-slate-400 font-medium">
            Topic: <span className="text-teal-400 font-semibold">"{activeTopic}"</span>
          </p>
        </div>

        <div className="glass-card rounded-3xl p-8 border border-slate-900 shadow-2xl relative overflow-hidden">
          <div className="absolute -left-16 -top-16 w-32 h-32 bg-teal-500/5 rounded-full blur-2xl"></div>
          <div className="absolute -right-16 -bottom-16 w-32 h-32 bg-indigo-500/5 rounded-full blur-2xl"></div>
          
          <ResearchTimeline currentStatus={polledStatus} />
        </div>

        {polledStatus === "failed" && (
          <div className="p-4 rounded-xl border border-rose-950/40 bg-rose-950/10 text-rose-300 text-xs font-semibold flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            Execution terminated. Please return to dashboard and try again.
          </div>
        )}
      </div>
    );
  }

  // 2. CONFIGURATION INTAKE VIEW
  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-8">
      <div className="flex flex-col gap-1.5">
        <h2 className="text-2xl font-extrabold text-white font-outfit">
          Launch Autonomous Research
        </h2>
        <p className="text-xs text-slate-400 leading-relaxed font-sans">
          Provide a topic to search arXiv preprints automatically, OR upload local PDF papers to analyze and synthesize them directly.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-rose-950/40 bg-rose-950/10 text-rose-300 text-xs font-medium leading-relaxed flex items-center gap-2">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-8">
        {/* Topic Input */}
        <div className="glass-card rounded-2xl p-6 border border-slate-900 flex flex-col gap-4">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Research Domain / Topic
          </label>
          <input
            type="text"
            placeholder="e.g. Multi-Agent Orchestration in Healthcare"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={loading}
            className="w-full bg-slate-950/40 border border-slate-900 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-teal-500/50 transition-colors"
          />
        </div>

        {/* Local PDF Drop Area */}
        <div className="glass-card rounded-2xl p-6 border border-slate-900 flex flex-col gap-4">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Upload Local PDFs (Optional)
          </label>

          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`w-full py-8 border-2 border-dashed rounded-xl flex flex-col items-center gap-3 cursor-pointer transition-all duration-300 ${
              dragActive
                ? "border-teal-400 bg-teal-950/5"
                : "border-slate-900 hover:border-slate-800 bg-slate-950/10 hover:bg-slate-950/20"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
            />
            <Upload className="w-8 h-8 text-slate-600 animate-bounce" style={{ animationDuration: "3s" }} />
            <div className="flex flex-col items-center gap-1">
              <span className="text-xs font-bold text-slate-200">Drag and drop academic PDFs here</span>
              <span className="text-[10px] text-slate-500">Supports PDF format up to 50MB</span>
            </div>
          </div>

          {/* Files List */}
          {files.length > 0 && (
            <div className="flex flex-col gap-2 mt-2">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Selected Documents ({files.length})</span>
              <div className="flex flex-col gap-2 max-h-48 overflow-y-auto pr-2">
                {files.map((file, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-slate-950/40 border border-slate-950 flex justify-between items-center text-xs"
                  >
                    <div className="flex items-center gap-2 w-3/4">
                      <FileText className="w-4 h-4 text-teal-400 shrink-0" />
                      <span className="text-slate-200 truncate">{file.name}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFile(idx)}
                      className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Submit Launcher */}
        <button
          type="submit"
          disabled={loading || !topic.trim()}
          className="w-full py-4 rounded-2xl bg-gradient-to-r from-teal-400 to-indigo-500 hover:from-teal-300 hover:to-indigo-400 text-white font-bold text-xs tracking-wider uppercase flex items-center justify-center gap-2 transition-all duration-300 hover:scale-[1.01] shadow-xl disabled:opacity-50 disabled:pointer-events-none"
        >
          <Compass className="w-4 h-4" />
          Deploy Autonomous Research Engine
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}

export default function NewResearch() {
  return (
    <Suspense fallback={
      <div className="max-w-2xl mx-auto text-center py-20 flex flex-col gap-4 items-center">
        <div className="w-10 h-10 border-4 border-slate-900 border-t-teal-400 rounded-full animate-spin"></div>
        <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase">Loading Research Deck...</p>
      </div>
    }>
      <NewResearchInner />
    </Suspense>
  );
}
