import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  category: 'trade' | 'order' | 'risk' | 'compliance' | 'system' | 'market';
  title: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
  read: boolean;
  dismissed: boolean;
  actionable: boolean;
  actions?: Array<{
    label: string;
    action: string;
    primary?: boolean;
  }>;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  autoHide?: boolean;
  duration?: number;
  relatedId?: string;
}

interface NotificationPreferences {
  enabled: boolean;
  categories: {
    trade: boolean;
    order: boolean;
    risk: boolean;
    compliance: boolean;
    system: boolean;
    market: boolean;
  };
  channels: {
    toast: boolean;
    badge: boolean;
    email: boolean;
    sms: boolean;
    push: boolean;
  };
  priority: {
    low: boolean;
    medium: boolean;
    high: boolean;
    urgent: boolean;
  };
  quietHours: {
    enabled: boolean;
    start: string;
    end: string;
  };
  sounds: {
    enabled: boolean;
    volume: number;
  };
}

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  preferences: NotificationPreferences;
  toastQueue: Notification[];
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

const initialState: NotificationState = {
  notifications: [],
  unreadCount: 0,
  preferences: {
    enabled: true,
    categories: {
      trade: true,
      order: true,
      risk: true,
      compliance: true,
      system: true,
      market: true,
    },
    channels: {
      toast: true,
      badge: true,
      email: false,
      sms: false,
      push: false,
    },
    priority: {
      low: true,
      medium: true,
      high: true,
      urgent: true,
    },
    quietHours: {
      enabled: false,
      start: '22:00',
      end: '08:00',
    },
    sounds: {
      enabled: true,
      volume: 0.5,
    },
  },
  toastQueue: [],
  isLoading: false,
  error: null,
  lastUpdated: null,
};

const notificationSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    addNotification: (state, action: PayloadAction<Notification>) => {
      const notification = action.payload;
      
      // Check if notifications are enabled for this category
      if (!state.preferences.enabled || !state.preferences.categories[notification.category]) {
        return;
      }
      
      // Check if priority is enabled
      if (!state.preferences.priority[notification.priority]) {
        return;
      }
      
      state.notifications.unshift(notification);
      
      if (!notification.read) {
        state.unreadCount += 1;
      }
      
      // Add to toast queue if toast notifications are enabled
      if (state.preferences.channels.toast) {
        state.toastQueue.push(notification);
      }
      
      state.lastUpdated = new Date().toISOString();
    },
    setNotifications: (state, action: PayloadAction<Notification[]>) => {
      state.notifications = action.payload;
      state.unreadCount = action.payload.filter(n => !n.read).length;
      state.lastUpdated = new Date().toISOString();
      state.isLoading = false;
    },
    markAsRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification && !notification.read) {
        notification.read = true;
        state.unreadCount = Math.max(0, state.unreadCount - 1);
        state.lastUpdated = new Date().toISOString();
      }
    },
    markAllAsRead: (state) => {
      state.notifications.forEach(n => {
        if (!n.read) {
          n.read = true;
        }
      });
      state.unreadCount = 0;
      state.lastUpdated = new Date().toISOString();
    },
    dismissNotification: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification) {
        notification.dismissed = true;
        if (!notification.read) {
          notification.read = true;
          state.unreadCount = Math.max(0, state.unreadCount - 1);
        }
        state.lastUpdated = new Date().toISOString();
      }
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      const index = state.notifications.findIndex(n => n.id === action.payload);
      if (index !== -1) {
        const notification = state.notifications[index];
        if (!notification.read) {
          state.unreadCount = Math.max(0, state.unreadCount - 1);
        }
        state.notifications.splice(index, 1);
        state.lastUpdated = new Date().toISOString();
      }
    },
    clearAllNotifications: (state) => {
      state.notifications = [];
      state.unreadCount = 0;
      state.toastQueue = [];
      state.lastUpdated = new Date().toISOString();
    },
    clearOldNotifications: (state, action: PayloadAction<number>) => {
      const cutoffTime = action.payload;
      const oldNotifications = state.notifications.filter(n => new Date(n.timestamp).getTime() < cutoffTime);
      const unreadOldCount = oldNotifications.filter(n => !n.read).length;
      
      state.notifications = state.notifications.filter(n => new Date(n.timestamp).getTime() >= cutoffTime);
      state.unreadCount = Math.max(0, state.unreadCount - unreadOldCount);
      state.lastUpdated = new Date().toISOString();
    },
    removeFromToastQueue: (state, action: PayloadAction<string>) => {
      state.toastQueue = state.toastQueue.filter(n => n.id !== action.payload);
    },
    clearToastQueue: (state) => {
      state.toastQueue = [];
    },
    updatePreferences: (state, action: PayloadAction<Partial<NotificationPreferences>>) => {
      state.preferences = { ...state.preferences, ...action.payload };
      state.lastUpdated = new Date().toISOString();
    },
    updateCategoryPreference: (state, action: PayloadAction<{
      category: keyof NotificationPreferences['categories'];
      enabled: boolean;
    }>) => {
      const { category, enabled } = action.payload;
      state.preferences.categories[category] = enabled;
      state.lastUpdated = new Date().toISOString();
    },
    updateChannelPreference: (state, action: PayloadAction<{
      channel: keyof NotificationPreferences['channels'];
      enabled: boolean;
    }>) => {
      const { channel, enabled } = action.payload;
      state.preferences.channels[channel] = enabled;
      state.lastUpdated = new Date().toISOString();
    },
    updatePriorityPreference: (state, action: PayloadAction<{
      priority: keyof NotificationPreferences['priority'];
      enabled: boolean;
    }>) => {
      const { priority, enabled } = action.payload;
      state.preferences.priority[priority] = enabled;
      state.lastUpdated = new Date().toISOString();
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setLoading,
  addNotification,
  setNotifications,
  markAsRead,
  markAllAsRead,
  dismissNotification,
  removeNotification,
  clearAllNotifications,
  clearOldNotifications,
  removeFromToastQueue,
  clearToastQueue,
  updatePreferences,
  updateCategoryPreference,
  updateChannelPreference,
  updatePriorityPreference,
  setError,
  clearError,
} = notificationSlice.actions;

export default notificationSlice.reducer;
