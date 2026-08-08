import { useState, useRef, useEffect } from 'react';
import { HiOutlineBell, HiOutlineCheckCircle, HiOutlineX } from 'react-icons/hi';
import { useNotifications } from '../context/NotificationsContext';
import { useAuth } from '../context/AuthContext';

const TYPE_STYLES = {
  success: 'bg-emerald-50 border-emerald-200 text-emerald-700',
  info:    'bg-blue-50 border-blue-200 text-blue-700',
  warning: 'bg-amber-50 border-amber-200 text-amber-700',
  error:   'bg-red-50 border-red-200 text-red-700',
};

const TYPE_DOT = {
  success: 'bg-emerald-500',
  info:    'bg-blue-500',
  warning: 'bg-amber-500',
  error:   'bg-red-500',
};

function timeAgo(dateStr) {
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export default function NotificationBell() {
  const { isAuthenticated } = useAuth();
  const { notifications, unreadCount, fetchAll, markRead, markAllRead } = useNotifications();
  const [open, setOpen] = useState(false);
  const [prevCount, setPrevCount] = useState(0);
  const [shake, setShake] = useState(false);
  const dropdownRef = useRef(null);

  // Shake bell when new notifications arrive
  useEffect(() => {
    if (unreadCount > prevCount && prevCount !== 0) {
      setShake(true);
      setTimeout(() => setShake(false), 600);
    }
    setPrevCount(unreadCount);
  }, [unreadCount]);

  // Open → fetch latest
  const handleOpen = () => {
    setOpen((v) => {
      if (!v) fetchAll();
      return !v;
    });
  };

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  if (!isAuthenticated) return null;

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Bell Button */}
      <button
        id="notification-bell"
        onClick={handleOpen}
        className={`relative p-2 rounded-xl hover:bg-slate-100 transition-all ${shake ? 'animate-bounce' : ''}`}
        aria-label="Notifications"
      >
        <HiOutlineBell className="w-6 h-6 text-slate-600" />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 w-5 h-5 bg-red-500 text-white text-[10px] font-extrabold rounded-full flex items-center justify-center shadow-sm animate-pulse">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown — fixed & centered on mobile (slides straight down from top), absolute right on desktop */}
      {open && (
        <div className="fixed top-16 left-4 right-4 sm:absolute sm:top-full sm:left-auto sm:right-0 sm:mt-2 sm:w-80 max-w-md mx-auto sm:mx-0 bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden z-50 animate-slide-down">
          {/* Header */}
          <div className="px-4 py-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-bold text-slate-900">Notifications</p>
              {unreadCount > 0 && (
                <p className="text-xs text-slate-500">{unreadCount} unread</p>
              )}
            </div>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllRead}
                  className="text-xs font-semibold text-teal-600 hover:text-teal-700 flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-teal-50 transition-colors"
                >
                  <HiOutlineCheckCircle className="w-3.5 h-3.5" />
                  Mark all read
                </button>
              )}
              <button
                onClick={() => setOpen(false)}
                className="p-1 rounded-lg hover:bg-slate-200 transition-colors"
              >
                <HiOutlineX className="w-4 h-4 text-slate-500" />
              </button>
            </div>
          </div>

          {/* Notifications List */}
          <div className="max-h-80 overflow-y-auto divide-y divide-slate-100">
            {notifications.length === 0 ? (
              <div className="px-4 py-10 text-center">
                <HiOutlineBell className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                <p className="text-sm text-slate-400 font-medium">No notifications yet</p>
              </div>
            ) : (
              notifications.slice(0, 10).map((n) => (
                <div
                  key={n.id}
                  onClick={() => !n.is_read && markRead(n.id)}
                  className={`flex items-start gap-3 px-4 py-3.5 cursor-pointer transition-colors hover:bg-slate-50 ${
                    !n.is_read ? 'bg-blue-50/50' : ''
                  }`}
                >
                  {/* Type dot */}
                  <div className="mt-1.5 shrink-0">
                    <span className={`w-2 h-2 rounded-full block ${n.is_read ? 'bg-slate-300' : TYPE_DOT[n.type] || 'bg-blue-500'}`} />
                  </div>
                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p className={`text-xs font-bold leading-snug ${n.is_read ? 'text-slate-500' : 'text-slate-900'}`}>
                      {n.title}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{n.message}</p>
                    <p className="text-[10px] text-slate-400 mt-1 font-medium">{timeAgo(n.created_at)}</p>
                  </div>
                  {/* Unread indicator */}
                  {!n.is_read && (
                    <div className="shrink-0 mt-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-500 block" />
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
