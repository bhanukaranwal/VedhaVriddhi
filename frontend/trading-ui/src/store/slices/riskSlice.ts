import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface RiskLimit {
  name: string;
  type: 'position' | 'concentration' | 'var' | 'exposure';
  current: number;
  limit: number;
  utilization: number;
  status: 'normal' | 'warning' | 'breach';
  threshold: {
    warning: number;
    critical: number;
  };
}

interface RiskMetrics {
  var: {
    oneDay: number;
    tenDay: number;
    method: 'parametric' | 'historical' | 'monte_carlo';
  };
  expectedShortfall: number;
  maxDrawdown: number;
  volatility: number;
  beta: number;
  trackingError: number;
  informationRatio: number;
  sharpeRatio: number;
  timestamp: string;
}

interface StressTestResult {
  scenarioName: string;
  type: 'interest_rate' | 'credit' | 'liquidity' | 'market';
  parameters: Record<string, number>;
  results: {
    portfolioValue: number;
    pnlImpact: number;
    percentageImpact: number;
  };
  timestamp: string;
}

interface RiskViolation {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  details: Record<string, any>;
  timestamp: string;
  status: 'active' | 'acknowledged' | 'resolved';
  resolvedAt?: string;
  resolvedBy?: string;
}

interface RiskState {
  riskMetrics: RiskMetrics | null;
  riskLimits: RiskLimit[];
  stressTestResults: StressTestResult[];
  violations: RiskViolation[];
  concentrationRisk: {
    byIssuer: Array<{ issuer: string; exposure: number; percentage: number }>;
    bySector: Array<{ sector: string; exposure: number; percentage: number }>;
    byRating: Array<{ rating: string; exposure: number; percentage: number }>;
    byMaturity: Array<{ maturityBucket: string; exposure: number; percentage: number }>;
  };
  liquidityMetrics: {
    portfolioLiquidity: number;
    liquidityAtRisk: number;
    fundingGap: number;
    liquidityBuffer: number;
  };
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
  alertsEnabled: boolean;
}

const initialState: RiskState = {
  riskMetrics: null,
  riskLimits: [],
  stressTestResults: [],
  violations: [],
  concentrationRisk: {
    byIssuer: [],
    bySector: [],
    byRating: [],
    byMaturity: [],
  },
  liquidityMetrics: {
    portfolioLiquidity: 0,
    liquidityAtRisk: 0,
    fundingGap: 0,
    liquidityBuffer: 0,
  },
  isLoading: false,
  error: null,
  lastUpdated: null,
  alertsEnabled: true,
};

const riskSlice = createSlice({
  name: 'risk',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setRiskMetrics: (state, action: PayloadAction<RiskMetrics>) => {
      state.riskMetrics = action.payload;
      state.lastUpdated = new Date().toISOString();
      state.isLoading = false;
    },
    setRiskLimits: (state, action: PayloadAction<RiskLimit[]>) => {
      state.riskLimits = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    updateRiskLimit: (state, action: PayloadAction<RiskLimit>) => {
      const updatedLimit = action.payload;
      const index = state.riskLimits.findIndex(limit => limit.name === updatedLimit.name);
      
      if (index !== -1) {
        state.riskLimits[index] = updatedLimit;
      } else {
        state.riskLimits.push(updatedLimit);
      }
      
      state.lastUpdated = new Date().toISOString();
    },
    setStressTestResults: (state, action: PayloadAction<StressTestResult[]>) => {
      state.stressTestResults = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    addStressTestResult: (state, action: PayloadAction<StressTestResult>) => {
      const newResult = action.payload;
      const existingIndex = state.stressTestResults.findIndex(
        result => result.scenarioName === newResult.scenarioName && result.type === newResult.type
      );
      
      if (existingIndex !== -1) {
        state.stressTestResults[existingIndex] = newResult;
      } else {
        state.stressTestResults.push(newResult);
      }
      
      state.lastUpdated = new Date().toISOString();
    },
    setViolations: (state, action: PayloadAction<RiskViolation[]>) => {
      state.violations = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    addViolation: (state, action: PayloadAction<RiskViolation>) => {
      state.violations.unshift(action.payload);
      state.lastUpdated = new Date().toISOString();
    },
    updateViolation: (state, action: PayloadAction<RiskViolation>) => {
      const updatedViolation = action.payload;
      const index = state.violations.findIndex(v => v.id === updatedViolation.id);
      
      if (index !== -1) {
        state.violations[index] = updatedViolation;
        state.lastUpdated = new Date().toISOString();
      }
    },
    acknowledgeViolation: (state, action: PayloadAction<{ id: string; acknowledgedBy: string }>) => {
      const { id, acknowledgedBy } = action.payload;
      const violation = state.violations.find(v => v.id === id);
      
      if (violation) {
        violation.status = 'acknowledged';
        violation.resolvedBy = acknowledgedBy;
        violation.resolvedAt = new Date().toISOString();
        state.lastUpdated = new Date().toISOString();
      }
    },
    setConcentrationRisk: (state, action: PayloadAction<RiskState['concentrationRisk']>) => {
      state.concentrationRisk = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    setLiquidityMetrics: (state, action: PayloadAction<RiskState['liquidityMetrics']>) => {
      state.liquidityMetrics = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    setAlertsEnabled: (state, action: PayloadAction<boolean>) => {
      state.alertsEnabled = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearRiskData: (state) => {
      state.riskMetrics = null;
      state.riskLimits = [];
      state.stressTestResults = [];
      state.violations = [];
      state.concentrationRisk = {
        byIssuer: [],
        bySector: [],
        byRating: [],
        byMaturity: [],
      };
      state.liquidityMetrics = {
        portfolioLiquidity: 0,
        liquidityAtRisk: 0,
        fundingGap: 0,
        liquidityBuffer: 0,
      };
      state.lastUpdated = null;
    },
  },
});

export const {
  setLoading,
  setRiskMetrics,
  setRiskLimits,
  updateRiskLimit,
  setStressTestResults,
  addStressTestResult,
  setViolations,
  addViolation,
  updateViolation,
  acknowledgeViolation,
  setConcentrationRisk,
  setLiquidityMetrics,
  setAlertsEnabled,
  setError,
  clearError,
  clearRiskData,
} = riskSlice.actions;

export default riskSlice.reducer;
