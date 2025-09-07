import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface TradingSettings {
  defaultOrderType: 'market' | 'limit' | 'stop' | 'stop_limit';
  defaultTimeInForce: 'gtc' | 'ioc' | 'fok' | 'gtd';
  confirmOrders: boolean;
  maxOrderSize: number;
  enableSoundAlerts: boolean;
  autoRefreshInterval: number;
  showAdvancedOrderOptions: boolean;
  enableOneClickTrading: boolean;
  defaultQuantityIncrement: number;
  enableHotkeys: boolean;
}

interface DisplaySettings {
  theme: 'light' | 'dark' | 'auto';
  language: 'en' | 'hi' | 'mr';
  timezone: string;
  dateFormat: 'dd/mm/yyyy' | 'mm/dd/yyyy' | 'yyyy-mm-dd';
  timeFormat: '12h' | '24h';
  numberFormat: 'standard' | 'indian' | 'international';
  currencyFormat: 'symbol' | 'code' | 'name';
  decimalPlaces: {
    price: number;
    quantity: number;
    percentage: number;
    currency: number;
  };
  showAnimations: boolean;
  compactMode: boolean;
  highContrastMode: boolean;
  fontSize: 'small' | 'medium' | 'large';
}

interface NotificationSettings {
  enabled: boolean;
  types: {
    orderFilled: boolean;
    orderRejected: boolean;
    positionUpdates: boolean;
    priceAlerts: boolean;
    riskAlerts: boolean;
    complianceAlerts: boolean;
    systemAlerts: boolean;
    marketNews: boolean;
  };
  channels: {
    inApp: boolean;
    email: boolean;
    sms: boolean;
    push: boolean;
  };
  sounds: {
    enabled: boolean;
    volume: number;
    orderFilled: string;
    orderRejected: string;
    alert: string;
  };
  quietHours: {
    enabled: boolean;
    start: string;
    end: string;
  };
  frequency: {
    immediate: boolean;
    batch: boolean;
    batchInterval: number; // in minutes
  };
}

interface SecuritySettings {
  twoFactorEnabled: boolean;
  biometricEnabled: boolean;
  sessionTimeout: number; // in minutes
  autoLockEnabled: boolean;
  autoLockTimeout: number; // in minutes
  requirePasswordForSensitiveActions: boolean;
  logSecurityEvents: boolean;
  allowRememberDevice: boolean;
  maxConcurrentSessions: number;
}

interface APISettings {
  rateLimitPerMinute: number;
  rateLimitPerHour: number;
  webhookEnabled: boolean;
  webhookUrl: string;
  webhookSecret: string;
  webhookEvents: string[];
  apiKeysEnabled: boolean;
  ipWhitelist: string[];
}

interface BackupSettings {
  autoBackup: boolean;
  backupInterval: 'daily' | 'weekly' | 'monthly';
  backupRetention: number; // in days
  includePersonalData: boolean;
  encryptBackups: boolean;
  backupLocation: 'local' | 'cloud';
  cloudProvider?: 'aws' | 'google' | 'azure';
}

interface SettingsState {
  trading: TradingSettings;
  display: DisplaySettings;
  notifications: NotificationSettings;
  security: SecuritySettings;
  api: APISettings;
  backup: BackupSettings;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  lastUpdated: string | null;
  lastSynced: string | null;
  hasUnsavedChanges: boolean;
}

const initialState: SettingsState = {
  trading: {
    defaultOrderType: 'limit',
    defaultTimeInForce: 'gtc',
    confirmOrders: true,
    maxOrderSize: 100000000,
    enableSoundAlerts: true,
    autoRefreshInterval: 5000,
    showAdvancedOrderOptions: false,
    enableOneClickTrading: false,
    defaultQuantityIncrement: 1000,
    enableHotkeys: true,
  },
  display: {
    theme: 'dark',
    language: 'en',
    timezone: 'Asia/Kolkata',
    dateFormat: 'dd/mm/yyyy',
    timeFormat: '24h',
    numberFormat: 'indian',
    currencyFormat: 'symbol',
    decimalPlaces: {
      price: 4,
      quantity: 0,
      percentage: 2,
      currency: 2,
    },
    showAnimations: true,
    compactMode: false,
    highContrastMode: false,
    fontSize: 'medium',
  },
  notifications: {
    enabled: true,
    types: {
      orderFilled: true,
      orderRejected: true,
      positionUpdates: true,
      priceAlerts: true,
      riskAlerts: true,
      complianceAlerts: true,
      systemAlerts: true,
      marketNews: false,
    },
    channels: {
      inApp: true,
      email: false,
      sms: false,
      push: false,
    },
    sounds: {
      enabled: true,
      volume: 0.7,
      orderFilled: 'success.wav',
      orderRejected: 'error.wav',
      alert: 'warning.wav',
    },
    quietHours: {
      enabled: false,
      start: '22:00',
      end: '08:00',
    },
    frequency: {
      immediate: true,
      batch: false,
      batchInterval: 15,
    },
  },
  security: {
    twoFactorEnabled: false,
    biometricEnabled: false,
    sessionTimeout: 480, // 8 hours
    autoLockEnabled: false,
    autoLockTimeout: 15, // 15 minutes
    requirePasswordForSensitiveActions: true,
    logSecurityEvents: true,
    allowRememberDevice: false,
    maxConcurrentSessions: 3,
  },
  api: {
    rateLimitPerMinute: 1000,
    rateLimitPerHour: 10000,
    webhookEnabled: false,
    webhookUrl: '',
    webhookSecret: '',
    webhookEvents: [],
    apiKeysEnabled: false,
    ipWhitelist: [],
  },
  backup: {
    autoBackup: false,
    backupInterval: 'daily',
    backupRetention: 30,
    includePersonalData: false,
    encryptBackups: true,
    backupLocation: 'local',
  },
  isLoading: false,
  isSaving: false,
  error: null,
  lastUpdated: null,
  lastSynced: null,
  hasUnsavedChanges: false,
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setSaving: (state, action: PayloadAction<boolean>) => {
      state.isSaving = action.payload;
    },
    setSettings: (state, action: PayloadAction<Partial<SettingsState>>) => {
      const { isLoading, isSaving, error, hasUnsavedChanges, ...settings } = action.payload;
      Object.assign(state, settings);
      state.lastSynced = new Date().toISOString();
      state.hasUnsavedChanges = false;
      state.isLoading = false;
    },
    updateTradingSettings: (state, action: PayloadAction<Partial<TradingSettings>>) => {
      state.trading = { ...state.trading, ...action.payload };
      state.lastUpdated = new Date().toISOString();
      state.hasUnsavedChanges = true;
    },
    updateDisplaySettings: (state, action: PayloadAction<Partial<DisplaySettings>>) => {
      state.display = { ...state.display, ...action.payload };
      state.lastUpdated = new Date().toISOString();
      state.hasUnsavedChanges = true;
    },
    updateNotificationSettings: (state, action: PayloadAction<Partial<NotificationSettings>>) => {
      state.notifications = { ...state.notifications, ...action.payload };
      state.lastUpdated = new Date().toISOString();
      state.hasUnsavedChanges = true;
    },
    updateSecuritySettings: (state, action: PayloadAction<Partial<SecuritySettings>>) => {
      state.security = { ...state.security, ...action.payload };
      state.lastUpdated = new Date().toISOString();
      state.hasUnsavedChanges = true;
    },
    updateAPISettings: (state, action: PayloadAction<Partial<APISettings>>) => {
      state.api = { ...state.api, ...action.payload };
      state.lastUpdated = new Date().toISOString();
      state.hasUnsavedChanges = true;
    },
    updateBackupSettings: (state, action: PayloadAction<Partial<BackupSettings>>) => {
      state.backup = { ...state.backup, ...action.payload };
      state.lastUpdated = new Date().toISOString();
      state.hasUnsavedChanges = true;
    },
    toggleNotificationType: (state, action: PayloadAction<keyof NotificationSettings['types']>) => {
      const type = action.payload;
      state.notifications.types[type] = !state.notifications.types[type];
      state.lastUpdated = new Date().toISOString();
      state.hasUnsavedChanges = true;
    },
    toggleNotificationChannel: (state, action: PayloadAction<keyof NotificationSettings['channels']>) => {
      const channel = action.payload;
      state.notifications.channels[channel] = !state.notifications.channels[channel];
      state.lastUpdated = new Date().toISOString();
      state.hasUnsavedChanges = true;
    },
    addWebhookEvent: (state, action: PayloadAction<string>) => {
      if (!state.api.webhookEvents.includes(action.payload)) {
        state.api.webhookEvents.push(action.payload);
        state.lastUpdated = new Date().toISOString();
        state.hasUnsavedChanges = true;
      }
    },
    removeWebhookEvent: (state, action: PayloadAction<string>) => {
      state.api.webhookEvents = state.api.webhookEvents.filter(event => event !== action.payload);
      state.lastUpdated = new Date().toISOString();
      state.hasUnsavedChanges = true;
    },
    addIPToWhitelist: (state, action: PayloadAction<string>) => {
      if (!state.api.ipWhitelist.includes(action.payload)) {
        state.api.ipWhitelist.push(action.payload);
        state.lastUpdated = new Date().toISOString();
        state.hasUnsavedChanges = true;
      }
    },
    removeIPFromWhitelist: (state, action: PayloadAction<string>) => {
      state.api.ipWhitelist = state.api.ipWhitelist.filter(ip => ip !== action.payload);
      state.lastUpdated = new Date().toISOString();
      state.hasUnsavedChanges = true;
    },
    resetToDefaults: (state, action: PayloadAction<keyof SettingsState | 'all'>) => {
      const section = action.payload;
      
      if (section === 'all') {
        Object.assign(state, initialState);
      } else if (section in initialState) {
        state[section] = initialState[section];
      }
      
      state.lastUpdated = new Date().toISOString();
      state.hasUnsavedChanges = true;
    },
    markAsSaved: (state) => {
      state.hasUnsavedChanges = false;
      state.lastSynced = new Date().toISOString();
      state.isSaving = false;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
      state.isSaving = false;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setLoading,
  setSaving,
  setSettings,
  updateTradingSettings,
  updateDisplaySettings,
  updateNotificationSettings,
  updateSecuritySettings,
  updateAPISettings,
  updateBackupSettings,
  toggleNotificationType,
  toggleNotificationChannel,
  addWebhookEvent,
  removeWebhookEvent,
  addIPToWhitelist,
  removeIPFromWhitelist,
  resetToDefaults,
  markAsSaved,
  setError,
  clearError,
} = settingsSlice.actions;

export default settingsSlice.reducer;
