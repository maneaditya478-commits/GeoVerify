import React from 'react';
import { Compass, Map, History, BookOpen, Info } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  backendHealthy: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, backendHealthy }) => {
  const navItems = [
    { id: 'verify', label: 'Verify Address', icon: <Compass className="w-4 h-4" /> },
    { id: 'map', label: 'Map Explorer', icon: <Map className="w-4 h-4" /> },
    { id: 'history', label: 'Verification History', icon: <History className="w-4 h-4" /> },
    { id: 'docs', label: 'Documentation', icon: <BookOpen className="w-4 h-4" /> },
    { id: 'about', label: 'About', icon: <Info className="w-4 h-4" /> },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('verify')}>
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-md shadow-emerald-950">
            <Compass className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-white tracking-tight text-lg">GeoVerify</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                India
              </span>
            </div>
            <p className="text-[10px] font-mono text-slate-400 hidden sm:block">
              Geographic & Administrative Intelligence
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1 font-mono text-xs">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
                activeTab === item.id
                  ? 'bg-slate-800 text-emerald-400 font-semibold border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Backend Status Indicator */}
        <div className="flex items-center gap-2 font-mono text-xs">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800">
            <div
              className={`w-2 h-2 rounded-full ${
                backendHealthy ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'
              }`}
            />
            <span className="text-slate-400 text-[11px]">
              {backendHealthy ? 'Engine Online' : 'Engine Offline'}
            </span>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="md:hidden flex items-center justify-around border-t border-slate-800/80 bg-slate-950 px-2 py-1.5 font-mono text-xs overflow-x-auto">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`flex flex-col items-center gap-1 p-1.5 rounded transition-colors ${
              activeTab === item.id ? 'text-emerald-400 font-semibold' : 'text-slate-400'
            }`}
          >
            {item.icon}
            <span className="text-[10px]">{item.label.split(' ')[0]}</span>
          </button>
        ))}
      </div>
    </header>
  );
};
