import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Position {
  symbol: string;
  accountId: string;
  quantity: number;
  averagePrice: number;
  marketValue: number;
  unrealizedPnL: number;
  realizedPnL: number;
  dayPnL: number;
  lastUpdated: string;
  instrumentName?: string;
  sector?: string;
  maturityDate?: string;
  yieldToMaturity?: number;
  duration?: number;
}

interface PositionState {
  positions: Position[];
  totalValue: number;
  totalPnL: number;
  dayPnL: number;
  unrealizedPnL: number;
  realizedPnL: number;
  selectedPosition: Position | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
  groupBy: 'symbol' | 'sector' | 'maturity' | 'rating';
  sortBy: 'symbol' | 'value' | 'pnl' | 'dayPnL';
  sortOrder: 'asc' | 'desc';
}

const initialState: PositionState = {
  positions: [],
  totalValue: 0,
  totalPnL: 0,
  dayPnL: 0,
  unrealizedPnL: 0,
  realizedPnL: 0,
  selectedPosition: null,
  isLoading: false,
  error: null,
  lastUpdated: null,
  groupBy: 'symbol',
  sortBy: 'value',
  sortOrder: 'desc',
};

const positionSlice = createSlice({
  name: 'positions',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setPositions: (state, action: PayloadAction<Position[]>) => {
      state.positions = action.payload;
      
      // Calculate totals
      state.totalValue = action.payload.reduce((sum, pos) => sum + pos.marketValue, 0);
      state.totalPnL = action.payload.reduce((sum, pos) => sum + pos.unrealizedPnL + pos.realizedPnL, 0);
      state.dayPnL = action.payload.reduce((sum, pos) => sum + (pos.dayPnL || 0), 0);
      state.unrealizedPnL = action.payload.reduce((sum, pos) => sum + pos.unrealizedPnL, 0);
      state.realizedPnL = action.payload.reduce((sum, pos) => sum + pos.realizedPnL, 0);
      
      state.lastUpdated = new Date().toISOString();
      state.isLoading = false;
    },
    updatePosition: (state, action: PayloadAction<Position>) => {
      const updatedPosition = action.payload;
      const index = state.positions.findIndex(
        pos => pos.symbol === updatedPosition.symbol && pos.accountId === updatedPosition.accountId
      );
      
      if (index !== -1) {
        state.positions[index] = updatedPosition;
      } else {
        state.positions.push(updatedPosition);
      }
      
      // Recalculate totals
      state.totalValue = state.positions.reduce((sum, pos) => sum + pos.marketValue, 0);
      state.totalPnL = state.positions.reduce((sum, pos) => sum + pos.unrealizedPnL + pos.realizedPnL, 0);
      state.dayPnL = state.positions.reduce((sum, pos) => sum + (pos.dayPnL || 0), 0);
      state.unrealizedPnL = state.positions.reduce((sum, pos) => sum + pos.unrealizedPnL, 0);
      state.realizedPnL = state.positions.reduce((sum, pos) => sum + pos.realizedPnL, 0);
      
      state.lastUpdated = new Date().toISOString();
      
      // Update selected position if it's the same
      if (state.selectedPosition && 
          state.selectedPosition.symbol === updatedPosition.symbol && 
          state.selectedPosition.accountId === updatedPosition.accountId) {
        state.selectedPosition = updatedPosition;
      }
    },
    removePosition: (state, action: PayloadAction<{ symbol: string; accountId: string }>) => {
      const { symbol, accountId } = action.payload;
      state.positions = state.positions.filter(
        pos => !(pos.symbol === symbol && pos.accountId === accountId)
      );
      
      // Recalculate totals
      state.totalValue = state.positions.reduce((sum, pos) => sum + pos.marketValue, 0);
      state.totalPnL = state.positions.reduce((sum, pos) => sum + pos.unrealizedPnL + pos.realizedPnL, 0);
      state.dayPnL = state.positions.reduce((sum, pos) => sum + (pos.dayPnL || 0), 0);
      state.unrealizedPnL = state.positions.reduce((sum, pos) => sum + pos.unrealizedPnL, 0);
      state.realizedPnL = state.positions.reduce((sum, pos) => sum + pos.realizedPnL, 0);
      
      state.lastUpdated = new Date().toISOString();
      
      // Clear selected position if it was the removed one
      if (state.selectedPosition && 
          state.selectedPosition.symbol === symbol && 
          state.selectedPosition.accountId === accountId) {
        state.selectedPosition = null;
      }
    },
    setSelectedPosition: (state, action: PayloadAction<Position | null>) => {
      state.selectedPosition = action.payload;
    },
    setGroupBy: (state, action: PayloadAction<PositionState['groupBy']>) => {
      state.groupBy = action.payload;
    },
    setSortBy: (state, action: PayloadAction<{ sortBy: PositionState['sortBy']; sortOrder: PositionState['sortOrder'] }>) => {
      state.sortBy = action.payload.sortBy;
      state.sortOrder = action.payload.sortOrder;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearPositions: (state) => {
      state.positions = [];
      state.totalValue = 0;
      state.totalPnL = 0;
      state.dayPnL = 0;
      state.unrealizedPnL = 0;
      state.realizedPnL = 0;
      state.selectedPosition = null;
      state.lastUpdated = null;
    },
  },
});

export const {
  setLoading,
  setPositions,
  updatePosition,
  removePosition,
  setSelectedPosition,
  setGroupBy,
  setSortBy,
  setError,
  clearError,
  clearPositions,
} = positionSlice.actions;

export default positionSlice.reducer;
