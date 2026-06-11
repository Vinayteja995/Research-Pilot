"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listResearchJobs, ResearchJobStatus } from "@/lib/api";
import { Compass, BookOpen, Target, Calendar, ArrowRight, RefreshCw, FileText } from "lucide-react";

export default function Dashboard() {
  const [jobs, setJobs] = useState<ResearchJobStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const data = await listResearchJobs();
      setJobs(data);
      setError("");
    } catch (e: any) {
      console.error(e);
      setError("Failed to fetch historical research missions. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  // Compute stats
  const totalMissions = jobs.length;
  const totalPapers = jobs.reduce((acc, curr) => acc + (curr.papers_count || 0), 0);
  const completedReports = jobs.filter((j) => j.status === "completed").length;

  return (
    <div className="flex flex-col gap-10">
      {/* 1. Header Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="flex flex-col gap-1.5">
          <h2 className="text-3xl font-extrabold tracking-tight text-white font-outfit">
            Academic Research Command
          </h2>
          <p className="text-sm text-slate-400">
            Deploy autonomous agents to survey, analyze, and map complex academic fields.
          </p>
        </div>

        <div className="flex gap-4">
          <button
            onClick={fetchJobs}
            disabled={loading}
            className="px-4 py-3 rounded-xl border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-900/40 flex items-center gap-2 text-xs font-semibold tracking-wider uppercase transition-all duration-300"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
          
          <Link
            href="/new-research"
            className="px-5 py-3 rounded-xl bg-gradient-to-r from-teal-400 to-indigo-500 hover:from-teal-300 hover:to-indigo-400 text-white shadow-lg shadow-indigo-950/20 flex items-center gap-2 text-xs font-bold tracking-wider uppercase transition-all duration-300 hover:scale-[1.02]"
          >
            <Compass className="w-4 h-4 animate-spin" style={{ animationDuration: "10s" }} />
            New Research Mission
          </Link>
        </div>
      </div>

      {/* 2. Error Display */}
      {error && (
        <div className="p-4 rounded-xl border border-rose-950/40 bg-rose-950/10 text-rose-300 text-xs font-medium leading-relaxed">
          {error}
        </div>
      )}

      {/* 3. Metric Widgets */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Stat 1 */}
        <div className="glass-card rounded-2xl p-6 border border-slate-900 relative overflow-hidden group">
          <div className="absolute -right-8 -bottom-8 w-24 h-24 bg-teal-500/5 rounded-full blur-2xl"></div>
          <div className="flex justify-between items-center">
            <div className="flex flex-col gap-1">
              <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Research Topics</span>
              <span className="text-3xl font-extrabold text-white font-outfit">{totalMissions}</span>
            </div>
            <div className="w-12 h-12 rounded-xl bg-teal-950/30 border border-teal-900/30 flex items-center justify-center">
              <Compass className="w-5 h-5 text-teal-400" />
            </div>
          </div>
        </div>

        {/* Stat 2 */}
        <div className="glass-card rounded-2xl p-6 border border-slate-900 relative overflow-hidden group">
          <div className="absolute -right-8 -bottom-8 w-24 h-24 bg-indigo-500/5 rounded-full blur-2xl"></div>
          <div className="flex justify-between items-center">
            <div className="flex flex-col gap-1">
              <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Indexed Papers</span>
              <span className="text-3xl font-extrabold text-white font-outfit">{totalPapers}</span>
            </div>
            <div className="w-12 h-12 rounded-xl bg-indigo-950/30 border border-indigo-900/30 flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-indigo-400" />
            </div>
          </div>
        </div>

        {/* Stat 3 */}
        <div className="glass-card rounded-2xl p-6 border border-slate-900 relative overflow-hidden group">
          <div className="absolute -right-8 -bottom-8 w-24 h-24 bg-fuchsia-500/5 rounded-full blur-2xl"></div>
          <div className="flex justify-between items-center">
            <div className="flex flex-col gap-1">
              <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Completed Reports</span>
              <span className="text-3xl font-extrabold text-white font-outfit">{completedReports}</span>
            </div>
            <div className="w-12 h-12 rounded-xl bg-fuchsia-950/30 border border-fuchsia-900/30 flex items-center justify-center">
              <FileText className="w-5 h-5 text-fuchsia-400" />
            </div>
          </div>
        </div>
      </div>

      {/* 4. Previous Archives */}
      <div className="flex flex-col gap-6">
        <h3 className="text-lg font-bold text-white font-outfit">Research Archives & History</h3>
        
        {loading ? (
          <div className="flex flex-col gap-4">
            {[1, 2].map((n) => (
              <div key={n} className="glass-card rounded-2xl p-6 border border-slate-900 animate-pulse flex justify-between items-center">
                <div className="flex flex-col gap-2 w-1/2">
                  <div className="h-4 bg-slate-800 rounded w-3/4"></div>
                  <div className="h-3 bg-slate-800 rounded w-1/4"></div>
                </div>
                <div className="w-24 h-8 bg-slate-800 rounded"></div>
              </div>
            ))}
          </div>
        ) : jobs.length === 0 ? (
          <div className="glass-card rounded-2xl p-12 text-center border border-slate-900 flex flex-col items-center gap-4">
            <Compass className="w-10 h-10 text-slate-600 animate-spin" style={{ animationDuration: "30s" }} />
            <div className="flex flex-col gap-1">
              <p className="text-sm font-bold text-white">No active or historical research missions found.</p>
              <p className="text-xs text-slate-400">Launch a new mission above to begin analyzing academic preprints.</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="glass-card glass-card-hover rounded-2xl p-6 border border-slate-900/80 flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
              >
                {/* Left Meta info */}
                <div className="flex flex-col gap-2">
                  <h4 className="text-base font-bold text-white tracking-tight leading-snug font-outfit">
                    {job.topic}
                  </h4>
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-400 font-sans">
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-500" />
                      <span>{new Date(job.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-slate-500" />
                      <span>{job.papers_count} papers indexed</span>
                    </div>
                    {/* Status Badge */}
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border tracking-wider uppercase ${
                        job.status === "completed"
                          ? "bg-emerald-950/20 text-emerald-400 border-emerald-900/30"
                          : job.status === "failed"
                          ? "bg-rose-950/20 text-rose-400 border-rose-900/30"
                          : "bg-teal-950/20 text-teal-400 border-teal-900/30 animate-pulse"
                      }`}
                    >
                      {job.status}
                    </span>
                  </div>
                </div>

                {/* Right Progress & View Button */}
                <div className="flex items-center gap-6 w-full md:w-auto justify-between md:justify-end">
                  {/* Progress Indicator */}
                  <div className="flex flex-col items-end gap-1">
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Mission Progress</span>
                    <div className="w-32 bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-900">
                      <div
                        className={`h-full rounded-full ${
                          job.status === "failed" ? "bg-rose-500" : "bg-gradient-to-r from-teal-400 to-indigo-500"
                        }`}
                        style={{ width: `${job.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Action Link */}
                  {job.status === "completed" ? (
                    <Link
                      href={`/report/${job.id}`}
                      className="px-4 py-2.5 rounded-lg border border-teal-500/20 hover:border-teal-500/50 bg-teal-950/10 hover:bg-teal-950/20 text-teal-400 text-xs font-bold tracking-wider uppercase flex items-center gap-1.5 transition-all duration-300"
                    >
                      View Report
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  ) : job.status === "failed" ? (
                    <span className="text-xs text-rose-400 font-semibold px-4 py-2 bg-rose-950/10 rounded-lg border border-rose-950/30">
                      Execution Failed
                    </span>
                  ) : (
                    <Link
                      href={`/new-research?job_id=${job.id}&topic=${encodeURIComponent(job.topic)}`}
                      className="px-4 py-2.5 rounded-lg border border-slate-800 hover:border-slate-700 bg-slate-900/50 hover:bg-slate-900 text-slate-300 hover:text-white text-xs font-bold tracking-wider uppercase flex items-center gap-1.5 transition-all duration-300"
                    >
                      Track Live
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
