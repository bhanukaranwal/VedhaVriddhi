import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Trade {
  id: string;
  symbol: string;
  buyerOrderId: string;
  sellerOrderId: string;
  quantity: number;
  price: number;
  timestamp: string;
  tradeType: string;
  side?: 'buy' | 'sell';
}

interface TradeState {
  trades: Trade[];
  recentTrades: Trade[];
  tradeHistory: Trade[];
  selectedTrade: Trade | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
  filters: {
    symbol?: string;
    dateRange?: { start: string; end: string };
    tradeType?: string;
  };
}

const initialState: TradeState = {
  trades: [],
  recentTrades: [],
  tradeHistory: [],
  selectedTrade: null,
  isLoading: false,
  error: null,
  lastUpdated: null,
  filters: {},
};

const tradeSlice = createSlice({
  name: 'trades',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setTrades: (state, action: PayloadAction<Trade[]>) => {
      state.trades = action.payload;
      state.recentTrades = action.payload.slice(0, 50);
      state.lastUpdated = new Date().toISOString();
      state.isLoading = false;
    },
    addTrade: (state, action: PayloadAction<Trade>) => {
      const newTrade = action.payload;
      state.trades.unshift(newTrade);
      state.recentTrades.unshift(newTrade);
      
      // Keep only last 50 recent trades
      if (state.recentTrades.length > 50) {
        state.recentTrades = state.recentTrades.slice(0, 50);
      }
      
      state.lastUpdated = new Date().toISOString();
    },
    setTradeHistory: (state, action: PayloadAction<Trade[]>) => {
      state.tradeHistory = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    setSelectedTrade: (state, action: PayloadAction<Trade | null>) => {
      state.selectedTrade = action.payload;
    },
    setFilters: (state, action: PayloadAction<TradeState['filters']>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {};
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearTrades: (state) => {
      state.trades = [];
      state.recentTrades = [];
      state.tradeHistory = [];
      state.selectedTrade = null;
      state.lastUpdated = null;
    },
  },
});

export const {
  setLoading,
  setTrades,
  addTrade,
  setTradeHistory,
  setSelectedTrade,
  setFilters,
  clearFilters,
  setError,
  clearError,
  clearTrades,
} = tradeSlice.actions;

export default tradeSlice.reducer;
