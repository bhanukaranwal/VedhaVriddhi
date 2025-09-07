import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = process.env.REACT_APP_ANALYTICS_URL || 'http://localhost:8003';

interface PortfolioAnalytics {
  portfolio_id: string;
  summary: {
    total_value: number;
    total_pnl: number;
    position_count: number;
    last_updated: string;
  };
  allocation: {
    by_instrument_type: Record<string, { value: number; percentage: number; count: number }>;
    by_sector: Record<string, { value: number; percentage: number; count: number }>;
    by_rating: Record<string, { value: number; percentage: number; count: number }>;
    by_maturity: Record<string, { value: number; percentage: number; count: number }>;
  };
  risk_metrics: {
    volatility: number;
    sharpe_ratio: number;
    max_drawdown: number;
    var_95: number;
    var_99: number;
  };
  duration_metrics: {
    modified_duration: number;
    macaulay_duration: number;
    convexity: number;
    dv01: number;
  };
  credit_analysis: {
    average_rating: string;
    investment_grade_percentage: number;
    high_yield_percentage: number;
  };
}

interface YieldCurveData {
  government: Array<{
    tenor: number;
    tenor_label: string;
    yield: number;
    maturity_date: string;
    timestamp: string;
  }>;
  corporate: Array<{
    tenor: number;
    tenor_label: string;
    yield: number;
    maturity_date: string;
    timestamp: string;
  }>;
}

interface PerformanceAttribution {
  portfolio_id: string;
  total_return: number;
  benchmark_return: number;
  active_return: number;
  attribution: {
    selection: number;
    allocation: number;
    interaction: number;
    total: number;
  };
  sector_attribution: Record<string, number>;
}

class AnalyticsService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  constructor() {
    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('vedhavriddhi_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  async getPortfolioAnalytics(portfolioId: string): Promise<PortfolioAnalytics> {
    const response: AxiosResponse<PortfolioAnalytics> = await this.api.get(
      `/analytics/portfolio/${portfolioId}`
    );
    return response.data;
  }

  async getYieldCurves(): Promise<YieldCurveData> {
    const [govResponse, corpResponse] = await Promise.all([
      this.api.get('/yield-curve/government'),
      this.api.get('/yield-curve/corporate')
    ]);

    return {
      government: govResponse.data.data || [],
      corporate: corpResponse.data.data || []
    };
  }

  async getPerformanceAttribution(
    portfolioId: string, 
    timeRange: string
  ): Promise<PerformanceAttribution> {
    const response: AxiosResponse<PerformanceAttribution> = await this.api.get(
      `/analytics/attribution/${portfolioId}`,
      { params: { period: timeRange } }
    );
    return response.data;
  }

  async runScenarioAnalysis(
    portfolioId: string,
    scenarios: string[]
  ): Promise<any> {
    const response = await this.api.post('/analytics/scenario-analysis', {
      portfolio_id: portfolioId,
      scenarios: scenarios
    });
    return response.data;
  }

  async getCreditSpreads(filters?: {
    sector?: string;
    rating?: string;
    maturity_bucket?: string;
  }): Promise<any> {
    const response = await this.api.get('/analytics/credit-spreads', {
      params: filters
    });
    return response.data;
  }

  async getMLPrediction(
    modelType: string,
    features: number[],
    horizon = 1
  ): Promise<any> {
    const response = await this.api.post('/ml/predict', {
      model_type: modelType,
      features: features,
      horizon: horizon
    });
    return response.data;
  }
}

export const analyticsService = new AnalyticsService();
