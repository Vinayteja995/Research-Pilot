import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import Sidebar from "@/components/layout/Sidebar";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "ResearchPilot — Multi-Agent Autonomous Academic Assistant",
  description: "Autonomously researches topics, compiles vector databases, identifies gaps, and generates gorgeous literature survey reports.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable} dark`}>
      <body className="bg-[#05070f] text-slate-100 min-h-screen flex antialiased font-sans">
        <Sidebar />
        <main className="flex-1 h-screen overflow-y-auto bg-[#070911] p-8 md:p-12">
          {children}
        </main>
      </body>
    </html>
  );
}
