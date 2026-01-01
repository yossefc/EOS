import Tabs from './components/tabs';
import { Shield, Bell, Settings, User } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header Premium (Sticky & Centered) */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200/50 shadow-sm transition-all duration-300">
        <div className="max-w-[1600px] mx-auto px-8 py-5">
          <div className="grid grid-cols-3 items-center">

            {/* Left: System Status */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2.5 px-4 py-2 bg-slate-100/50 rounded-full border border-slate-200/60 transition-all hover:bg-slate-100">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.1em]">Système Actif</span>
                <div className="w-px h-3 bg-slate-300 mx-1" />
                <span className="text-xs font-bold text-slate-700">v1.2.5</span>
              </div>
            </div>

            {/* Center: Branding XXL */}
            <div className="flex flex-col items-center group cursor-pointer">
              <div className="flex items-center gap-4 translate-y-1 transition-transform group-hover:scale-105 duration-500">
                <div className="w-14 h-14 bg-gradient-to-tr from-blue-600 via-indigo-600 to-indigo-700 rounded-2xl flex items-center justify-center shadow-xl shadow-blue-200/50 group-hover:rotate-[10deg] transition-all duration-500">
                  <Shield className="w-8 h-8 text-white stroke-[2.5px]" />
                </div>
                <h1 className="text-5xl font-[900] tracking-tighter bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 bg-clip-text text-transparent drop-shadow-sm">
                  NESSAYA
                </h1>
              </div>
              <div className="h-1 w-24 bg-gradient-to-r from-transparent via-blue-500 to-transparent mt-3 opacity-20 group-hover:opacity-100 group-hover:w-48 transition-all duration-700 rounded-full" />
            </div>

            {/* Right: Actions & Profile */}
            <div className="flex justify-end items-center gap-4">
              <button className="p-2.5 hover:bg-slate-100 rounded-xl transition-all relative group overflow-hidden">
                <Bell className="w-5 h-5 text-slate-600 group-hover:scale-110 transition-transform" />
                <span className="absolute top-2.5 right-2.5 w-2.5 h-2.5 bg-rose-500 rounded-full border-2 border-white" />
              </button>
              <div className="w-px h-8 bg-slate-200 mx-1" />
              <button className="flex items-center gap-3 p-1.5 pr-4 hover:bg-slate-100 rounded-2xl transition-all border border-transparent hover:border-slate-200 group">
                <div className="w-10 h-10 bg-slate-900 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-blue-200 transition-all">
                  <User className="w-6 h-6 text-white" />
                </div>
                <div className="flex flex-col items-start leading-none">
                  <span className="text-sm font-bold text-slate-900">Admin</span>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mt-1">Super User</span>
                </div>
              </button>
            </div>

          </div>
        </div>
      </header>

      {/* Main Content */}
      <main >
        <Tabs />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">

      </footer>
    </div>
  );
}

export default App;