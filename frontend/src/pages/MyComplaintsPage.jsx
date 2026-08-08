import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getComplaints } from '../api/complaints';
import { StatusBadge, PriorityBadge } from '../components/Badges';
import { CardSkeleton } from '../components/Skeletons';
import EmptyState from '../components/EmptyState';
import { HiOutlinePlus, HiOutlineSearch, HiOutlineFilter } from 'react-icons/hi';

const STATUS_OPTIONS = ['All', 'Open', 'Assigned', 'In Progress', 'Resolved'];

export default function MyComplaintsPage() {
  const [statusFilter, setStatusFilter] = useState('All');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);

  const params = { page, page_size: 12 };
  if (statusFilter !== 'All') params.status = statusFilter;
  if (search.trim()) params.search = search.trim();

  const { data, isLoading, error } = useQuery({
    queryKey: ['myComplaints', statusFilter, search, page],
    queryFn: () => getComplaints(params),
    keepPreviousData: true,
  });

  const complaints = data?.complaints || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / 12);

  return (
    <div className="section py-8 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="page-title">My Complaints</h1>
          <p className="page-subtitle">{total} complaint{total !== 1 ? 's' : ''} total</p>
        </div>
        <Link to="/complaints/new" className="btn-primary">
          <HiOutlinePlus className="w-4 h-4 mr-2" />
          New Complaint
        </Link>
      </div>

      {/* Filters */}
      <div className="card p-4 mb-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <HiOutlineSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              id="search-complaints"
              type="text"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="input pl-10 text-sm"
              placeholder="Search complaints..."
            />
          </div>
          <div className="flex gap-1 overflow-x-auto pb-1">
            {STATUS_OPTIONS.map(s => (
              <button
                key={s}
                onClick={() => { setStatusFilter(s); setPage(1); }}
                className={`px-3 py-2 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
                  statusFilter === s
                    ? 'bg-primary-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <CardSkeleton count={6} />
      ) : error ? (
        <div className="card p-8 text-center">
          <p className="text-red-500">Failed to load complaints. Please try again.</p>
        </div>
      ) : complaints.length === 0 ? (
        <EmptyState
          title={search || statusFilter !== 'All' ? 'No matching complaints' : 'No complaints yet'}
          message={search || statusFilter !== 'All' ? 'Try adjusting your filters.' : 'Report your first civic issue to get started.'}
          action={
            !search && statusFilter === 'All' && (
              <Link to="/complaints/new" className="btn-primary">Report an Issue</Link>
            )
          }
        />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {complaints.map((c) => (
              <Link key={c.id} to={`/complaints/${c.id}`} className="card-hover p-5 block group">
                <div className="flex items-start justify-between mb-3">
                  <StatusBadge status={c.status} />
                  <PriorityBadge priority={c.ai_output.priority} />
                </div>
                <p className="text-sm text-slate-800 line-clamp-2 mb-3 group-hover:text-primary-700 transition-colors">
                  {c.description}
                </p>
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="bg-slate-100 px-2 py-0.5 rounded-full text-slate-600 font-medium">
                    {c.ai_output.category}
                  </span>
                  <span>{new Date(c.created_at).toLocaleDateString()}</span>
                </div>
                {c.location?.text && (
                  <p className="text-xs text-slate-400 mt-2 truncate">📍 {c.location.text}</p>
                )}
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn-ghost btn-sm"
              >
                Previous
              </button>
              <span className="text-sm text-slate-500">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="btn-ghost btn-sm"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
