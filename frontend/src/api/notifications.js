import client from './client';

const notificationsApi = {
  /** Fetch last 20 notifications for current user */
  getAll: () => client.get('/notifications').then((r) => r.data),

  /** Fast unread count — polled every 30s */
  getUnreadCount: () => client.get('/notifications/unread-count').then((r) => r.data),

  /** Mark a single notification as read */
  markRead: (id) => client.patch(`/notifications/${id}/read`).then((r) => r.data),

  /** Mark all notifications as read */
  markAllRead: () => client.patch('/notifications/read-all'),
};

export default notificationsApi;
