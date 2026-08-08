import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getComplaint, updateComplaint } from '../api/complaints';
import { StatusBadge, PriorityBadge } from '../components/Badges';
import toast from 'react-hot-toast';
import { HiOutlineArrowLeft, HiOutlineLocationMarker, HiOutlineClock, HiOutlineUser, HiOutlinePhotograph } from 'react-icons/hi';
import { MdOutlineSmartToy } from 'react-icons/md';
import { useState } from 'react';
import LocationViewerMap from '../components/LocationViewerMap';

const STATUSES = ['Open', 'Assigned', 'In Progress', 'Resolved'];
const DEPARTMENTS = ['Roads', 'Water', 'Waste', 'Electricity', 'Drainage', 'Safety', 'Other'];
const STATUS_TIMELINE = ['Open', 'Assigned', 'In Progress', 'Resolved'];

const getImageUrl = (url) => {
  if (!url) return null;
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  return `http://127.0.0.1:8000${url.startsWith('/') ? '' : '/'}${url}`;
};

export default function AdminComplaintDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: complaint, isLoading, error } = useQuery({
    queryKey: ['complaint', id],
    queryFn: () => getComplaint(id),
  });

  const [editStatus, setEditStatus] = useState('');
  const [editDept, setEditDept] = useState('');

  const updateMutation = useMutation({
    mutationFn: (data) => updateComplaint(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries(['complaint', id]);
      queryClient.invalidateQueries(['adminComplaints']);
      toast.success('Complaint updated successfully');
    },
    onError: () => toast.error('Update failed'),
  });

  // Sync edit state when complaint loads
  if (complaint && !editStatus) {
    setTimeout(() => {
      setEditStatus(complaint.status);
      setEditDept(complaint.assigned_department || '');
    }, 0);
  }

  if (isLoading) {
    return (
      <div className="section py-8">
        <div className="max-w-4xl mx-auto space-y-4">
          <div className="skeleton h-8 w-48" />
          <div className="card p-6 space-y-3">
            <div className="skeleton h-4 w-full" />
            <div className="skeleton h-4 w-3/4" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !complaint) {
    return (
      <div className="section py-8">
        <div className="card p-8 text-center max-w-lg mx-auto">
          <p className="text-red-500 mb-4">Complaint not found.</p>
          <button onClick={() => navigate(-1)} className="btn-primary">Go Back</button>
        </div>
      </div>
    );
  }

  const currentStepIndex = STATUS_TIMELINE.indexOf(complaint.status);

  const handleUpdate = () => {
    const data = {};
    if (editStatus !== complaint.status) data.status = editStatus;
    if (editDept !== (complaint.assigned_department || '')) data.assigned_department = editDept || null;
    if (Object.keys(data).length > 0) {
      updateMutation.mutate(data);
    }
  };

  return (
    <div className="section py-8 animate-fade-in">
      <div className="max-w-4xl mx-auto">
        <button onClick={() => navigate(-1)} className="btn-ghost btn-sm mb-6">
          <HiOutlineArrowLeft className="w-4 h-4 mr-1" />
          Back to Management
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-4">
            {/* Header */}
            <div className="flex flex-wrap items-center gap-3">
              <StatusBadge status={complaint.status} />
              <PriorityBadge priority={complaint.ai_output.priority} />
              <span className="bg-slate-100 px-3 py-0.5 rounded-full text-xs font-medium text-slate-600">
                {complaint.ai_output.category}
              </span>
            </div>

            {/* Description */}
            <div className="card p-6">
              <h2 className="text-sm font-medium text-slate-500 mb-2">Complaint Description</h2>
              <p className="text-slate-800 leading-relaxed">{complaint.description}</p>
            </div>

            {/* AI Summary */}
            {complaint.ai_output.summary && (
              <div className="bg-primary-50 border border-primary-200 rounded-2xl p-5">
                <div className="flex items-center gap-2 mb-2">
                  <MdOutlineSmartToy className="text-primary-600" />
                  <h3 className="text-sm font-semibold text-primary-800">AI Summary for Service Team</h3>
                </div>
                <p className="text-sm text-primary-900">{complaint.ai_output.summary}</p>
              </div>
            )}

            {/* Attached Photo */}
            {complaint.image_url && (
              <div className="card p-5">
                <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-1.5">
                  <HiOutlinePhotograph className="w-4 h-4 text-primary-600" />
                  Attached Photo Evidence
                </h3>
                <div className="relative group overflow-hidden rounded-xl border border-slate-200 bg-slate-50 max-w-md">
                  <img
                    src={getImageUrl(complaint.image_url)}
                    alt="Complaint evidence"
                    className="w-full max-h-80 object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                  <a
                    href={getImageUrl(complaint.image_url)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-semibold gap-1"
                  >
                    Click to view full resolution ↗
                  </a>
                </div>

                {/* Local Computer Vision Analysis */}
                {complaint.image_analysis && (
                  <div className="mt-4 pt-3 border-t border-slate-100 space-y-2 max-w-md">
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700">
                      <MdOutlineSmartToy className="text-primary-600 w-4 h-4" />
                      <span>AI Local Image Analysis</span>
                      <span className="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full font-normal">Local CV</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="bg-slate-50 p-2 rounded-lg border border-slate-100">
                        <span className="text-slate-400 block text-[10px]">Photo Quality</span>
                        <span className="font-medium text-slate-800">{complaint.image_analysis.clarity_label}</span>
                      </div>
                      <div className="bg-slate-50 p-2 rounded-lg border border-slate-100">
                        <span className="text-slate-400 block text-[10px]">Lighting</span>
                        <span className="font-medium text-slate-800">{complaint.image_analysis.lighting}</span>
                      </div>
                    </div>
                    {complaint.image_analysis.detected_tags?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {complaint.image_analysis.detected_tags.map((tag, idx) => (
                          <span key={idx} className="bg-primary-50 text-primary-700 text-[10px] font-medium px-2 py-0.5 rounded-md border border-primary-100">
                            🔍 {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Location & Map */}
            <LocationViewerMap location={complaint.location} />

            {/* Submitted Date */}
            <div className="card p-4">
              <h3 className="text-xs font-medium text-slate-500 mb-2">
                <HiOutlineClock className="inline w-3 h-3 mr-1" />
                Submitted Date & Time
              </h3>
              <p className="text-sm text-slate-800">{new Date(complaint.created_at).toLocaleString()}</p>
            </div>

            {/* AI Classification */}
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-slate-700 mb-3">AI Classification Details</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-slate-500">Category</p>
                  <div className="mt-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-primary-500 rounded-full" style={{ width: `${(complaint.ai_output.category_confidence * 100)}%` }} />
                  </div>
                  <p className="text-xs text-slate-600 mt-1">{complaint.ai_output.category} — {(complaint.ai_output.category_confidence * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Priority</p>
                  <div className="mt-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-amber-500 rounded-full" style={{ width: `${(complaint.ai_output.priority_confidence * 100)}%` }} />
                  </div>
                  <p className="text-xs text-slate-600 mt-1">{complaint.ai_output.priority} — {(complaint.ai_output.priority_confidence * 100).toFixed(1)}%</p>
                </div>
              </div>
              {complaint.citizen_confirmed_category && (
                <div className="mt-3 p-2 bg-emerald-50 rounded-lg">
                  <p className="text-xs text-emerald-700">
                    <HiOutlineUser className="inline w-3 h-3 mr-1" />
                    Citizen confirmed category: <strong>{complaint.citizen_confirmed_category}</strong>
                  </p>
                </div>
              )}
            </div>

            {/* Status Timeline */}
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-slate-700 mb-4">Status Timeline</h3>
              <div className="flex items-center justify-between">
                {STATUS_TIMELINE.map((step, i) => (
                  <div key={step} className="flex items-center flex-1">
                    <div className="flex flex-col items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                        i <= currentStepIndex ? 'bg-primary-600 text-white' : 'bg-slate-200 text-slate-400'
                      }`}>
                        {i < currentStepIndex ? '✓' : i + 1}
                      </div>
                      <span className={`text-xs mt-1 ${i <= currentStepIndex ? 'text-primary-600 font-medium' : 'text-slate-400'}`}>
                        {step}
                      </span>
                    </div>
                    {i < STATUS_TIMELINE.length - 1 && (
                      <div className={`flex-1 h-0.5 mx-1 ${i < currentStepIndex ? 'bg-primary-400' : 'bg-slate-200'}`} />
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Admin Actions Sidebar */}
          <div className="lg:col-span-1">
            <div className="card p-5 sticky top-20 space-y-4">
              <h3 className="text-sm font-semibold text-slate-700">Manage Complaint</h3>

              <div>
                <label htmlFor="admin-status" className="label">Update Status</label>
                <select
                  id="admin-status"
                  value={editStatus}
                  onChange={(e) => setEditStatus(e.target.value)}
                  className="input text-sm"
                >
                  {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>

              <div>
                <label htmlFor="admin-department" className="label">Assign Department</label>
                <select
                  id="admin-department"
                  value={editDept}
                  onChange={(e) => setEditDept(e.target.value)}
                  className="input text-sm"
                >
                  <option value="">Unassigned</option>
                  {DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>

              <button
                onClick={handleUpdate}
                disabled={updateMutation.isPending}
                className="btn-primary w-full"
              >
                {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
              </button>

              <div className="pt-3 border-t border-slate-100">
                <p className="text-xs text-slate-400">
                  Last updated: {new Date(complaint.updated_at).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
