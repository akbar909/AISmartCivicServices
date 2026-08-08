import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getComplaints, updateComplaint, deleteComplaint } from '../api/complaints';
import { StatusBadge, PriorityBadge } from '../components/Badges';
import { TableSkeleton } from '../components/Skeletons';
import EmptyState from '../components/EmptyState';
import toast from 'react-hot-toast';
import { HiOutlineSearch, HiOutlineTrash, HiOutlineEye } from 'react-icons/hi';

const CATEGORIES = ['All', 'Road', 'Water', 'Waste', 'Electricity', 'Drainage', 'Safety', 'Other'];
const PRIORITIES = ['All', 'Critical', 'High', 'Medium', 'Low'];
const STATUSES = ['All', 'Open', 'Assigned', 'In Progress', 'Resolved'];
const DEPARTMENTS = ['Roads', 'Water', 'Waste', 'Electricity', 'Drainage', 'Safety', 'Other'];

export default function ComplaintsManagementPage() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({
    category: 'All', priority: 'All', status: 'All', search: '', page: 1,
  });

  const params = { page: filters.page, page_size: 15 };
  if (filters.category !== 'All') params.category = filters.category;
  if (filters.priority !== 'All') params.priority = filters.priority;
  if (filters.status !== 'All') params.status = filters.status;
  if (filters.search.trim()) params.search = filters.search.trim();

  const { data, isLoading } = useQuery({
    queryKey: ['adminComplaints', filters],
    queryFn: () => getComplaints(params),
    keepPreviousData: true,
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => updateComplaint(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['adminComplaints']);
      toast.success('Complaint updated');
    },
    onError: () => toast.error('Update failed'),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => deleteComplaint(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['adminComplaints']);
      toast.success('Complaint deleted');
    },
    onError: () => toast.error('Delete failed'),
  });

  const complaints = data?.complaints || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / 15);

  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  };

  return (
    <div className="section py-8 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Complaints Management</h1>
        <p className="page-subtitle">{total} total complaints</p>
      </div>

      {/* Filters */}
      <div className="card p-4 mb-6 space-y-3">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <HiOutlineSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              id="admin-search"
              type="text"
              value={filters.search}
              onChange={(e) => updateFilter('search', e.target.value)}
              className="input pl-10 text-sm"
              placeholder="Search complaints..."
            />
          </div>
          <select
            value={filters.category}
            onChange={(e) => updateFilter('category', e.target.value)}
            className="input text-sm w-full sm:w-40"
          >
            {CATEGORIES.map(c => <option key={c} value={c}>{c === 'All' ? 'All Categories' : c}</option>)}
          </select>
          <select
            value={filters.priority}
            onChange={(e) => updateFilter('priority', e.target.value)}
            className="input text-sm w-full sm:w-36"
          >
            {PRIORITIES.map(p => <option key={p} value={p}>{p === 'All' ? 'All Priorities' : p}</option>)}
          </select>
          <select
            value={filters.status}
            onChange={(e) => updateFilter('status', e.target.value)}
            className="input text-sm w-full sm:w-36"
          >
            {STATUSES.map(s => <option key={s} value={s}>{s === 'All' ? 'All Statuses' : s}</option>)}
          </select>
        </div>
      </div>

      {/* Table */}
      {isLoading ? (
        <TableSkeleton rows={8} />
      ) : complaints.length === 0 ? (
        <EmptyState title="No complaints found" message="Try adjusting your filters." />
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Description</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Category</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Priority</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Department</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Date</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody>
                {complaints.map((c) => (
                  <tr key={c.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 max-w-[200px]">
                      <p className="truncate text-slate-800">{c.description}</p>
                      <p className="text-xs text-slate-400 truncate">📍 {c.location.text}</p>
                    </td>
                    <td className="px-4 py-3">
                      <span className="bg-slate-100 px-2 py-0.5 rounded-full text-xs font-medium text-slate-600">
                        {c.ai_output.category}
                      </span>
                    </td>
                    <td className="px-4 py-3"><PriorityBadge priority={c.ai_output.priority} /></td>
                    <td className="px-4 py-3">
                      <select
                        value={c.status}
                        onChange={(e) => updateMutation.mutate({ id: c.id, data: { status: e.target.value } })}
                        className="text-xs border border-slate-200 rounded-lg px-2 py-1 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      >
                        {STATUSES.filter(s => s !== 'All').map(s => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <select
                        value={c.assigned_department || ''}
                        onChange={(e) => updateMutation.mutate({ id: c.id, data: { assigned_department: e.target.value } })}
                        className="text-xs border border-slate-200 rounded-lg px-2 py-1 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      >
                        <option value="">Unassigned</option>
                        {DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
                      </select>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500 whitespace-nowrap">
                      {new Date(c.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1">
                        <Link
                          to={`/admin/complaints/${c.id}`}
                          className="p-1.5 rounded-lg hover:bg-primary-50 text-primary-600 transition-colors"
                          title="View details"
                        >
                          <HiOutlineEye className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={() => {
                            if (window.confirm('Delete this complaint?')) {
                              deleteMutation.mutate(c.id);
                            }
                          }}
                          className="p-1.5 rounded-lg hover:bg-red-50 text-red-500 transition-colors"
                          title="Delete"
                        >
                          <HiOutlineTrash className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-slate-100">
              <p className="text-xs text-slate-500">
                Showing {(filters.page - 1) * 15 + 1}–{Math.min(filters.page * 15, total)} of {total}
              </p>
              <div className="flex gap-1">
                <button
                  onClick={() => setFilters(p => ({ ...p, page: Math.max(1, p.page - 1) }))}
                  disabled={filters.page === 1}
                  className="btn-ghost btn-sm"
                >
                  Previous
                </button>
                <button
                  onClick={() => setFilters(p => ({ ...p, page: Math.min(totalPages, p.page + 1) }))}
                  disabled={filters.page === totalPages}
                  className="btn-ghost btn-sm"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
