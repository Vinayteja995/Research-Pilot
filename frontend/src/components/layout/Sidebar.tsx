"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Compass, LayoutDashboard, FileText, Database, Shield } from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  const menuItems = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "New Research", href: "/new-research", icon: Compass },
  ];

  return (
    <aside className="w-64 min-h-screen bg-[#070a13] border-r border-slate-900 flex flex-col justify-between p-6">
      <div className="flex flex-col gap-8">
        {/* Brand Header */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-400 to-indigo-500 flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform duration-300">
            <Compass className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white font-sans">
              Research<span className="text-teal-400">Pilot</span>
            </h1>
            <p className="text-[10px] text-slate-500 font-medium">AUTONOMOUS RESEARCH</p>
          </div>
        </Link>

        {/* Navigation Items */}
        <nav className="flex flex-col gap-2">
          {menuItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 ${
                  isActive
                    ? "bg-slate-900 text-teal-400 border-l-2 border-teal-400 font-semibold"
                    : "text-slate-400 hover:text-white hover:bg-slate-900/30"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-teal-400" : "text-slate-400"}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer / System Status */}
      <div className="glass-card p-4 rounded-xl flex items-center gap-3">
        <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></div>
        <div>
          <p className="text-xs font-semibold text-slate-200">System Engine</p>
          <p className="text-[10px] text-slate-500">Autonomous & Online</p>
        </div>
      </div>
    </aside>
  );
}
