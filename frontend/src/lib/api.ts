const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface ResearchJobStatus {
  id: string;
  topic: string;
  status: string;
  created_at: string;
  updated_at: string;
  papers_count: number;
  has_report: boolean;
  progress_percentage: number;
}

export interface Paper {
  id: string;
  title: string;
  authors: string;
  abstract: string;
  url: string;
  pdf_url: string;
  published: string;
}

export interface Summary {
  paper_id: string;
  title: string;
  objective: string;
  methodology: string;
  findings: string;
  limitations: string;
}

export interface Gap {
  title: string;
  description: string;
  implications: string;
  proposed_approach: string;
}

export interface RoadmapLevel {
  concepts: string[];
  reading: string[];
  projects: string[];
}

export interface Roadmap {
  beginner: RoadmapLevel;
  intermediate: RoadmapLevel;
  advanced: RoadmapLevel;
}

export interface ResearchJobDetails {
  id: string;
  topic: string;
  status: string;
  papers?: Paper[];
  summaries?: Summary[];
  criticism?: string;
  gaps?: { gaps: Gap[] };
  roadmap?: Roadmap;
  report_markdown?: string;
  report_path?: string;
  created_at: string;
  updated_at: string;
}

export async function startResearch(topic: string): Promise<{ job_id: string; status: string }> {
  const response = await fetch(`${API_BASE_URL}/research/start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ topic }),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to initiate research: ${response.statusText}`);
  }
  return response.json();
}

export async function getResearchStatus(jobId: string): Promise<ResearchJobStatus> {
  const response = await fetch(`${API_BASE_URL}/research/status/${jobId}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch job status: ${response.statusText}`);
  }
  return response.json();
}

export async function getResearchDetails(jobId: string): Promise<ResearchJobDetails> {
  const response = await fetch(`${API_BASE_URL}/research/details/${jobId}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch job details: ${response.statusText}`);
  }
  return response.json();
}

export async function uploadPdfsAndResearch(
  topic: string,
  files: File[]
): Promise<{ job_id: string; status: string }> {
  const formData = new FormData();
  formData.append("topic", topic);
  files.forEach((file) => {
    formData.append("files", file);
  });
  
  const response = await fetch(`${API_BASE_URL}/upload?topic=${encodeURIComponent(topic)}`, {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to upload PDFs and begin synthesis: ${response.statusText}`);
  }
  return response.json();
}

export function getReportDownloadUrl(jobId: string): string {
  return `${API_BASE_URL}/report/${jobId}`;
}

export async function listResearchJobs(): Promise<ResearchJobStatus[]> {
  const response = await fetch(`${API_BASE_URL}/research/jobs`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Failed to list research jobs: ${response.statusText}`);
  }
  return response.json();
}
