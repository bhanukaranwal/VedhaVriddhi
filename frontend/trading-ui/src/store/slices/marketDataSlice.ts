import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface MarketData {
  symbol: string;
  bidPrice?: number;
  askPrice?: number;
  lastPrice?: number;
  volume: number;
  timestamp: string;
  yieldToMaturity?: number;
  duration?: number;
  accruedInterest?: number;
  change?: number;
  changePercent?: number;
}

interface YieldCurvePoint {
  tenor: string;
  yield: number;
  price: number;
  timestamp: string;
}

interface MarketDataState {
  marketData: Record<string, MarketData>;
  yieldCurve: YieldCurvePoint[];
  topMovers: Array<{
    symbol: string;
    lastPrice: number;
    change: number;
    changePercent: number;
    volume: number;
  }>;
  marketSummary: {
    totalVolume: number;
    totalValue: number;
    activeInstruments: number;
    avgYield: number;
  } | null;
  subscriptions: Set<string>;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
  connectionStatus: 'connected' | 'disconnected' | 'connecting';
}

const initialState: MarketDataState = {
  marketData: {},
  yieldCurve: [],
  topMovers: [],
  marketSummary: null,
  subscriptions: new Set(),
  isLoading: false,
  error: null,
  lastUpdated: null,
  connectionStatus: 'disconnected',
};

const marketDataSlice = createSlice({
  name: 'marketData',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setConnectionStatus: (state, action: PayloadAction<'connected' | 'disconnected' | 'connecting'>) => {
      state.connectionStatus = action.payload;
    },
    updateMarketData: (state, action: PayloadAction<MarketData>) => {
      const data = action.payload;
      state.marketData[data.symbol] = data;
      state.lastUpdated = new Date().toISOString();
    },
    setBulkMarketData: (state, action: PayloadAction<MarketData[]>) => {
      const dataArray = action.payload;
      dataArray.forEach(data => {
        state.marketData[data.symbol] = data;
      });
      state.lastUpdated = new Date().toISOString();
      state.isLoading = false;
    },
    setYieldCurve: (state, action: PayloadAction<YieldCurvePoint[]>) => {
      state.yieldCurve = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    setTopMovers: (state, action: PayloadAction<MarketDataState['topMovers']>) => {
      state.topMovers = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    setMarketSummary: (state, action: PayloadAction<MarketDataState['marketSummary']>) => {
      state.marketSummary = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    addSubscription: (state, action: PayloadAction<string>) => {
      state.subscriptions.add(action.payload);
    },
    removeSubscription: (state, action: PayloadAction<string>) => {
      state.subscriptions.delete(action.payload);
    },
    clearSubscriptions: (state) => {
      state.subscriptions.clear();
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearMarketData: (state) => {
      state.marketData = {};
      state.yieldCurve = [];
      state.topMovers = [];
      state.marketSummary = null;
      state.subscriptions.clear();
      state.lastUpdated = null;
    },
  },
});

export const {
  setLoading,
  setConnectionStatus,
  updateMarketData,
  setBulkMarketData,
  setYieldCurve,
  setTopMovers,
  setMarketSummary,
  addSubscription,
  removeSubscription,
  clearSubscriptions,
  setError,
  clearError,
  clearMarketData,
} = marketDataSlice.actions;

export default marketDataSlice.reducer;
