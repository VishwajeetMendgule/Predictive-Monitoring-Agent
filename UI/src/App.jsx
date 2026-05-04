import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { 
  Activity, Cpu, HardDrive, ShieldAlert, LayoutDashboard, Terminal, Globe, Bot, User, Search, Calendar, Filter, Database, FileText
} from 'lucide-react';

const socket = io('http://localhost:3000');

export default function App() {
  // --- STATE ---
  const [activeView, setActiveView] = useState('live'); 
  const [dataStream, setDataStream] = useState([]);
  const [currentMetrics, setCurrentMetrics] = useState({ cpu: 0, memory: 0, network: 0 });
  const [alert, setAlert] = useState(null);

  // Log Explorer State
  const [isQuerying, setIsQuerying] = useState(false);
  const [searchDate, setSearchDate] = useState(new Date().toISOString().split('T')[0]);
  const [searchLevel, setSearchLevel] = useState('All Levels');
  const [searchComponent, setSearchComponent] = useState('');
  
  // Dual State for Hybrid View
  const [queriedMetrics, setQueriedMetrics] = useState(null);
  const [queriedLogs, setQueriedLogs] = useState(null);

  // --- SOCKET CONNECTION (Live Feed) ---
  useEffect(() => {
    socket.on('telemetry_update', (data) => {
      setCurrentMetrics({ cpu: data.cpu, memory: data.memory, network: data.network });
      setDataStream(prev => {
        const newStream = [...prev, { time: data.timestamp, cpu: data.cpu, memory: data.memory }];
        if (newStream.length > 20) newStream.shift();
        return newStream;
      });

      if (data.is_anomaly) {
        setAlert({
          predicted_cpu: data.predicted_cpu,
          predicted_memory: data.predicted_memory,
          predicted_network: data.predicted_network,
          llm: data.llm_response 
        });
      } else {
        setAlert(null);
      }
    });
    return () => socket.off('telemetry_update');
  }, []);

  // --- DUAL FETCH: HYBRID VIEW ---
  const handleFetchLogs = async (e) => {
    e.preventDefault();
    setIsQuerying(true);
    
    try {
      const queryParams = new URLSearchParams({
        date: searchDate,
        level: searchLevel,
        component: searchComponent
      });
      
      const [metricsResponse, logsResponse] = await Promise.all([
        fetch(`http://localhost:3000/api/history?date=${searchDate}`),
        fetch(`http://localhost:3000/api/logs?${queryParams}`)
      ]);

      const metricsData = await metricsResponse.json();
      const logsData = await logsResponse.json();

      setQueriedMetrics(metricsData);
      setQueriedLogs(logsData);
    } catch (error) {
      console.error("Failed to fetch hybrid data:", error);
    } finally {
      setIsQuerying(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-300 font-sans overflow-hidden selection:bg-blue-500/30">
      
      {/* --- SIDEBAR --- */}
      <div className="w-64 bg-slate-900/50 backdrop-blur-xl border-r border-slate-800/60 flex flex-col relative z-10 shrink-0">
        <div className="h-20 flex items-center px-6 border-b border-slate-800/60">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-[0_0_15px_rgba(59,130,246,0.5)] mr-3">
            <Activity className="text-white w-6 h-6" />
          </div>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 font-bold text-xl tracking-wide">
            Predictive Monitoring Agent
          </span>
        </div>
        <nav className="flex-1 px-4 py-6 space-y-2">
          <div onClick={() => setActiveView('live')} className={`flex items-center px-4 py-3 rounded-lg cursor-pointer transition-all ${activeView === 'live' ? 'bg-blue-500/10 border-l-2 border-blue-500 text-blue-400 rounded-l-none' : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'}`}>
            <LayoutDashboard className="w-5 h-5 mr-3" />
            <span className="text-sm font-medium">Live Feed</span>
          </div>
          <div onClick={() => setActiveView('explorer')} className={`flex items-center px-4 py-3 rounded-lg cursor-pointer transition-all ${activeView === 'explorer' ? 'bg-blue-500/10 border-l-2 border-blue-500 text-blue-400 rounded-l-none' : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'}`}>
            <Terminal className="w-5 h-5 mr-3" />
            <span className="text-sm font-medium">Log Explorer</span>
          </div>
        </nav>
      </div>

      {/* --- MAIN CONTENT AREA --- */}
      <div className="flex-1 flex flex-col overflow-y-auto relative bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black">
        
        {/* HEADER */}
        <header className="h-20 flex items-center justify-between px-8 border-b border-slate-800/60 bg-slate-900/30 backdrop-blur-md sticky top-0 z-20 shrink-0">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-white mr-4">
              {activeView === 'live' ? 'System Feed' : 'Forensic Explorer'}
            </h1>
            {activeView === 'live' && (
              alert ? (
                <span className="px-3 py-1 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-semibold flex items-center">
                  <span className="w-2 h-2 rounded-full bg-red-500 animate-ping mr-2"></span> Spike Detected
                </span>
              ) : (
                <span className="px-3 py-1 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 text-xs font-semibold flex items-center">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse mr-2"></span> System Stable
                </span>
              )
            )}
          </div>
          <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center cursor-pointer hover:border-slate-500 transition-all">
            <User className="w-5 h-5 text-slate-300" />
          </div>
        </header>

        <div className="p-8 max-w-7xl mx-auto w-full h-full flex flex-col">
          
          {/* ========================================== */}
          {/*                LIVE FEED VIEW                */}
          {/* ========================================== */}
          {activeView === 'live' && (
            <div className="space-y-6">
              {/* STAT CARDS */}
              <div className="grid grid-cols-3 gap-6">
                <div className="bg-slate-900/40 backdrop-blur-md border border-slate-800/60 rounded-2xl p-6 relative overflow-hidden group">
                  <Cpu className="absolute top-4 right-4 w-16 h-16 text-blue-500 opacity-10 group-hover:opacity-20 transition-opacity" />
                  <span className="text-slate-400 text-sm font-medium">Live CPU Usage</span>
                  <div className="mt-3 text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-white to-blue-200">
                    {currentMetrics.cpu}%
                  </div>
                </div>

                <div className={`backdrop-blur-md border rounded-2xl p-6 relative overflow-hidden group transition-colors duration-500 ${alert ? 'bg-red-950/20 border-red-500/30' : 'bg-slate-900/40 border-slate-800/60'}`}>
                  <HardDrive className={`absolute top-4 right-4 w-16 h-16 opacity-10 group-hover:opacity-20 transition-opacity ${alert ? 'text-red-500' : 'text-yellow-500'}`} />
                  <span className={`text-sm font-medium ${alert ? 'text-red-400' : 'text-slate-400'}`}>Live Memory Usage</span>
                  <div className={`mt-3 text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-br ${alert ? 'from-red-400 to-orange-200' : 'from-white to-yellow-200'}`}>
                    {currentMetrics.memory}%
                  </div>
                </div>

                <div className="bg-slate-900/40 backdrop-blur-md border border-slate-800/60 rounded-2xl p-6 relative overflow-hidden group">
                  <Globe className="absolute top-4 right-4 w-16 h-16 text-emerald-500 opacity-10 group-hover:opacity-20 transition-opacity" />
                  <span className="text-slate-400 text-sm font-medium">Network I/O</span>
                  <div className="mt-3 text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-white to-emerald-200">
                    {currentMetrics.network} <span className="text-lg text-slate-500">mb/s</span>
                  </div>
                </div>
              </div>

              {/* CHART & AI DIAGNOSTICS */}
              <div className="grid grid-cols-3 gap-6 h-[480px]">
                
                {/* Live Chart */}
                <div className="col-span-2 bg-slate-900/40 backdrop-blur-md border border-slate-800/60 rounded-2xl p-6 flex flex-col">
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="text-white font-semibold flex items-center text-lg">
                      <Activity className="w-5 h-5 mr-2 text-blue-400" /> Real-Time Data
                    </h3>
                    <div className="flex space-x-4 text-xs font-medium text-slate-400">
                      <span className="flex items-center"><div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div> CPU</span>
                      <span className="flex items-center"><div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div> Memory</span>
                    </div>
                  </div>
                  
                  <div className="flex-1 w-full relative">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={dataStream}>
                        <defs>
                          <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                          </linearGradient>
                          <linearGradient id="colorMem" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                            <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                        <XAxis dataKey="time" stroke="#64748b" tickLine={false} axisLine={false} dy={10} />
                        <YAxis stroke="#64748b" tickLine={false} axisLine={false} domain={[0, 100]} dx={-10} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }}
                          itemStyle={{ color: '#f8fafc' }}
                        />
                        <Area type="monotone" dataKey="cpu" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCpu)" strokeWidth={3} isAnimationActive={false} />
                        <Area type="monotone" dataKey="memory" stroke="#ef4444" fillOpacity={1} fill="url(#colorMem)" strokeWidth={3} isAnimationActive={false} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* AI Alert Panel */}
                <div className="col-span-1 bg-slate-900/40 backdrop-blur-md border border-slate-800/60 rounded-2xl p-6 flex flex-col overflow-y-auto">
                  <h3 className="text-white font-semibold mb-4 flex items-center text-lg shrink-0">
                    <ShieldAlert className="w-5 h-5 mr-2 text-indigo-400" /> AI Diagnostics
                  </h3>
                  
                  {alert ? (
                    <div className="flex flex-col space-y-4 animate-in slide-in-from-right-4 fade-in duration-300">
                      <div className="bg-red-950/40 border border-red-500/30 rounded-xl p-4 relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-24 h-24 bg-red-500/10 blur-2xl rounded-full translate-x-1/2 -translate-y-1/2"></div>
                        <span className="bg-red-500/20 border border-red-500/30 text-red-400 text-[10px] uppercase tracking-wider font-bold px-2 py-1 rounded inline-flex items-center mb-3">
                          <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping mr-1.5"></span> Critical Alert
                        </span>
                        <h4 className="text-white font-semibold text-sm mb-3">Predicted Values (Next 5m)</h4>
                        <div className="grid grid-cols-3 gap-2 text-center">
                          <div className="bg-black/40 py-2 rounded-lg border border-white/5">
                            <div className="text-[10px] text-slate-400 uppercase tracking-wide">CPU</div>
                            <div className="text-red-400 font-bold">{alert.predicted_cpu}%</div>
                          </div>
                          <div className="bg-black/40 py-2 rounded-lg border border-white/5">
                            <div className="text-[10px] text-slate-400 uppercase tracking-wide">Mem</div>
                            <div className="text-red-400 font-bold">{alert.predicted_memory}%</div>
                          </div>
                          <div className="bg-black/40 py-2 rounded-lg border border-white/5">
                            <div className="text-[10px] text-slate-400 uppercase tracking-wide">Net</div>
                            <div className="text-red-400 font-bold">{alert.predicted_network}</div>
                          </div>
                        </div>
                      </div>

                      {alert.llm && (
                        <div className="bg-indigo-950/30 border border-indigo-500/30 rounded-xl p-4">
                          <h4 className="text-indigo-300 font-semibold text-sm mb-3 flex items-center">
                            <Bot className="w-4 h-4 mr-1.5" /> LLM Root Cause Analysis
                          </h4>
                          <div className="space-y-2 text-sm">
                            <p className="text-slate-300">
                              <span className="text-slate-500 text-xs uppercase block mb-0.5">Issue Type</span>
                              {alert.llm.failure_type}
                            </p>
                            <p className="text-slate-300">
                              <span className="text-slate-500 text-xs uppercase block mb-0.5">Root Cause</span>
                              {alert.llm.RootCause}
                            </p>
                            <div className="pt-2 mt-2 border-t border-indigo-500/20">
                              <span className="text-emerald-500 text-xs uppercase font-bold block mb-1">Recommended Action</span>
                              <p className="text-emerald-400 text-sm">{alert.llm.RecommendedAction}</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-slate-500 opacity-60">
                      <ShieldAlert className="w-16 h-16 mb-4 text-slate-600" />
                      <p className="text-sm font-medium">All systems stable.</p>
                      <p className="text-xs text-slate-600 mt-1">Awaiting system spikes...</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ========================================== */}
          {/*          HYBRID LOG EXPLORER VIEW            */}
          {/* ========================================== */}
          {activeView === 'explorer' && (
            <div className="space-y-6 flex-1 flex flex-col animate-in fade-in duration-500">
              
              {/* Query Panel */}
              <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800/60 rounded-2xl p-6 shrink-0 shadow-lg">
                <form onSubmit={handleFetchLogs} className="flex items-end gap-4">
                  <div className="flex-1">
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center">
                      <Calendar className="w-3.5 h-3.5 mr-1" /> Target Date
                    </label>
                    <input type="date" value={searchDate} onChange={(e) => setSearchDate(e.target.value)} className="w-full bg-slate-950/50 border border-slate-700 text-slate-200 text-sm rounded-lg p-2.5 outline-none [color-scheme:dark]" />
                  </div>
                  <div className="flex-1">
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center">
                      <Filter className="w-3.5 h-3.5 mr-1" /> Severity Level
                    </label>
                    <select value={searchLevel} onChange={(e) => setSearchLevel(e.target.value)} className="w-full bg-slate-950/50 border border-slate-700 text-slate-200 text-sm rounded-lg p-2.5 outline-none">
                      <option>All Levels</option>
                      <option>ERROR & CRITICAL</option>
                      <option>WARNING</option>
                      <option>INFO</option>
                      <option>DEBUG</option>
                    </select>
                  </div>
                  <div className="flex-2 w-1/3">
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center">
                      <Search className="w-3.5 h-3.5 mr-1" /> Search Component/Message
                    </label>
                    <input type="text" value={searchComponent} onChange={(e) => setSearchComponent(e.target.value)} placeholder="e.g. JVM, memory, timeout..." className="w-full bg-slate-950/50 border border-slate-700 text-slate-200 text-sm rounded-lg p-2.5 outline-none placeholder-slate-600" />
                  </div>
                  <button type="submit" disabled={isQuerying} className="bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg text-sm px-6 py-2.5 text-center transition-colors shadow-lg shadow-blue-500/20 disabled:opacity-50">
                    {isQuerying ? 'Scanning Systems...' : 'Run Forensic Query'}
                  </button>
                </form>
              </div>

              {/* Data Table Area - SPLIT INTO TWO PANELS */}
              {!queriedMetrics && !queriedLogs ? (
                // EMPTY STATE
                <div className="flex-1 bg-slate-900/40 backdrop-blur-md border border-slate-800/60 rounded-2xl flex flex-col items-center justify-center text-slate-500 p-8 text-center min-h-[400px]">
                  <div className="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 border border-slate-700/50">
                    <Database className="w-10 h-10 text-slate-400" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-300 mb-2">Hybrid Forensic Explorer</h3>
                  <p className="max-w-md text-sm leading-relaxed">
                    Select your parameters to cross-reference server metrics (SQLite) with application behavior (Text Logs).
                  </p>
                </div>
              ) : (
                // RESULTS STATE - SIDE BY SIDE
                <div className="flex-1 grid grid-cols-2 gap-6 min-h-[400px]">
                  
                  {/* LEFT PANEL: SQLite Server Metrics */}
                  <div className="bg-slate-900/40 backdrop-blur-md border border-slate-800/60 rounded-2xl overflow-hidden flex flex-col">
                    <div className="px-6 py-4 border-b border-slate-800/60 flex items-center bg-slate-800/30">
                        <Activity className="w-4 h-4 mr-2 text-blue-400" />
                        <h3 className="text-sm font-bold text-white uppercase tracking-wider">Top Spikes (Metrics DB)</h3>
                    </div>
                    <div className="flex-1 overflow-auto">
                        <table className="w-full text-sm text-left text-slate-400">
                        <thead className="text-[10px] text-slate-500 uppercase bg-slate-950/50 sticky top-0">
                            <tr>
                                <th className="px-4 py-3 font-semibold">Time</th>
                                <th className="px-4 py-3 font-semibold">CPU</th>
                                <th className="px-4 py-3 font-semibold">Mem</th>
                                <th className="px-4 py-3 font-semibold">Net (mb/s)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {queriedMetrics?.length === 0 && <tr><td colSpan="4" className="text-center py-6">No metric data found.</td></tr>}
                            {queriedMetrics?.map((log, index) => (
                            <tr key={index} className="border-b border-slate-800/30 hover:bg-slate-800/30">
                                <td className="px-4 py-3 whitespace-nowrap font-mono text-xs">{log.timestamp?.split(' ')[1] || log.timestamp}</td>
                                <td className="px-4 py-3">
                                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${log.cpu > 70 ? 'bg-red-500/20 text-red-400' : 'text-slate-300'}`}>{log.cpu}%</span>
                                </td>
                                <td className="px-4 py-3">{log.memory}%</td>
                                <td className="px-4 py-3">{log.network}</td>
                            </tr>
                            ))}
                        </tbody>
                        </table>
                    </div>
                  </div>

                  {/* RIGHT PANEL: Application Logs */}
                  <div className="bg-slate-900/40 backdrop-blur-md border border-slate-800/60 rounded-2xl overflow-hidden flex flex-col">
                    <div className="px-6 py-4 border-b border-slate-800/60 flex items-center bg-slate-800/30">
                        <FileText className="w-4 h-4 mr-2 text-indigo-400" />
                        <h3 className="text-sm font-bold text-white uppercase tracking-wider">System Logs (Text File)</h3>
                    </div>
                    <div className="flex-1 overflow-auto">
                        <table className="w-full text-sm text-left text-slate-400">
                        <thead className="text-[10px] text-slate-500 uppercase bg-slate-950/50 sticky top-0">
                            <tr>
                                <th className="px-4 py-3 font-semibold">Time</th>
                                <th className="px-4 py-3 font-semibold">Component</th>
                                <th className="px-4 py-3 font-semibold w-1/2">Message</th>
                            </tr>
                        </thead>
                        <tbody>
                            {queriedLogs?.length === 0 && <tr><td colSpan="3" className="text-center py-6">No matching logs found.</td></tr>}
                            {queriedLogs?.map((log, index) => (
                            <tr key={index} className="border-b border-slate-800/30 hover:bg-slate-800/30">
                                <td className="px-4 py-3 whitespace-nowrap font-mono text-xs flex flex-col">
                                    <span className={`text-[9px] font-bold uppercase mb-0.5 ${log.level === 'ERROR' || log.level === 'CRITICAL' ? 'text-red-400' : log.level === 'WARN' ? 'text-yellow-400' : 'text-blue-400'}`}>{log.level}</span>
                                    {log.time}
                                </td>
                                <td className="px-4 py-3 font-medium text-slate-300">{log.component}</td>
                                <td className="px-4 py-3 text-xs">{log.message}</td>
                            </tr>
                            ))}
                        </tbody>
                        </table>
                    </div>
                  </div>

                </div>
              )}

            </div>
          )}

        </div>
      </div>
    </div>
  );
}