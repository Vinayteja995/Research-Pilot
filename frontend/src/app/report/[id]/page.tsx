"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getResearchDetails, getReportDownloadUrl, ResearchJobDetails } from "@/lib/api";
import GapsViewer from "@/components/dashboard/GapsViewer";
import SyllabusRoadmap from "@/components/dashboard/SyllabusRoadmap";
import { FileText, Download, LayoutDashboard, Copy, Check, Table, HelpCircle, Layers } from "lucide-react";

// Local highly robust Markdown formatter to output markdown to premium HTML structure
function renderMarkdownToHtml(markdown?: string) {
  if (!markdown) return null;

  const lines = markdown.split("\n");
  const story: React.ReactNode[] = [];
  let inList = false;
  let inTable = false;
  let tableHeaders: string[] = [];
  let tableRows: string[][] = [];

  const formatText = (text: string) => {
    // Format bold **text** -> <strong>text</strong>
    let formatted = text;
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    formatted = formatted.replace(/\*(.*?)\*/g, "<em>$1</em>");
    formatted = formatted.replace(/`(.*?)`/g, "<code class='bg-slate-900/60 px-1.5 py-0.5 rounded text-teal-400 font-mono text-[11px]'>$1</code>");
    return <span dangerouslySetInnerHTML={{ __html: formatted }} />;
  };

  let listKey = 0;
  let tableKey = 0;

  for (let idx = 0; idx < lines.length; idx++) {
    const line = lines[idx].trim();

    // Table Parsing
    if (line.startsWith("|")) {
      inTable = true;
      const cells = line.split("|").map(c => c.trim()).filter((_, i, arr) => i > 0 && i < arr.length - 1);
      
      // Skip dividing lines |---|---|
      if (cells.every(c => c.startsWith("-"))) {
        continue;
      }
      
      if (tableHeaders.length === 0) {
        tableHeaders = cells;
      } else {
        tableRows.push(cells);
      }
      continue;
    } else if (inTable && !line.startsWith("|")) {
      // Render compiled table
      inTable = false;
      if (tableHeaders.length > 0) {
        const currentHeaders = [...tableHeaders];
        const currentRows = [...tableRows];
        story.push(
          <div key={`table-${tableKey++}`} className="overflow-x-auto my-6 border border-slate-900 rounded-xl">
            <table className="w-full text-xs text-left text-slate-300 font-sans">
              <thead className="text-[10px] text-slate-400 uppercase bg-slate-950/60 border-b border-slate-900">
                <tr>
                  {currentHeaders.map((h, i) => (
                    <th key={i} className="px-4 py-3 font-semibold">{formatText(h)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {currentRows.map((row, i) => (
                  <tr key={i} className="border-b border-slate-900 bg-slate-900/10 hover:bg-slate-900/30">
                    {row.map((cell, j) => (
                      <td key={j} className="px-4 py-3 leading-relaxed">{formatText(cell)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
        tableHeaders = [];
        tableRows = [];
      }
    }

    // Header 2
    if (line.startsWith("## ")) {
      story.push(
        <h3 key={idx} className="text-base font-bold text-white font-outfit mt-8 mb-3 border-b border-slate-900 pb-2">
          {line.replace("## ", "")}
        </h3>
      );
      continue;
    }

    // Header 3
    if (line.startsWith("### ")) {
      story.push(
        <h4 key={idx} className="text-sm font-bold text-teal-400 font-outfit mt-6 mb-2">
          {line.replace("### ", "")}
        </h4>
      );
      continue;
    }

    // Bullet List
    if (line.startsWith("- ") || line.startsWith("* ")) {
      const content = line.substring(2);
      story.push(
        <div key={idx} className="flex gap-2 items-start text-xs text-slate-300 leading-relaxed font-sans pl-4 py-1">
          <span className="w-1.5 h-1.5 rounded-full bg-teal-400 mt-1.5 shrink-0"></span>
          <span>{formatText(content)}</span>
        </div>
      );
      continue;
    }

    // Paragraph
    if (line !== "") {
      story.push(
        <p key={idx} className="text-xs text-slate-400 leading-relaxed font-sans mb-3">
          {formatText(line)}
        </p>
      );
    }
  }

  return <div className="flex flex-col">{story}</div>;
}

export default function ReportDetails() {
  const { id } = useParams();
  const router = useRouter();
  
  const [data, setData] = useState<ResearchJobDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"survey" | "gaps" | "roadmap">("survey");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!id) return;
    
    const fetchDetails = async () => {
      try {
        setLoading(true);
        const res = await getResearchDetails(id as string);
        setData(res);
        setError("");
      } catch (err) {
        console.error(err);
        setError("Failed to fetch full research details.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchDetails();
  }, [id]);

  const copyMarkdown = () => {
    if (!data?.report_markdown) return;
    navigator.clipboard.writeText(data.report_markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="flex flex-col gap-8 animate-pulse">
        <div className="h-8 bg-slate-900 rounded w-1/3"></div>
        <div className="h-64 bg-slate-900 rounded-3xl"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-md mx-auto text-center flex flex-col gap-4 py-12">
        <div className="p-4 rounded-xl border border-rose-950/40 bg-rose-950/10 text-rose-400 text-xs font-semibold">
          {error || "Research details not found."}
        </div>
        <button
          onClick={() => router.push("/")}
          className="px-5 py-3 bg-slate-900 hover:bg-slate-800 text-slate-200 text-xs font-bold uppercase rounded-xl transition-all"
        >
          Return to Command
        </button>
      </div>
    );
  }

  const papers = data.papers || [];
  const summaries = data.summaries || [];

  return (
    <div className="flex flex-col gap-10">
      {/* 1. Header Navigation & Controls */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] font-bold text-teal-400 uppercase tracking-widest">RESEARCH SURVEY MISSION COMPLETE</span>
          <h2 className="text-2xl font-extrabold text-white tracking-tight font-outfit">
            {data.topic}
          </h2>
        </div>

        <div className="flex gap-4 w-full md:w-auto">
          {/* Copy MD button */}
          <button
            onClick={copyMarkdown}
            className="flex-1 md:flex-initial px-4 py-3 rounded-xl border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-900/40 flex items-center justify-center gap-2 text-xs font-semibold tracking-wider uppercase transition-all duration-300"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                Copied
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                Copy MD
              </>
            )}
          </button>
          
          {/* Download PDF button */}
          <a
            href={getReportDownloadUrl(data.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 md:flex-initial px-5 py-3 rounded-xl bg-gradient-to-r from-teal-400 to-indigo-500 hover:from-teal-300 hover:to-indigo-400 text-white shadow-lg flex items-center justify-center gap-2 text-xs font-bold tracking-wider uppercase transition-all duration-300 hover:scale-[1.02]"
          >
            <Download className="w-4 h-4 animate-bounce" style={{ animationDuration: "3s" }} />
            Download PDF Report
          </a>
        </div>
      </div>

      {/* 2. Viewer Tabs Navigation */}
      <div className="flex rounded-xl bg-slate-950/40 p-1 border border-slate-900">
        <button
          onClick={() => setActiveTab("survey")}
          className={`flex-1 text-center py-3 rounded-lg text-xs font-semibold tracking-wide transition-all duration-300 ${
            activeTab === "survey"
              ? "bg-slate-900 text-white shadow border-b border-slate-850"
              : "text-slate-500 hover:text-slate-350"
          }`}
        >
          Survey & Critiques
        </button>
        <button
          onClick={() => setActiveTab("gaps")}
          className={`flex-1 text-center py-3 rounded-lg text-xs font-semibold tracking-wide transition-all duration-300 ${
            activeTab === "gaps"
              ? "bg-slate-900 text-white shadow border-b border-slate-850"
              : "text-slate-500 hover:text-slate-355"
          }`}
        >
          Identified Gaps ({data.gaps?.gaps?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab("roadmap")}
          className={`flex-1 text-center py-3 rounded-lg text-xs font-semibold tracking-wide transition-all duration-300 ${
            activeTab === "roadmap"
              ? "bg-slate-900 text-white shadow border-b border-slate-850"
              : "text-slate-500 hover:text-slate-355"
          }`}
        >
          Mastery Roadmap
        </button>
      </div>

      {/* 3. Tab Contents */}
      <div className="flex flex-col gap-10">
        {activeTab === "survey" && (
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 items-start">
            {/* Left/Middle Content: Synthesized Markdown Critique */}
            <div className="xl:col-span-2 flex flex-col gap-6">
              <div className="glass-card rounded-3xl p-8 border border-slate-900 flex flex-col gap-4">
                <div className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-indigo-400" />
                  <h3 className="text-lg font-bold text-white font-outfit">SOTA Synthesis & Critical Review</h3>
                </div>
                
                <div className="mt-4 prose prose-invert max-w-none">
                  {renderMarkdownToHtml(data.criticism)}
                </div>
              </div>
            </div>

            {/* Right Panel: Analyzed Paper Cards */}
            <div className="flex flex-col gap-6">
              <h3 className="text-base font-bold text-white font-outfit px-1">Indexed Source Materials</h3>
              
              <div className="flex flex-col gap-4 max-h-[75vh] overflow-y-auto pr-2">
                {summaries.map((s, idx) => (
                  <div key={s.paper_id} className="glass-card rounded-2xl p-5 border border-slate-900 flex flex-col gap-3 relative group hover:border-slate-800 transition-all duration-300">
                    <div className="flex flex-col gap-1">
                      <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">PAPER #{idx+1}</span>
                      <h4 className="text-xs font-bold text-white leading-snug tracking-tight font-outfit">
                        {s.title}
                      </h4>
                    </div>

                    <div className="flex flex-col gap-2.5 mt-2">
                      <div className="flex flex-col gap-0.5">
                        <span className="text-[9px] font-bold text-teal-400 uppercase tracking-wider">Objective</span>
                        <p className="text-[11px] text-slate-400 leading-relaxed font-sans">{s.objective}</p>
                      </div>
                      <div className="flex flex-col gap-0.5">
                        <span className="text-[9px] font-bold text-indigo-400 uppercase tracking-wider">Methodology</span>
                        <p className="text-[11px] text-slate-400 leading-relaxed font-sans">{s.methodology}</p>
                      </div>
                      <div className="flex flex-col gap-0.5">
                        <span className="text-[9px] font-bold text-fuchsia-400 uppercase tracking-wider">Limitations</span>
                        <p className="text-[11px] text-slate-400 leading-relaxed font-sans">{s.limitations}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "gaps" && (
          <GapsViewer gapsData={data.gaps} />
        )}

        {activeTab === "roadmap" && (
          <SyllabusRoadmap roadmap={data.roadmap} />
        )}
      </div>
    </div>
  );
}
