import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Widget {
  id: string;
  type: 'orderBook' | 'positions' | 'trades' | 'marketData' | 'chart' | 'news' | 'alerts' | 'portfolio' | 'risk';
  title: string;
  config: Record<string, any>;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  minimized: boolean;
  visible: boolean;
  resizable: boolean;
  draggable: boolean;
}

interface Layout {
  id: string;
  name: string;
  description?: string;
  widgets: Widget[];
  createdAt: string;
  updatedAt: string;
  isDefault?: boolean;
}

interface Workspace {
  id: string;
  name: string;
  description?: string;
  layouts: Layout[];
  activeLayoutId: string;
  createdAt: string;
  updatedAt: string;
}

interface WorkspaceState {
  workspaces: Workspace[];
  activeWorkspaceId: string | null;
  currentLayout: Layout | null;
  presetLayouts: Array<{
    id: string;
    name: string;
    description: string;
    preview: string;
    config: Layout;
  }>;
  gridSize: number;
  snapToGrid: boolean;
  showGrid: boolean;
  multiMonitorSetup: {
    enabled: boolean;
    monitors: Array<{
      id: string;
      name: string;
      resolution: { width: number; height: number };
      position: { x: number; y: number };
      primary: boolean;
    }>;
  };
  isEditing: boolean;
  isLoading: boolean;
  error: string | null;
  lastSaved: string | null;
  autoSave: boolean;
  saveInterval: number;
}

const initialState: WorkspaceState = {
  workspaces: [],
  activeWorkspaceId: null,
  currentLayout: null,
  presetLayouts: [
    {
      id: 'default-trader',
      name: 'Default Trader Layout',
      description: 'Standard layout for bond traders',
      preview: '/images/layouts/default-trader.png',
      config: {
        id: 'default-trader',
        name: 'Default Trader',
        widgets: [
          {
            id: 'orderbook-1',
            type: 'orderBook',
            title: 'Order Book',
            config: { symbol: 'GSEC10Y' },
            position: { x: 0, y: 0, width: 4, height: 6 },
            minimized: false,
            visible: true,
            resizable: true,
            draggable: true,
          },
          {
            id: 'positions-1',
            type: 'positions',
            title: 'Positions',
            config: {},
            position: { x: 4, y: 0, width: 8, height: 6 },
            minimized: false,
            visible: true,
            resizable: true,
            draggable: true,
          },
          {
            id: 'trades-1',
            type: 'trades',
            title: 'Recent Trades',
            config: { limit: 20 },
            position: { x: 0, y: 6, width: 6, height: 6 },
            minimized: false,
            visible: true,
            resizable: true,
            draggable: true,
          },
          {
            id: 'marketdata-1',
            type: 'marketData',
            title: 'Market Data',
            config: { symbols: ['GSEC10Y', 'GSEC5Y', 'GSEC2Y'] },
            position: { x: 6, y: 6, width: 6, height: 6 },
            minimized: false,
            visible: true,
            resizable: true,
            draggable: true,
          },
        ],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        isDefault: true,
      },
    },
  ],
  gridSize: 20,
  snapToGrid: true,
  showGrid: false,
  multiMonitorSetup: {
    enabled: false,
    monitors: [],
  },
  isEditing: false,
  isLoading: false,
  error: null,
  lastSaved: null,
  autoSave: true,
  saveInterval: 30000, // 30 seconds
};

const workspaceSlice = createSlice({
  name: 'workspace',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setWorkspaces: (state, action: PayloadAction<Workspace[]>) => {
      state.workspaces = action.payload;
      state.isLoading = false;
    },
    addWorkspace: (state, action: PayloadAction<Workspace>) => {
      state.workspaces.push(action.payload);
    },
    updateWorkspace: (state, action: PayloadAction<Workspace>) => {
      const index = state.workspaces.findIndex(w => w.id === action.payload.id);
      if (index !== -1) {
        state.workspaces[index] = action.payload;
        state.lastSaved = new Date().toISOString();
      }
    },
    removeWorkspace: (state, action: PayloadAction<string>) => {
      state.workspaces = state.workspaces.filter(w => w.id !== action.payload);
      
      // If the removed workspace was active, clear active workspace
      if (state.activeWorkspaceId === action.payload) {
        state.activeWorkspaceId = null;
        state.currentLayout = null;
      }
    },
    setActiveWorkspace: (state, action: PayloadAction<string>) => {
      state.activeWorkspaceId = action.payload;
      const workspace = state.workspaces.find(w => w.id === action.payload);
      
      if (workspace) {
        const activeLayout = workspace.layouts.find(l => l.id === workspace.activeLayoutId);
        state.currentLayout = activeLayout || workspace.layouts[0] || null;
      }
    },
    addLayout: (state, action: PayloadAction<{ workspaceId: string; layout: Layout }>) => {
      const { workspaceId, layout } = action.payload;
      const workspace = state.workspaces.find(w => w.id === workspaceId);
      
      if (workspace) {
        workspace.layouts.push(layout);
        workspace.updatedAt = new Date().toISOString();
      }
    },
    updateLayout: (state, action: PayloadAction<Layout>) => {
      const updatedLayout = action.payload;
      
      // Update in workspace
      const workspace = state.workspaces.find(w => w.activeLayoutId === updatedLayout.id);
      if (workspace) {
        const layoutIndex = workspace.layouts.findIndex(l => l.id === updatedLayout.id);
        if (layoutIndex !== -1) {
          workspace.layouts[layoutIndex] = updatedLayout;
          workspace.updatedAt = new Date().toISOString();
        }
      }
      
      // Update current layout if it's the active one
      if (state.currentLayout?.id === updatedLayout.id) {
        state.currentLayout = updatedLayout;
      }
      
      state.lastSaved = new Date().toISOString();
    },
    setActiveLayout: (state, action: PayloadAction<string>) => {
      if (state.activeWorkspaceId) {
        const workspace = state.workspaces.find(w => w.id === state.activeWorkspaceId);
        if (workspace) {
          workspace.activeLayoutId = action.payload;
          const newActiveLayout = workspace.layouts.find(l => l.id === action.payload);
          state.currentLayout = newActiveLayout || null;
          workspace.updatedAt = new Date().toISOString();
        }
      }
    },
    addWidget: (state, action: PayloadAction<Widget>) => {
      if (state.currentLayout) {
        state.currentLayout.widgets.push(action.payload);
        state.currentLayout.updatedAt = new Date().toISOString();
      }
    },
    updateWidget: (state, action: PayloadAction<Widget>) => {
      if (state.currentLayout) {
        const widgetIndex = state.currentLayout.widgets.findIndex(w => w.id === action.payload.id);
        if (widgetIndex !== -1) {
          state.currentLayout.widgets[widgetIndex] = action.payload;
          state.currentLayout.updatedAt = new Date().toISOString();
        }
      }
    },
    removeWidget: (state, action: PayloadAction<string>) => {
      if (state.currentLayout) {
        state.currentLayout.widgets = state.currentLayout.widgets.filter(w => w.id !== action.payload);
        state.currentLayout.updatedAt = new Date().toISOString();
      }
    },
    moveWidget: (state, action: PayloadAction<{
      widgetId: string;
      position: { x: number; y: number };
    }>) => {
      if (state.currentLayout) {
        const { widgetId, position } = action.payload;
        const widget = state.currentLayout.widgets.find(w => w.id === widgetId);
        
        if (widget) {
          widget.position.x = position.x;
          widget.position.y = position.y;
          state.currentLayout.updatedAt = new Date().toISOString();
        }
      }
    },
    resizeWidget: (state, action: PayloadAction<{
      widgetId: string;
      size: { width: number; height: number };
    }>) => {
      if (state.currentLayout) {
        const { widgetId, size } = action.payload;
        const widget = state.currentLayout.widgets.find(w => w.id === widgetId);
        
        if (widget) {
          widget.position.width = size.width;
          widget.position.height = size.height;
          state.currentLayout.updatedAt = new Date().toISOString();
        }
      }
    },
    toggleWidgetVisibility: (state, action: PayloadAction<string>) => {
      if (state.currentLayout) {
        const widget = state.currentLayout.widgets.find(w => w.id === action.payload);
        if (widget) {
          widget.visible = !widget.visible;
          state.currentLayout.updatedAt = new Date().toISOString();
        }
      }
    },
    minimizeWidget: (state, action: PayloadAction<string>) => {
      if (state.currentLayout) {
        const widget = state.currentLayout.widgets.find(w => w.id === action.payload);
        if (widget) {
          widget.minimized = !widget.minimized;
          state.currentLayout.updatedAt = new Date().toISOString();
        }
      }
    },
    setGridSettings: (state, action: PayloadAction<{
      gridSize?: number;
      snapToGrid?: boolean;
      showGrid?: boolean;
    }>) => {
      const { gridSize, snapToGrid, showGrid } = action.payload;
      
      if (gridSize !== undefined) state.gridSize = gridSize;
      if (snapToGrid !== undefined) state.snapToGrid = snapToGrid;
      if (showGrid !== undefined) state.showGrid = showGrid;
    },
    setMultiMonitorSetup: (state, action: PayloadAction<WorkspaceState['multiMonitorSetup']>) => {
      state.multiMonitorSetup = action.payload;
    },
    setEditing: (state, action: PayloadAction<boolean>) => {
      state.isEditing = action.payload;
    },
    setAutoSave: (state, action: PayloadAction<{ enabled: boolean; interval?: number }>) => {
      const { enabled, interval } = action.payload;
      state.autoSave = enabled;
      if (interval !== undefined) {
        state.saveInterval = interval;
      }
    },
    duplicateLayout: (state, action: PayloadAction<{ layoutId: string; newName: string }>) => {
      if (state.activeWorkspaceId && state.currentLayout) {
        const { layoutId, newName } = action.payload;
        const workspace = state.workspaces.find(w => w.id === state.activeWorkspaceId);
        const layoutToDuplicate = workspace?.layouts.find(l => l.id === layoutId);
        
        if (workspace && layoutToDuplicate) {
          const newLayout: Layout = {
            ...layoutToDuplicate,
            id: Math.random().toString(36).substr(2, 9),
            name: newName,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            isDefault: false,
          };
          
          workspace.layouts.push(newLayout);
          workspace.updatedAt = new Date().toISOString();
        }
      }
    },
    resetLayout: (state, action: PayloadAction<string>) => {
      const presetLayout = state.presetLayouts.find(p => p.id === action.payload);
      if (presetLayout && state.currentLayout) {
        state.currentLayout.widgets = [...presetLayout.config.widgets];
        state.currentLayout.updatedAt = new Date().toISOString();
      }
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
  setWorkspaces,
  addWorkspace,
  updateWorkspace,
  removeWorkspace,
  setActiveWorkspace,
  addLayout,
  updateLayout,
  setActiveLayout,
  addWidget,
  updateWidget,
  removeWidget,
  moveWidget,
  resizeWidget,
  toggleWidgetVisibility,
  minimizeWidget,
  setGridSettings,
  setMultiMonitorSetup,
  setEditing,
  setAutoSave,
  duplicateLayout,
  resetLayout,
  setError,
  clearError,
} = workspaceSlice.actions;

export default workspaceSlice.reducer;
