import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getComplaint } from '../api/complaints';
import { StatusBadge, PriorityBadge } from '../components/Badges';
import { HiOutlineArrowLeft, HiOutlineLocationMarker, HiOutlineClock, HiOutlinePhotograph } from 'react-icons/hi';
import { MdOutlineSmartToy } from 'react-icons/md';
import LocationViewerMap from '../components/LocationViewerMap';

const STATUS_TIMELINE = ['Open', 'Assigned', 'In Progress', 'Resolved'];

const getImageUrl = (url) => {
  if (!url) return null;
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  return `http://127.0.0.1:8000${url.startsWith('/') ? '' : '/'}${url}`;
};

export default function ComplaintDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: complaint, isLoading, error } = useQuery({
    queryKey: ['complaint', id],
    queryFn: () => getComplaint(id),
  });

  if (isLoading) {
    return (
      <div className="section py-8">
        <div className="max-w-3xl mx-auto space-y-4">
          <div className="skeleton h-8 w-48" />
          <div className="card p-6 space-y-3">
            <div className="skeleton h-4 w-full" />
            <div className="skeleton h-4 w-3/4" />
            <div className="skeleton h-4 w-1/2" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !complaint) {
    return (
      <div className="section py-8">
        <div className="card p-8 text-center max-w-lg mx-auto">
          <p className="text-red-500 mb-4">Complaint not found or you don't have permission to view it.</p>
          <button onClick={() => navigate(-1)} className="btn-primary">Go Back</button>
        </div>
      </div>
    );
  }

  const currentStepIndex = STATUS_TIMELINE.indexOf(complaint.status);

  return (
    <div className="section py-8 animate-fade-in">
      <div className="max-w-3xl mx-auto">
        {/* Back button */}
        <button onClick={() => navigate(-1)} className="btn-ghost btn-sm mb-6">
          <HiOutlineArrowLeft className="w-4 h-4 mr-1" />
          Back
        </button>

        {/* Header */}
        <div className="flex flex-wrap items-center gap-3 mb-6">
          <StatusBadge status={complaint.status} />
          <PriorityBadge priority={complaint.ai_output.priority} />
          <span className="bg-slate-100 px-3 py-0.5 rounded-full text-xs font-medium text-slate-600">
            {complaint.ai_output.category}
          </span>
          {complaint.assigned_department && (
            <span className="bg-secondary-100 px-3 py-0.5 rounded-full text-xs font-medium text-secondary-700">
              {complaint.assigned_department}
            </span>
          )}
        </div>

        {/* Description */}
        <div className="card p-6 mb-4">
          <h2 className="text-sm font-medium text-slate-500 mb-2">Description</h2>
          <p className="text-slate-800 leading-relaxed">{complaint.description}</p>
        </div>

        {/* AI Summary */}
        {complaint.ai_output.summary && (
          <div className="bg-primary-50 border border-primary-200 rounded-2xl p-5 mb-4">
            <div className="flex items-center gap-2 mb-2">
              <MdOutlineSmartToy className="text-primary-600" />
              <h3 className="text-sm font-semibold text-primary-800">AI Summary</h3>
            </div>
            <p className="text-sm text-primary-900">{complaint.ai_output.summary}</p>
          </div>
        )}

        {/* Attached Photo */}
        {complaint.image_url && (
          <div className="card p-5 mb-4">
            <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-1.5">
              <HiOutlinePhotograph className="w-4 h-4 text-primary-600" />
              Attached Photo
            </h3>
            <div className="relative group overflow-hidden rounded-xl border border-slate-200 bg-slate-50 max-w-md">
              <img
                src={getImageUrl(complaint.image_url)}
                alt="Complaint evidence"
                className="w-full max-h-72 object-cover transition-transform duration-300 group-hover:scale-105"
              />
              <a
                href={getImageUrl(complaint.image_url)}
                target="_blank"
                rel="noopener noreferrer"
                className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-semibold gap-1"
              >
                Click to view full size ↗
              </a>
            </div>

            {/* AI Image Analysis Output */}
            {complaint.image_analysis && (
              <div className="mt-4 pt-3 border-t border-slate-100 space-y-2 max-w-md">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700">
                  <MdOutlineSmartToy className="text-primary-600 w-4 h-4" />
                  <span>AI Local Image Analysis</span>
                  <span className="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full font-normal">CPU Vision</span>
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

        {/* Map & Location */}
        <div className="mb-4">
          <LocationViewerMap location={complaint.location} />
        </div>

        {/* Details Card */}
        <div className="card p-4 mb-4">
          <h3 className="text-xs font-medium text-slate-500 mb-2">
            <HiOutlineClock className="inline w-3 h-3 mr-1" />
            Submitted Date & Time
          </h3>
          <p className="text-sm text-slate-800">
            {new Date(complaint.created_at).toLocaleString()}
          </p>
        </div>

        {/* AI Confidence Details */}
        <div className="card p-5 mb-4">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">AI Classification Details</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-slate-500">Category Confidence</p>
              <div className="mt-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-500 rounded-full transition-all"
                  style={{ width: `${(complaint.ai_output.category_confidence * 100).toFixed(0)}%` }}
                />
              </div>
              <p className="text-xs text-slate-600 mt-1">
                {complaint.ai_output.category} — {(complaint.ai_output.category_confidence * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Priority Confidence</p>
              <div className="mt-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-amber-500 rounded-full transition-all"
                  style={{ width: `${(complaint.ai_output.priority_confidence * 100).toFixed(0)}%` }}
                />
              </div>
              <p className="text-xs text-slate-600 mt-1">
                {complaint.ai_output.priority} — {(complaint.ai_output.priority_confidence * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        {/* Status Timeline */}
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Status Timeline</h3>
          <div className="flex items-center justify-between">
            {STATUS_TIMELINE.map((step, i) => (
              <div key={step} className="flex items-center flex-1">
                <div className="flex flex-col items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                    i <= currentStepIndex
                      ? 'bg-primary-600 text-white'
                      : 'bg-slate-200 text-slate-400'
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
    </div>
  );
}
