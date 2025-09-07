import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface YieldCurveData {
  date: string;
  curves: Array<{
    tenor: string;
    yield: number;
    price: number;
  }>;
}

interface CreditSpread {
  symbol: string;
  creditSpread: number;
  benchmarkYield: number;
  bondYield: number;
  rating: string;
  sector: string;
  timestamp: string;
}

interface ScenarioAnalysis {
  scenarioName: string;
  parameters: Record<string, number>;
  results: {
    portfolioValue: number;
    pnlImpact: number;
    riskMetrics: {
      var: number;
      expectedShortfall: number;
    };
  };
}

interface AnalyticsState {
  yieldCurves: {
    government: YieldCurveData[];
    corporate: YieldCurveData[];
    municipal: YieldCurveData[];
  };
  creditSpreads: CreditSpread[];
  scenarioAnalysis: ScenarioAnalysis[];
  marketTrends: {
    yieldTrends: Array<{ date: string; trend: 'steepening' | 'flattening' | 'parallel_shift' }>;
    creditTrends: Array<{ date: string; sector: string; trend: 'tightening' | 'widening' }>;
  };
  correlationMatrix: Array<{
    asset1: string;
    asset2: string;
    correlation: number;
    timestamp: string;
  }>;
  volatilitySurface: Array<{
    underlying: string;
    tenor: string;
    strike: number;
    volatility: number;
  }>;
  selectedAnalysis: string | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

const initialState: AnalyticsState = {
  yieldCurves: {
    government: [],
    corporate: [],
    municipal: [],
  },
  creditSpreads: [],
  scenarioAnalysis: [],
  marketTrends: {
    yieldTrends: [],
    creditTrends: [],
  },
  correlationMatrix: [],
  volatilitySurface: [],
  selectedAnalysis: null,
  isLoading: false,
  error: null,
  lastUpdated: null,
};

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setYieldCurves: (state, action: PayloadAction<{
      type: 'government' | 'corporate' | 'municipal';
      data: YieldCurveData[];
    }>) => {
      const { type, data } = action.payload;
      state.yieldCurves[type] = data;
      state.lastUpdated = new Date().toISOString();
      state.isLoading = false;
    },
    updateYieldCurve: (state, action: PayloadAction<{
      type: 'government' | 'corporate' | 'municipal';
      data: YieldCurveData;
    }>) => {
      const { type, data } = action.payload;
      const existingIndex = state.yieldCurves[type].findIndex(curve => curve.date === data.date);
      
      if (existingIndex !== -1) {
        state.yieldCurves[type][existingIndex] = data;
      } else {
        state.yieldCurves[type].push(data);
        // Keep only last 100 data points
        if (state.yieldCurves[type].length > 100) {
          state.yieldCurves[type] = state.yieldCurves[type].slice(-100);
        }
      }
      
      state.lastUpdated = new Date().toISOString();
    },
    setCreditSpreads: (state, action: PayloadAction<CreditSpread[]>) => {
      state.creditSpreads = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    updateCreditSpread: (state, action: PayloadAction<CreditSpread>) => {
      const updatedSpread = action.payload;
      const existingIndex = state.creditSpreads.findIndex(spread => spread.symbol === updatedSpread.symbol);
      
      if (existingIndex !== -1) {
        state.creditSpreads[existingIndex] = updatedSpread;
      } else {
        state.creditSpreads.push(updatedSpread);
      }
      
      state.lastUpdated = new Date().toISOString();
    },
    setScenarioAnalysis: (state, action: PayloadAction<ScenarioAnalysis[]>) => {
      state.scenarioAnalysis = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    addScenarioAnalysis: (state, action: PayloadAction<ScenarioAnalysis>) => {
      const newScenario = action.payload;
      const existingIndex = state.scenarioAnalysis.findIndex(scenario => scenario.scenarioName === newScenario.scenarioName);
      
      if (existingIndex !== -1) {
        state.scenarioAnalysis[existingIndex] = newScenario;
      } else {
        state.scenarioAnalysis.push(newScenario);
      }
      
      state.lastUpdated = new Date().toISOString();
    },
    setMarketTrends: (state, action: PayloadAction<AnalyticsState['marketTrends']>) => {
      state.marketTrends = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    setCorrelationMatrix: (state, action: PayloadAction<AnalyticsState['correlationMatrix']>) => {
      state.correlationMatrix = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    setVolatilitySurface: (state, action: PayloadAction<AnalyticsState['volatilitySurface']>) => {
      state.volatilitySurface = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    setSelectedAnalysis: (state, action: PayloadAction<string | null>) => {
      state.selectedAnalysis = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearAnalytics: (state) => {
      state.yieldCurves = { government: [], corporate: [], municipal: [] };
      state.creditSpreads = [];
      state.scenarioAnalysis = [];
      state.marketTrends = { yieldTrends: [], creditTrends: [] };
      state.correlationMatrix = [];
      state.volatilitySurface = [];
      state.selectedAnalysis = null;
      state.lastUpdated = null;
    },
  },
});

export const {
  setLoading,
  setYieldCurves,
  updateYieldCurve,
  setCreditSpreads,
  updateCreditSpread,
  setScenarioAnalysis,
  addScenarioAnalysis,
  setMarketTrends,
  setCorrelationMatrix,
  setVolatilitySurface,
  setSelectedAnalysis,
  setError,
  clearError,
  clearAnalytics,
} = analyticsSlice.actions;

export default analyticsSlice.reducer;
