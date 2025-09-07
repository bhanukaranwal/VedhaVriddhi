import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  ShowChart,
  Refresh,
  Notifications,
} from '@mui/icons-material';
import { useQuery } from 'react-query';

import { formatCurrency, formatPercentage, formatNumber } from '../../utils/formatting';
import { marketDataService } from '../../services/api/marketDataService';
import { tradingService } from '../../services/api/tradingService';
import { useWebSocket } from '../../hooks/useWebSocket';

interface DashboardStats {
  totalPnL: number;
  dayPnL: number;
  totalValue: number;
  positionsCount: number;
  ordersCount: number;
  tradesCount: number;
}

interface MarketOverview {
  symbol: string;
  lastPrice: number;
  change: number;
  changePercent: number;
  volume: number;
  yield: number;
}

interface RecentTrade {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  price: number;
  timestamp: string;
}

const TradingDashboard: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);
  
  // Fetch dashboard data
  const { data: dashboardStats, refetch: refetchStats } = useQuery<DashboardStats>(
    'dashboardStats',
    async () => {
      const [positions, orders, trades] = await Promise.all([
        tradingService.getPositions(),
        tradingService.getOrders(),
        tradingService.getTrades(),
      ]);
      
      const totalPnL = positions.reduce((sum: number, pos: any) => sum + pos.unrealizedPnL, 0);
      const dayPnL = positions.reduce((sum: number, pos: any) => sum + pos.dayPnL, 0);
      const totalValue = positions.reduce((sum: number, pos: any) => sum + pos.marketValue, 0);
      
      return {
        totalPnL,
        dayPnL,
        totalValue,
        positionsCount: positions.length,
        ordersCount: orders.filter((o: any) => ['pending', 'partially_filled'].includes(o.status)).length,
        tradesCount: trades.filter((t: any) => new Date(t.timestamp).toDateString() === new Date().toDateString()).length,
      };
    },
    { refetchInterval: 30000 }
  );

  const { data: marketOverview } = useQuery<MarketOverview[]>(
    'marketOverview',
    async () => {
      const symbols = ['GSEC10Y', 'GSEC5Y', 'GSEC2Y', 'TBILL91D', 'TBILL182D'];
      const marketData = await Promise.all(
        symbols.map(symbol => marketDataService.getMarketData(symbol))
      );
      
      return marketData.map((data, index) => ({
        symbol: symbols[index],
        lastPrice: data.lastPrice || 0,
        change: data.change || 0,
        changePercent: data.changePercent || 0,
        volume: data.volume || 0,
        yield: data.yieldToMaturity || 0,
      }));
    },
    { refetchInterval: 5000 }
  );

  const { data: recentTrades } = useQuery<RecentTrade[]>(
    'recentTrades',
    async () => {
      const trades = await tradingService.getTrades();
      return trades.slice(0, 10).map((trade: any) => ({
        id: trade.id,
        symbol: trade.symbol,
        side: trade.side,
        quantity: trade.quantity,
        price: trade.price,
        timestamp: trade.timestamp,
      }));
    },
    { refetchInterval: 10000 }
  );

  // WebSocket for real-time updates
  const { lastMessage } = useWebSocket('/ws/orders');

  useEffect(() => {
    if (lastMessage) {
      refetchStats();
    }
  }, [lastMessage, refetchStats]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetchStats();
    setRefreshing(false);
  };

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    change?: number;
    icon: React.ReactNode;
    color?: string;
  }> = ({ title, value, change, icon, color = 'primary' }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography variant="overline" color="text.secondary">
              {title}
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: `${color}.main` }}>
              {value}
            </Typography>
            {change !== undefined && (
              <Box display="flex" alignItems="center" mt={1}>
                {change >= 0 ? (
                  <TrendingUp color="success" fontSize="small" />
                ) : (
                  <TrendingDown color="error" fontSize="small" />
                )}
                <Typography
                  variant="body2"
                  color={change >= 0 ? 'success.main' : 'error.main'}
                  sx={{ ml: 0.5 }}
                >
                  {formatPercentage(Math.abs(change))}
                </Typography>
              </Box>
            )}
          </Box>
          <Box sx={{ color: `${color}.main` }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ height: '100%', overflow: 'auto' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Trading Dashboard
        </Typography>
        <Box>
          <IconButton onClick={handleRefresh} disabled={refreshing}>
            <Refresh />
          </IconButton>
          <IconButton>
            <Notifications />
          </IconButton>
        </Box>
      </Box>

      {refreshing && <LinearProgress sx={{ mb: 2 }} />}

      {/* Key Metrics */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total P&L"
            value={formatCurrency(dashboardStats?.totalPnL || 0)}
            change={dashboardStats?.dayPnL}
            icon={<AccountBalance fontSize="large" />}
            color={dashboardStats?.totalPnL >= 0 ? 'success' : 'error'}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Portfolio Value"
            value={formatCurrency(dashboardStats?.totalValue || 0)}
            icon={<ShowChart fontSize="large" />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Positions"
            value={dashboardStats?.positionsCount || 0}
            icon={<TrendingUp fontSize="large" />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Orders"
            value={dashboardStats?.ordersCount || 0}
            icon={<TrendingDown fontSize="large" />}
            color="warning"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Market Overview */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ height: 400 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Market Overview
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Symbol</TableCell>
                      <TableCell align="right">Price</TableCell>
                      <TableCell align="right">Change</TableCell>
                      <TableCell align="right">Volume</TableCell>
                      <TableCell align="right">Yield</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {marketOverview?.map((item) => (
                      <TableRow key={item.symbol} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {item.symbol}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            {formatCurrency(item.lastPrice)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Box display="flex" alignItems="center" justifyContent="flex-end">
                            {item.change >= 0 ? (
                              <TrendingUp color="success" fontSize="small" />
                            ) : (
                              <TrendingDown color="error" fontSize="small" />
                            )}
                            <Typography
                              variant="body2"
                              color={item.change >= 0 ? 'success.main' : 'error.main'}
                              sx={{ ml: 0.5 }}
                            >
                              {formatPercentage(Math.abs(item.changePercent))}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            {formatNumber(item.volume)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            {formatPercentage(item.yield)}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Trades */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: 400 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Trades
              </Typography>
              <Box sx={{ maxHeight: 320, overflow: 'auto' }}>
                {recentTrades?.map((trade) => (
                  <Box
                    key={trade.id}
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                    p={1}
                    sx={{
                      borderBottom: '1px solid',
                      borderColor: 'divider',
                      '&:last-child': { borderBottom: 'none' },
                    }}
                  >
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {trade.symbol}
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Chip
                          label={trade.side.toUpperCase()}
                          size="small"
                          color={trade.side === 'buy' ? 'success' : 'error'}
                          variant="outlined"
                        />
                        <Typography variant="caption" color="text.secondary">
                          {formatNumber(trade.quantity)}
                        </Typography>
                      </Box>
                    </Box>
                    <Box textAlign="right">
                      <Typography variant="body2" fontWeight="medium">
                        {formatCurrency(trade.price)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(trade.timestamp).toLocaleTimeString()}
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TradingDashboard;
