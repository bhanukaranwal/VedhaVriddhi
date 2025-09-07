import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = process.env.REACT_APP_RISK_URL || 'http://localhost:8004';

interface StressTestRequest {
  portfolio_id: string;
  scenarios: string[];
  confidence_level: number;
}

class RiskService {
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

  async getPortfolioRisk(portfolioId: string): Promise<any> {
    const response: AxiosResponse = await this.api.get(`/risk/portfolio/${portfolioId}`);
    return response.data;
  }

  async getRiskLimits(portfolioId: string): Promise<any> {
    const response: AxiosResponse = await this.api.get(`/risk/limits/${portfolioId}`);
    return response.data;
  }

  async runStressTest(request: StressTestRequest): Promise<any> {
    const response: AxiosResponse = await this.api.post('/risk/stress-test', request);
    return response.data;
  }

  async getStressTestResults(portfolioId: string): Promise<any> {
    const response: AxiosResponse = await this.api.get(`/risk/stress-test-results/${portfolioId}`);
    return response.data;
  }
}

export const riskService = new RiskService();
