import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from './AuthContext';
import notificationsApi from '../api/notifications';

const NotificationsContext = createContext(null);

const POLL_INTERVAL_MS = 30000; // 30 seconds

export function NotificationsProvider({ children }) {
  const { isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const intervalRef = useRef(null);

  const fetchAll = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const data = await notificationsApi.getAll();
      setNotifications(data);
      setUnreadCount(data.filter((n) => !n.is_read).length);
    } catch {
      // Silent fail — notifications are non-critical
    }
  }, [isAuthenticated]);

  const pollUnreadCount = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const data = await notificationsApi.getUnreadCount();
      setUnreadCount(data.count);
    } catch {
      // Silent fail
    }
  }, [isAuthenticated]);

  const markRead = useCallback(async (id) => {
    try {
      await notificationsApi.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch {/* silent */}
  }, []);

  const markAllRead = useCallback(async () => {
    try {
      await notificationsApi.markAllRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch {/* silent */}
  }, []);

  // Initial fetch when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchAll();
    } else {
      setNotifications([]);
      setUnreadCount(0);
    }
  }, [isAuthenticated, fetchAll]);

  // Poll unread count every 30 seconds
  useEffect(() => {
    if (!isAuthenticated) {
      clearInterval(intervalRef.current);
      return;
    }
    intervalRef.current = setInterval(pollUnreadCount, POLL_INTERVAL_MS);
    return () => clearInterval(intervalRef.current);
  }, [isAuthenticated, pollUnreadCount]);

  return (
    <NotificationsContext.Provider
      value={{ notifications, unreadCount, loading, fetchAll, markRead, markAllRead }}
    >
      {children}
    </NotificationsContext.Provider>
  );
}

export function useNotifications() {
  const ctx = useContext(NotificationsContext);
  if (!ctx) throw new Error('useNotifications must be used inside NotificationsProvider');
  return ctx;
}
