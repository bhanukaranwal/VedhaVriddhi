import axios, { AxiosResponse } from 'axios';
import { Order, Trade, Position, OrderRequest } from '../../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8002';

class TradingService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  constructor() {
    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('vedhavriddhi_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired, redirect to login
          localStorage.removeItem('vedhavriddhi_token');
          localStorage.removeItem('vedhavriddhi_user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async getOrders(limit = 100, offset = 0): Promise<Order[]> {
    const response: AxiosResponse<Order[]> = await this.api.get('/orders', {
      params: { limit, offset },
    });
    return response.data;
  }

  async getOrder(orderId: string): Promise<Order> {
    const response: AxiosResponse<Order> = await this.api.get(`/orders/${orderId}`);
    return response.data;
  }

  async submitOrder(orderRequest: OrderRequest): Promise<Order> {
    const response: AxiosResponse<Order> = await this.api.post('/orders', orderRequest);
    return response.data;
  }

  async cancelOrder(orderId: string): Promise<boolean> {
    const response: AxiosResponse<{ cancelled: boolean }> = await this.api.delete(`/orders/${orderId}`);
    return response.data.cancelled;
  }

  async modifyOrder(orderId: string, modifications: Partial<OrderRequest>): Promise<Order> {
    const response: AxiosResponse<Order> = await this.api.put(`/orders/${orderId}`, modifications);
    return response.data;
  }

  async getTrades(limit = 100, offset = 0): Promise<Trade[]> {
    const response: AxiosResponse<Trade[]> = await this.api.get('/trades', {
      params: { limit, offset },
    });
    return response.data;
  }

  async getTradeHistory(symbol?: string, startDate?: string, endDate?: string): Promise<Trade[]> {
    const response: AxiosResponse<Trade[]> = await this.api.get('/trades/history', {
      params: { symbol, start_date: startDate, end_date: endDate },
    });
    return response.data;
  }

  async getPositions(accountId?: string): Promise<Position[]> {
    const response: AxiosResponse<Position[]> = await this.api.get('/positions', {
      params: { account_id: accountId },
    });
    return response.data;
  }

  async getPosition(symbol: string, accountId?: string): Promise<Position> {
    const response: AxiosResponse<Position> = await this.api.get(`/positions/${symbol}`, {
      params: { account_id: accountId },
    });
    return response.data;
  }

  async getPortfolioSummary(accountId?: string): Promise<{
    totalValue: number;
    totalPnL: number;
    dayPnL: number;
    unrealizedPnL: number;
    realizedPnL: number;
    positions: Position[];
  }> {
    const response = await this.api.get('/portfolio/summary', {
      params: { account_id: accountId },
    });
    return response.data;
  }

  async getOrderBook(symbol: string): Promise<{
    symbol: string;
    bids: Array<{ price: number; quantity: number; orderCount: number }>;
    asks: Array<{ price: number; quantity: number; orderCount: number }>;
    lastUpdate: string;
  }> {
    const response = await this.api.get(`/market-data/orderbook/${symbol}`);
    return response.data;
  }

  async getRiskMetrics(accountId?: string): Promise<{
    var: number;
    expectedShortfall: number;
    maxDrawdown: number;
    sharpeRatio: number;
    beta: number;
    concentrationRisk: number;
  }> {
    const response = await this.api.get('/risk/metrics', {
      params: { account_id: accountId },
    });
    return response.data;
  }

  async getComplianceStatus(): Promise<{
    violations: Array<{
      id: string;
      type: string;
      severity: string;
      description: string;
      timestamp: string;
    }>;
    limits: Array<{
      name: string;
      current: number;
      limit: number;
      utilization: number;
    }>;
  }> {
    const response = await this.api.get('/compliance/status');
    return response.data;
  }

  // Batch operations
  async submitBulkOrders(orders: OrderRequest[]): Promise<{
    successful: Order[];
    failed: Array<{ order: OrderRequest; error: string }>;
  }> {
    const response = await this.api.post('/orders/bulk', { orders });
    return response.data;
  }

  async cancelMultipleOrders(orderIds: string[]): Promise<{
    cancelled: string[];
    failed: Array<{ orderId: string; error: string }>;
  }> {
    const response = await this.api.post('/orders/cancel-bulk', { order_ids: orderIds });
    return response.data;
  }

  // Real-time updates subscription
  async subscribeToOrderUpdates(callback: (order: Order) => void): Promise<() => void> {
    // This would typically use WebSocket
    // For now, we'll use polling as a fallback
    const intervalId = setInterval(async () => {
      try {
        const orders = await this.getOrders(10);
        orders.forEach(callback);
      } catch (error) {
        console.error('Failed to fetch order updates:', error);
      }
    }, 5000);

    return () => clearInterval(intervalId);
  }

  // Performance analytics
  async getPerformanceAnalytics(accountId?: string, period = '1M'): Promise<{
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
    };
  }> {
    const response = await this.api.get('/analytics/performance', {
      params: { account_id: accountId, period },
    });
    return response.data;
  }
}

export const tradingService = new TradingService();
