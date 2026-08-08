import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getStats } from '../api/admin';
import { StatSkeleton } from '../components/Skeletons';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend,
} from 'recharts';
import { HiOutlineClipboardList, HiOutlineExclamation, HiOutlineCheck, HiOutlineClock, HiOutlineAdjustments } from 'react-icons/hi';

const COLORS = ['#0d9488', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#10b981', '#64748b'];

const PIE_COLORS = ['#0d9488', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#10b981', '#94a3b8'];

export default function DashboardPage() {
  const { data: stats, isLoading, error, refetch } = useQuery({
    queryKey: ['adminStats'],
    queryFn: getStats,
    refetchInterval: 30000, // Auto-refresh every 30s
  });

  if (isLoading) {
    return (
      <div className="section py-8 animate-fade-in">
        <h1 className="page-title mb-8">Dashboard</h1>
        <StatSkeleton count={4} />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <div className="card p-6"><div className="skeleton h-64" /></div>
          <div className="card p-6"><div className="skeleton h-64" /></div>
        </div>
      </div>
    );
  }

  if (error) {
    const isForbidden = error.response?.status === 403;

    return (
      <div className="section py-12 animate-fade-in">
        <div className="max-w-md mx-auto card p-8 text-center">
          <div className="w-14 h-14 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <HiOutlineExclamation className="w-8 h-8 text-amber-600" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">
            {isForbidden ? 'Admin Access Required' : 'Failed to Load Dashboard'}
          </h2>
          <p className="text-sm text-slate-500 mb-6">
            {isForbidden
              ? 'You are currently signed in with a Citizen account. Accessing the Dashboard analytics requires Admin privileges.'
              : (error.response?.data?.detail || 'Unable to connect to the backend server. Please make sure the backend is running.')}
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            {isForbidden ? (
              <a href="/login" className="btn-primary btn-md">
                Sign in as Admin (admin@gmail.com)
              </a>
            ) : (
              <button onClick={() => refetch()} className="btn-primary btn-md">
                Retry Loading
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      label: 'Total Complaints',
      value: stats.total_complaints,
      icon: HiOutlineClipboardList,
      color: 'bg-primary-100 text-primary-600',
    },
    {
      label: 'Open Issues',
      value: stats.open_count,
      icon: HiOutlineExclamation,
      color: 'bg-amber-100 text-amber-600',
    },
    {
      label: 'Resolved This Week',
      value: stats.resolved_this_week,
      icon: HiOutlineCheck,
      color: 'bg-emerald-100 text-emerald-600',
    },
    {
      label: 'Avg. Resolution Time',
      value: `${stats.avg_resolution_hours}h`,
      icon: HiOutlineClock,
      color: 'bg-blue-100 text-blue-600',
    },
  ];

  return (
    <div className="section py-8 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="page-title">Admin Dashboard</h1>
          <p className="page-subtitle">Real-time analytics, issue tracking, and department insights</p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/admin/complaints"
            className="inline-flex items-center gap-2 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-700 hover:to-emerald-700 text-white font-semibold px-5 py-2.5 rounded-xl shadow-sm hover:shadow-md transition-all text-sm"
          >
            <HiOutlineAdjustments className="w-5 h-5" />
            <span>Manage Complaints</span>
          </Link>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map((card, i) => (
          <div key={i} className="card p-5 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm text-slate-500">{card.label}</p>
              <div className={`w-10 h-10 rounded-xl ${card.color} flex items-center justify-center`}>
                <card.icon className="w-5 h-5" />
              </div>
            </div>
            <p className="text-3xl font-bold text-slate-900">{card.value}</p>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Category Distribution */}
        <div className="card p-6">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Complaints by Category</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={stats.category_counts} margin={{ top: 5, right: 5, left: -15, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="category" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
              <Tooltip
                contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '13px' }}
              />
              <Bar dataKey="count" fill="#0d9488" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Priority Breakdown */}
        <div className="card p-6">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Priority Breakdown</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={stats.priority_counts}
                dataKey="count"
                nameKey="priority"
                cx="50%"
                cy="50%"
                outerRadius={100}
                innerRadius={55}
                paddingAngle={4}
                label={({ priority, percent }) => `${priority} ${(percent * 100).toFixed(0)}%`}
              >
                {stats.priority_counts.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '13px' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Complaints Over Time */}
        <div className="card p-6">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Complaints Over Time (30 days)</h3>
          {stats.complaints_over_time.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={stats.complaints_over_time} margin={{ top: 5, right: 5, left: -15, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '13px' }}
                />
                <Line type="monotone" dataKey="count" stroke="#0d9488" strokeWidth={2} dot={{ fill: '#0d9488', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-400 text-sm">
              No data yet for the last 30 days
            </div>
          )}
        </div>

        {/* Status Distribution */}
        <div className="card p-6">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Status Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={stats.status_counts} layout="vertical" margin={{ top: 5, right: 5, left: 30, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis type="category" dataKey="status" tick={{ fontSize: 11, fill: '#64748b' }} width={90} />
              <Tooltip
                contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '13px' }}
              />
              <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                {stats.status_counts.map((entry, i) => {
                  const colors = { 'Open': '#94a3b8', 'Assigned': '#3b82f6', 'In Progress': '#f59e0b', 'Resolved': '#10b981' };
                  return <Cell key={i} fill={colors[entry.status] || '#94a3b8'} />;
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
