import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UIState {
  theme: 'light' | 'dark' | 'auto';
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  activeView: string;
  loading: {
    global: boolean;
    orders: boolean;
    trades: boolean;
    positions: boolean;
    marketData: boolean;
    analytics: boolean;
    risk: boolean;
    compliance: boolean;
  };
  modals: {
    orderEntry: boolean;
    positionDetails: boolean;
    tradeDetails: boolean;
    settings: boolean;
    alerts: boolean;
  };
  panels: {
    orderBook: boolean;
    tradeHistory: boolean;
    positions: boolean;
    alerts: boolean;
    marketData: boolean;
    yieldCurve: boolean;
    riskMetrics: boolean;
  };
  preferences: {
    defaultView: string;
    refreshInterval: number;
    autoRefresh: boolean;
    compactMode: boolean;
    showAnimations: boolean;
    numberFormat: 'standard' | 'indian' | 'international';
    dateFormat: 'dd/mm/yyyy' | 'mm/dd/yyyy' | 'yyyy-mm-dd';
    timeFormat: '12h' | '24h';
    timezone: string;
  };
  filters: {
    orders: Record<string, any>;
    trades: Record<string, any>;
    positions: Record<string, any>;
    notifications: Record<string, any>;
  };
  sorting: {
    orders: { column: string; direction: 'asc' | 'desc' };
    trades: { column: string; direction: 'asc' | 'desc' };
    positions: { column: string; direction: 'asc' | 'desc' };
  };
  columns: {
    orders: Array<{ key: string; visible: boolean; width?: number; order: number }>;
    trades: Array<{ key: string; visible: boolean; width?: number; order: number }>;
    positions: Array<{ key: string; visible: boolean; width?: number; order: number }>;
  };
  alerts: Array<{
    id: string;
    type: 'error' | 'warning' | 'info' | 'success';
    message: string;
    timestamp: string;
    dismissible: boolean;
    autoHide: boolean;
    duration?: number;
  }>;
  breadcrumbs: Array<{
    label: string;
    path: string;
    active: boolean;
  }>;
  quickActions: Array<{
    id: string;
    label: string;
    icon: string;
    action: string;
    shortcut?: string;
    visible: boolean;
  }>;
}

const initialState: UIState = {
  theme: 'dark',
  sidebarOpen: true,
  sidebarCollapsed: false,
  activeView: 'dashboard',
  loading: {
    global: false,
    orders: false,
    trades: false,
    positions: false,
    marketData: false,
    analytics: false,
    risk: false,
    compliance: false,
  },
  modals: {
    orderEntry: false,
    positionDetails: false,
    tradeDetails: false,
    settings: false,
    alerts: false,
  },
  panels: {
    orderBook: true,
    tradeHistory: true,
    positions: true,
    alerts: true,
    marketData: true,
    yieldCurve: false,
    riskMetrics: false,
  },
  preferences: {
    defaultView: 'dashboard',
    refreshInterval: 5000,
    autoRefresh: true,
    compactMode: false,
    showAnimations: true,
    numberFormat: 'indian',
    dateFormat: 'dd/mm/yyyy',
    timeFormat: '24h',
    timezone: 'Asia/Kolkata',
  },
  filters: {
    orders: {},
    trades: {},
    positions: {},
    notifications: {},
  },
  sorting: {
    orders: { column: 'timestamp', direction: 'desc' },
    trades: { column: 'timestamp', direction: 'desc' },
    positions: { column: 'symbol', direction: 'asc' },
  },
  columns: {
    orders: [
      { key: 'symbol', visible: true, order: 0 },
      { key: 'side', visible: true, order: 1 },
      { key: 'quantity', visible: true, order: 2 },
      { key: 'price', visible: true, order: 3 },
      { key: 'status', visible: true, order: 4 },
      { key: 'timestamp', visible: true, order: 5 },
    ],
    trades: [
      { key: 'symbol', visible: true, order: 0 },
      { key: 'side', visible: true, order: 1 },
      { key: 'quantity', visible: true, order: 2 },
      { key: 'price', visible: true, order: 3 },
      { key: 'timestamp', visible: true, order: 4 },
    ],
    positions: [
      { key: 'symbol', visible: true, order: 0 },
      { key: 'quantity', visible: true, order: 1 },
      { key: 'averagePrice', visible: true, order: 2 },
      { key: 'marketValue', visible: true, order: 3 },
      { key: 'unrealizedPnL', visible: true, order: 4 },
    ],
  },
  alerts: [],
  breadcrumbs: [
    { label: 'Dashboard', path: '/', active: true },
  ],
  quickActions: [
    { id: 'new_order', label: 'New Order', icon: 'add', action: 'openOrderEntry', shortcut: 'Ctrl+N', visible: true },
    { id: 'refresh', label: 'Refresh', icon: 'refresh', action: 'refreshData', shortcut: 'F5', visible: true },
    { id: 'export', label: 'Export', icon: 'download', action: 'exportData', visible: true },
    { id: 'settings', label: 'Settings', icon: 'settings', action: 'openSettings', visible: true },
  ],
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'auto'>) => {
      state.theme = action.payload;
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    toggleSidebarCollapse: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload;
    },
    setActiveView: (state, action: PayloadAction<string>) => {
      state.activeView = action.payload;
    },
    setLoading: (state, action: PayloadAction<{ key: keyof UIState['loading']; value: boolean }>) => {
      const { key, value } = action.payload;
      state.loading[key] = value;
    },
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.loading.global = action.payload;
    },
    toggleModal: (state, action: PayloadAction<keyof UIState['modals']>) => {
      const modal = action.payload;
      state.modals[modal] = !state.modals[modal];
    },
    setModal: (state, action: PayloadAction<{ modal: keyof UIState['modals']; open: boolean }>) => {
      const { modal, open } = action.payload;
      state.modals[modal] = open;
    },
    togglePanel: (state, action: PayloadAction<keyof UIState['panels']>) => {
      const panel = action.payload;
      state.panels[panel] = !state.panels[panel];
    },
    setPanel: (state, action: PayloadAction<{ panel: keyof UIState['panels']; visible: boolean }>) => {
      const { panel, visible } = action.payload;
      state.panels[panel] = visible;
    },
    updatePreferences: (state, action: PayloadAction<Partial<UIState['preferences']>>) => {
      state.preferences = { ...state.preferences, ...action.payload };
    },
    setFilter: (state, action: PayloadAction<{
      category: keyof UIState['filters'];
      filters: Record<string, any>;
    }>) => {
      const { category, filters } = action.payload;
      state.filters[category] = filters;
    },
    clearFilter: (state, action: PayloadAction<keyof UIState['filters']>) => {
      state.filters[action.payload] = {};
    },
    setSorting: (state, action: PayloadAction<{
      category: keyof UIState['sorting'];
      column: string;
      direction: 'asc' | 'desc';
    }>) => {
      const { category, column, direction } = action.payload;
      state.sorting[category] = { column, direction };
    },
    updateColumnConfig: (state, action: PayloadAction<{
      category: keyof UIState['columns'];
      columns: UIState['columns'][keyof UIState['columns']];
    }>) => {
      const { category, columns } = action.payload;
      state.columns[category] = columns;
    },
    addAlert: (state, action: PayloadAction<Omit<UIState['alerts'][0], 'id' | 'timestamp'>>) => {
      const alert = {
        ...action.payload,
        id: Math.random().toString(36).substr(2, 9),
        timestamp: new Date().toISOString(),
      };
      state.alerts.push(alert);
    },
    removeAlert: (state, action: PayloadAction<string>) => {
      state.alerts = state.alerts.filter(alert => alert.id !== action.payload);
    },
    clearAlerts: (state) => {
      state.alerts = [];
    },
    setBreadcrumbs: (state, action: PayloadAction<UIState['breadcrumbs']>) => {
      state.breadcrumbs = action.payload;
    },
    addBreadcrumb: (state, action: PayloadAction<Omit<UIState['breadcrumbs'][0], 'active'>>) => {
      // Mark all existing breadcrumbs as inactive
      state.breadcrumbs.forEach(crumb => {
        crumb.active = false;
      });
      
      // Add new breadcrumb as active
      state.breadcrumbs.push({ ...action.payload, active: true });
    },
    updateQuickActions: (state, action: PayloadAction<UIState['quickActions']>) => {
      state.quickActions = action.payload;
    },
    toggleQuickAction: (state, action: PayloadAction<string>) => {
      const action_item = state.quickActions.find(item => item.id === action.payload);
      if (action_item) {
        action_item.visible = !action_item.visible;
      }
    },
    resetUI: (state) => {
      // Reset to initial state but preserve theme and some preferences
      const { theme, preferences } = state;
      Object.assign(state, initialState);
      state.theme = theme;
      state.preferences = preferences;
    },
  },
});

export const {
  setTheme,
  toggleSidebar,
  setSidebarOpen,
  toggleSidebarCollapse,
  setSidebarCollapsed,
  setActiveView,
  setLoading,
  setGlobalLoading,
  toggleModal,
  setModal,
  togglePanel,
  setPanel,
  updatePreferences,
  setFilter,
  clearFilter,
  setSorting,
  updateColumnConfig,
  addAlert,
  removeAlert,
  clearAlerts,
  setBreadcrumbs,
  addBreadcrumb,
  updateQuickActions,
  toggleQuickAction,
  resetUI,
} = uiSlice.actions;

export default uiSlice.reducer;
