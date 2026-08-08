import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { createComplaint, uploadImage } from '../api/complaints';
import { suggestCategory, sendChatMessage } from '../api/chatbot';
import toast from 'react-hot-toast';
import { HiOutlinePaperAirplane, HiOutlinePhotograph, HiOutlineLocationMarker, HiOutlineX, HiOutlineCheck } from 'react-icons/hi';
import { MdOutlineSmartToy } from 'react-icons/md';
import { PriorityBadge } from '../components/Badges';

import LocationPickerMap from '../components/LocationPickerMap';

const CATEGORIES = ['Road', 'Water', 'Waste', 'Electricity', 'Drainage', 'Safety', 'Other'];

export default function NewComplaintPage() {
  const navigate = useNavigate();
  const [description, setDescription] = useState('');
  const [locationData, setLocationData] = useState({ text: '', latitude: null, longitude: null });
  const [imagePreview, setImagePreview] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  // AI suggestion state
  const [suggestion, setSuggestion] = useState(null);
  const [confirmedCategory, setConfirmedCategory] = useState(null);
  const [suggestLoading, setSuggestLoading] = useState(false);
  const suggestTimer = useRef(null);

  // Formatted message content renderer
  const renderFormattedContent = (content) => {
    if (!content) return null;
    const lines = content.split('\n');
    return lines.map((line, idx) => {
      const parts = line.split(/(\*\*.*?\*\*)/g);
      const formattedParts = parts.map((part, pIdx) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={pIdx} className="font-semibold text-slate-900">{part.slice(2, -2)}</strong>;
        }
        return part;
      });

      return (
        <span key={idx} className="block min-h-[1.25rem]">
          {formattedParts}
        </span>
      );
    });
  };

  // Chatbot state
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! I'm your civic services assistant. Describe the issue you're facing or ask me any questions, and I'll help you file an effective complaint."
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef(null);

  // Submission result
  const [result, setResult] = useState(null);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Debounced category suggestion as user types
  const handleDescriptionChange = useCallback((e) => {
    const text = e.target.value;
    setDescription(text);

    // Clear description error immediately when 10+ characters are entered
    if (text.trim().length >= 10) {
      setErrors((prev) => {
        if (!prev.description) return prev;
        const copy = { ...prev };
        delete copy.description;
        return copy;
      });
    }

    // Clear previous timer
    if (suggestTimer.current) clearTimeout(suggestTimer.current);

    // Suggest category after user pauses typing (debounce 800ms)
    if (text.length >= 15) {
      setSuggestLoading(true);
      suggestTimer.current = setTimeout(async () => {
        try {
          const data = await suggestCategory(text);
          setSuggestion(data);
        } catch {
          // Non-critical — don't block the form
        } finally {
          setSuggestLoading(false);
        }
      }, 800);
    } else {
      setSuggestion(null);
      setSuggestLoading(false);
    }
  }, []);

  const handleLocationChange = (e) => {
    const text = e.target.value;
    setLocation(text);

    // Clear location error immediately when location is filled
    if (text.trim().length > 0) {
      setErrors((prev) => {
        if (!prev.location) return prev;
        const copy = { ...prev };
        delete copy.location;
        return copy;
      });
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onload = (ev) => setImagePreview(ev.target.result);
      reader.readAsDataURL(file);

      // Clear image error immediately when a new file is picked
      setErrors((prev) => {
        if (!prev.image) return prev;
        const copy = { ...prev };
        delete copy.image;
        return copy;
      });
    }
  };

  const handleChatSend = async () => {
    if (!chatInput.trim() || chatLoading) return;

    const userMessage = chatInput.trim();
    setChatInput('');
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatLoading(true);

    try {
      const history = chatMessages.map(m => ({ role: m.role, content: m.content }));
      const data = await sendChatMessage(userMessage, history);
      setChatMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
    } catch {
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I\'m having trouble connecting. Please try again.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  const validate = () => {
    const e = {};
    if (!description || description.trim().length < 10) e.description = 'Please provide at least 10 characters describing the issue';
    if (!locationData.text || !locationData.text.trim()) e.location = 'Location is required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      let uploadedUrl = null;
      if (imageFile) {
        try {
          const uploadRes = await uploadImage(imageFile);
          uploadedUrl = uploadRes.image_url;
        } catch (imgErr) {
          const detailMsg = imgErr.response?.data?.detail || 'Failed to upload photo';
          setErrors((prev) => ({
            ...prev,
            image: detailMsg,
          }));
          setLoading(false);
          return;
        }
      }

      const data = await createComplaint({
        description: description.trim(),
        location: {
          text: locationData.text.trim(),
          latitude: locationData.latitude,
          longitude: locationData.longitude,
        },
        citizen_confirmed_category: confirmedCategory,
        image_url: uploadedUrl,
      });
      setResult(data);
      toast.success('Complaint submitted successfully!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit complaint');
    } finally {
      setLoading(false);
    }
  };

  // Success screen
  if (result) {
    return (
      <div className="section py-12 animate-fade-in">
        <div className="max-w-2xl mx-auto">
          <div className="card p-8 text-center">
            <div className="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <HiOutlineCheck className="w-8 h-8 text-emerald-600" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Complaint Submitted!</h2>
            <p className="text-slate-500 mb-6">Your complaint has been classified and submitted. Here's what our AI determined:</p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <div className="bg-slate-50 rounded-xl p-4">
                <p className="text-xs text-slate-500 mb-1">Category</p>
                <p className="font-semibold text-slate-900">{result.ai_output.category}</p>
                <p className="text-xs text-slate-400">{(result.ai_output.category_confidence * 100).toFixed(0)}% confidence</p>
              </div>
              <div className="bg-slate-50 rounded-xl p-4">
                <p className="text-xs text-slate-500 mb-1">Priority</p>
                <PriorityBadge priority={result.ai_output.priority} />
                <p className="text-xs text-slate-400 mt-1">{(result.ai_output.priority_confidence * 100).toFixed(0)}% confidence</p>
              </div>
              <div className="bg-slate-50 rounded-xl p-4">
                <p className="text-xs text-slate-500 mb-1">Status</p>
                <p className="font-semibold text-slate-900">{result.status}</p>
              </div>
            </div>

            {result.ai_output.summary && (
              <div className="bg-primary-50 border border-primary-200 rounded-xl p-4 mb-6 text-left">
                <p className="text-xs font-medium text-primary-700 mb-1">AI Summary</p>
                <p className="text-sm text-primary-900">{result.ai_output.summary}</p>
              </div>
            )}

            <div className="flex gap-3 justify-center">
              <button onClick={() => navigate('/complaints')} className="btn-primary">
                View My Complaints
              </button>
              <button onClick={() => { setResult(null); setDescription(''); setLocationData({ text: '', latitude: null, longitude: null }); setConfirmedCategory(null); setSuggestion(null); setImageFile(null); setImagePreview(null); }} className="btn-outline">
                File Another
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="section py-8 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Report an Issue</h1>
        <p className="page-subtitle">Describe the problem and our AI will classify and route it automatically.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Complaint Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit}>
            <div className="card p-4 sm:p-6 space-y-5">
              {/* Description */}
              <div>
                <label htmlFor="complaint-description" className="label">
                  Describe the Issue *
                </label>
                <textarea
                  id="complaint-description"
                  rows={5}
                  value={description}
                  onChange={handleDescriptionChange}
                  className={errors.description ? 'input-error resize-none text-sm' : 'input resize-none text-sm'}
                  placeholder="e.g., Large pothole on Main Street near the intersection with 5th Ave. It's about 2 feet wide and has been causing damage to vehicles for the past week..."
                />
                {errors.description && <p className="text-red-500 text-xs mt-1">{errors.description}</p>}

                {/* AI Suggestion Chip */}
                {suggestLoading && (
                  <div className="mt-2 flex items-center gap-2 text-xs sm:text-sm text-slate-400">
                    <span className="w-3 h-3 border-2 border-primary-400 border-t-transparent rounded-full animate-spin" />
                    Analyzing...
                  </div>
                )}
                {suggestion && !suggestLoading && (
                  <div className="mt-3 animate-slide-up">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 bg-primary-50 border border-primary-200 rounded-xl p-3 sm:px-4 sm:py-2">
                      <div className="flex items-center gap-2">
                        <MdOutlineSmartToy className="text-primary-600 w-5 h-5 shrink-0" />
                        <span className="text-xs sm:text-sm text-primary-800">
                          Suggested: <strong>{suggestion.suggested_category}</strong>
                          <span className="text-primary-500 ml-1">({(suggestion.confidence * 100).toFixed(0)}%)</span>
                        </span>
                      </div>
                      {confirmedCategory === suggestion.suggested_category ? (
                        <span className="badge-resolved text-xs self-end sm:self-auto">Confirmed</span>
                      ) : (
                        <button
                          type="button"
                          onClick={() => setConfirmedCategory(suggestion.suggested_category)}
                          className="text-xs font-semibold text-primary-600 hover:text-primary-700 underline self-end sm:self-auto"
                        >
                          Confirm
                        </button>
                      )}
                    </div>
                    {suggestion.clarifying_question && (
                      <p className="text-xs sm:text-sm text-amber-700 bg-amber-50 rounded-xl p-3 mt-2">
                        💡 {suggestion.clarifying_question}
                      </p>
                    )}
                  </div>
                )}

                {/* Category override */}
                {suggestion && (
                  <div className="mt-3">
                    <p className="text-xs text-slate-500 mb-2">Or select a category manually:</p>
                    <div className="flex flex-wrap gap-1.5 sm:gap-2">
                      {CATEGORIES.map(cat => (
                        <button
                          key={cat}
                          type="button"
                          onClick={() => setConfirmedCategory(cat)}
                          className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                            confirmedCategory === cat
                              ? 'bg-primary-600 text-white'
                              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                          }`}
                        >
                          {cat}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Location */}
              <div>
                <label className="label">
                  <HiOutlineLocationMarker className="inline w-4 h-4 mr-1 text-primary-600" />
                  Location *
                </label>
                <LocationPickerMap
                  locationData={locationData}
                  onChange={(data) => {
                    setLocationData(data);
                    if (data.text?.trim()?.length > 0) {
                      setErrors((prev) => {
                        if (!prev.location) return prev;
                        const copy = { ...prev };
                        delete copy.location;
                        return copy;
                      });
                    }
                  }}
                  error={errors.location}
                />
                {errors.location && <p className="text-red-500 text-xs mt-1">{errors.location}</p>}
              </div>

              {/* Image Upload */}
              <div>
                <label className="label">
                  <HiOutlinePhotograph className="inline w-4 h-4 mr-1" />
                  Photo (optional)
                </label>
                <div className="flex flex-wrap items-center gap-3 sm:gap-4">
                  <label className="btn-outline btn-sm cursor-pointer">
                    Choose File
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageChange}
                      className="hidden"
                    />
                  </label>
                  {imagePreview && (
                    <div className="relative">
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className={errors.image ? "w-20 h-20 object-cover rounded-xl border-2 border-red-500" : "w-20 h-20 object-cover rounded-xl border"}
                      />
                      <button
                        type="button"
                        onClick={() => {
                          setImagePreview(null);
                          setImageFile(null);
                          setErrors((prev) => {
                            const copy = { ...prev };
                            delete copy.image;
                            return copy;
                          });
                        }}
                        className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center shadow-sm"
                      >
                        <HiOutlineX className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                </div>
                {errors.image && (
                  <p className="text-red-600 text-xs mt-2.5 bg-red-50 border border-red-200 rounded-xl p-3 font-medium flex items-start gap-1.5 animate-fade-in">
                    <span className="shrink-0 mt-0.5">⚠️</span>
                    <span>{errors.image}</span>
                  </p>
                )}
              </div>

              {/* Submit */}
              <button
                id="submit-complaint"
                type="submit"
                disabled={loading}
                className="btn-primary btn-lg w-full sm:w-auto"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Analyzing & Submitting...
                  </span>
                ) : (
                  'Submit Complaint'
                )}
              </button>
            </div>
          </form>
        </div>

        {/* AI Chatbot Panel */}
        <div className="lg:col-span-1">
          <div className="card h-[500px] lg:h-[500px] flex flex-col sticky top-20">
            <div className="px-4 py-3 border-b border-slate-200 flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-100 rounded-xl flex items-center justify-center">
                <MdOutlineSmartToy className="text-primary-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900">AI Guide</p>
                <p className="text-xs text-slate-400">Powered by Gemini</p>
              </div>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] p-3 rounded-xl text-xs ${
                      msg.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-slate-100 text-slate-800'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-slate-100 p-3 rounded-xl text-xs text-slate-500 flex items-center gap-2">
                    <span className="w-3 h-3 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
                    Assistant is typing...
                  </div>
                </div>
              )}
            </div>

            {/* Chat Input */}
            <div className="p-3 border-t border-slate-200 flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleChatSend()}
                placeholder="Ask AI for help..."
                className="input text-xs flex-1"
              />
              <button
                type="button"
                onClick={handleChatSend}
                disabled={!chatInput.trim() || chatLoading}
                className="btn-primary btn-sm"
              >
                <HiOutlinePaperAirplane className="w-4 h-4 rotate-90" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
