import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Portfolio {
  id: string;
  name: string;
  accountId: string;
  totalValue: number;
  totalPnL: number;
  dayPnL: number;
  unrealizedPnL: number;
  realizedPnL: number;
  cashBalance: number;
  marginUsed: number;
  marginAvailable: number;
  lastUpdated: string;
}

interface PerformanceMetrics {
  returns: Array<{ date: string; value: number }>;
  benchmarkReturns: Array<{ date: string; value: number }>;
  attribution: {
    selection: number;
    allocation: number;
    interaction: number;
    total: number;
  };
  riskMetrics: {
    volatility: number;
    maxDrawdown: number;
    sharpeRatio: number;
    informationRatio: number;
    beta: number;
    trackingError: number;
  };
}

interface AllocationBreakdown {
  byInstrumentType: Array<{ type: string; value: number; percentage: number }>;
  bySector: Array<{ sector: string; value: number; percentage: number }>;
  byRating: Array<{ rating: string; value: number; percentage: number }>;
  byMaturity: Array<{ maturity: string; value: number; percentage: number }>;
  byDuration: Array<{ range: string; value: number; percentage: number }>;
}

interface PortfolioState {
  portfolio: Portfolio | null;
  performanceMetrics: PerformanceMetrics | null;
  allocationBreakdown: AllocationBreakdown | null;
  historicalPerformance: Array<{
    date: string;
    portfolioValue: number;
    pnl: number;
    benchmarkValue: number;
  }>;
  selectedTimeRange: '1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | 'YTD' | 'ALL';
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

const initialState: PortfolioState = {
  portfolio: null,
  performanceMetrics: null,
  allocationBreakdown: null,
  historicalPerformance: [],
  selectedTimeRange: '1M',
  isLoading: false,
  error: null,
  lastUpdated: null,
};

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setPortfolio: (state, action: PayloadAction<Portfolio>) => {
      state.portfolio = action.payload;
      state.lastUpdated = new Date().toISOString();
      state.isLoading = false;
    },
    updatePortfolioValue: (state, action: PayloadAction<{
      totalValue: number;
      totalPnL: number;
      dayPnL: number;
      unrealizedPnL: number;
      realizedPnL: number;
    }>) => {
      if (state.portfolio) {
        const updates = action.payload;
        state.portfolio.totalValue = updates.totalValue;
        state.portfolio.totalPnL = updates.totalPnL;
        state.portfolio.dayPnL = updates.dayPnL;
        state.portfolio.unrealizedPnL = updates.unrealizedPnL;
        state.portfolio.realizedPnL = updates.realizedPnL;
        state.portfolio.lastUpdated = new Date().toISOString();
        state.lastUpdated = new Date().toISOString();
      }
    },
    setPerformanceMetrics: (state, action: PayloadAction<PerformanceMetrics>) => {
      state.performanceMetrics = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    setAllocationBreakdown: (state, action: PayloadAction<AllocationBreakdown>) => {
      state.allocationBreakdown = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    setHistoricalPerformance: (state, action: PayloadAction<PortfolioState['historicalPerformance']>) => {
      state.historicalPerformance = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    addPerformanceData: (state, action: PayloadAction<{
      date: string;
      portfolioValue: number;
      pnl: number;
      benchmarkValue: number;
    }>) => {
      const newData = action.payload;
      const existingIndex = state.historicalPerformance.findIndex(item => item.date === newData.date);
      
      if (existingIndex !== -1) {
        state.historicalPerformance[existingIndex] = newData;
      } else {
        state.historicalPerformance.push(newData);
        // Sort by date
        state.historicalPerformance.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
      }
      
      state.lastUpdated = new Date().toISOString();
    },
    setSelectedTimeRange: (state, action: PayloadAction<PortfolioState['selectedTimeRange']>) => {
      state.selectedTimeRange = action.payload;
    },
    updateCashBalance: (state, action: PayloadAction<number>) => {
      if (state.portfolio) {
        state.portfolio.cashBalance = action.payload;
        state.portfolio.lastUpdated = new Date().toISOString();
        state.lastUpdated = new Date().toISOString();
      }
    },
    updateMarginInfo: (state, action: PayloadAction<{ marginUsed: number; marginAvailable: number }>) => {
      if (state.portfolio) {
        state.portfolio.marginUsed = action.payload.marginUsed;
        state.portfolio.marginAvailable = action.payload.marginAvailable;
        state.portfolio.lastUpdated = new Date().toISOString();
        state.lastUpdated = new Date().toISOString();
      }
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearPortfolio: (state) => {
      state.portfolio = null;
      state.performanceMetrics = null;
      state.allocationBreakdown = null;
      state.historicalPerformance = [];
      state.lastUpdated = null;
    },
  },
});

export const {
  setLoading,
  setPortfolio,
  updatePortfolioValue,
  setPerformanceMetrics,
  setAllocationBreakdown,
  setHistoricalPerformance,
  addPerformanceData,
  setSelectedTimeRange,
  updateCashBalance,
  updateMarginInfo,
  setError,
  clearError,
  clearPortfolio,
} = portfolioSlice.actions;

export default portfolioSlice.reducer;
