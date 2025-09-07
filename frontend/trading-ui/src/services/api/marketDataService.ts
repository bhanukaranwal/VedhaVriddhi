import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8002';

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

interface Instrument {
  isin: string;
  symbol: string;
  instrumentName: string;
  issuer: string;
  bondType: string;
  faceValue: number;
  couponRate?: number;
  maturityDate: string;
  currency: string;
  exchange: string;
  sector?: string;
  rating?: string;
}

interface YieldCurveData {
  date: string;
  tenor: string;
  yield: number;
  price: number;
}

interface HistoricalDataRequest {
  symbols: string[];
  startDate: string;
  endDate: string;
  interval?: string;
}

class MarketDataService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 15000,
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

  async getMarketData(symbol: string): Promise<MarketData> {
    const response: AxiosResponse<MarketData> = await this.api.get(`/market-data/${symbol}`);
    return response.data;
  }

  async getAllMarketData(): Promise<MarketData[]> {
    const response: AxiosResponse<{ data: MarketData[] }> = await this.api.get('/market-data');
    return response.data.data;
  }

  async getHistoricalData(request: HistoricalDataRequest): Promise<Array<{
    symbol: string;
    timestamp: string;
    price: number;
    volume: number;
    yield?: number;
  }>> {
    const response = await this.api.post('/market-data/historical', request);
    return response.data.data;
  }

  async getInstruments(): Promise<Instrument[]> {
    const response: AxiosResponse<{ instruments: Instrument[] }> = await this.api.get('/instruments');
    return response.data.instruments;
  }

  async getInstrument(isin: string): Promise<Instrument> {
    const response: AxiosResponse<Instrument> = await this.api.get(`/instruments/${isin}`);
    return response.data;
  }

  async searchInstruments(query: string, filters?: {
    bondType?: string;
    issuer?: string;
    rating?: string;
    sector?: string;
    exchange?: string;
  }): Promise<Instrument[]> {
    const response: AxiosResponse<{ instruments: Instrument[] }> = await this.api.get('/instruments/search', {
      params: { q: query, ...filters },
    });
    return response.data.instruments;
  }

  async getYieldCurve(curveType = 'government', date?: string): Promise<YieldCurveData[]> {
    const response: AxiosResponse<{ data: YieldCurveData[] }> = await this.api.get('/market-data/yield-curve', {
      params: { curve_type: curveType, date },
    });
    return response.data.data;
  }

  async getYieldCurveHistory(
    curveType = 'government',
    startDate: string,
    endDate: string
  ): Promise<Array<{
    date: string;
        curves: YieldCurveData[];
  }>> {
    const response = await this.api.get('/market-data/yield-curve/history', {
      params: { curve_type: curveType, start_date: startDate, end_date: endDate },
    });
    return response.data.data;
  }

  async getTopMovers(count = 10): Promise<Array<{
    symbol: string;
    lastPrice: number;
    change: number;
    changePercent: number;
    volume: number;
  }>> {
    const response = await this.api.get('/market-data/movers', {
      params: { count },
    });
    return response.data.data;
  }

  async getBondCalculations(
    isin: string,
    price: number,
    settlementDate?: string
  ): Promise<{
    yieldToMaturity: number;
    modifiedDuration: number;
    macaulayDuration: number;
    convexity: number;
    accruedInterest: number;
    cleanPrice: number;
    dirtyPrice: number;
  }> {
    const response = await this.api.post('/market-data/calculations', {
      isin,
      price,
      settlement_date: settlementDate,
    });
    return response.data;
  }

  async getCreditSpreads(rating?: string, sector?: string): Promise<Array<{
    symbol: string;
    creditSpread: number;
    benchmarkYield: number;
    bondYield: number;
    rating: string;
    sector: string;
  }>> {
    const response = await this.api.get('/market-data/credit-spreads', {
      params: { rating, sector },
    });
    return response.data.data;
  }

  async getMarketSummary(): Promise<{
    totalVolume: number;
    totalValue: number;
    activeInstruments: number;
    avgYield: number;
    topSectors: Array<{ sector: string; volume: number; value: number }>;
    yieldCurveMovement: { steepening: boolean; parallelShift: number };
  }> {
    const response = await this.api.get('/market-data/summary');
    return response.data;
  }
}

export const marketDataService = new MarketDataService();

