import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Tab,
  Tabs,
  CircularProgress,
  Alert,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useQuery } from 'react-query';

import { analyticsService } from '../../services/api/analyticsService';
import { formatCurrency, formatPercentage } from '../../utils/formatting';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AnalyticsDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedPortfolio, setSelectedPortfolio] = useState<string>('all');
  const [timeRange, setTimeRange] = useState<string>('1M');

  // Fetch portfolio analytics
  const { data: portfolioAnalytics, isLoading: loadingAnalytics, error: analyticsError } = useQuery(
    ['portfolioAnalytics', selectedPortfolio],
    () => analyticsService.getPortfolioAnalytics(selectedPortfolio),
    { 
      refetchInterval: 30000,
      enabled: selectedPortfolio !== ''
    }
  );

  // Fetch yield curves
  const { data: yieldCurves, isLoading: loadingYieldCurves } = useQuery(
    'yieldCurves',
    () => analyticsService.getYieldCurves(),
    { refetchInterval: 60000 }
  );

  // Fetch performance attribution
  const { data: attribution, isLoading: loadingAttribution } = useQuery(
    ['attribution', selectedPortfolio, timeRange],
    () => analyticsService.getPerformanceAttribution(selectedPortfolio, timeRange),
    { 
      refetchInterval: 300000,
      enabled: selectedPortfolio !== ''
    }
  );

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1'];

  return (
    <Box sx={{ width: '100%', height: '100vh', overflow: 'auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Advanced Analytics
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Portfolio</InputLabel>
            <Select
              value={selectedPortfolio}
              label="Portfolio"
              onChange={(e) => setSelectedPortfolio(e.target.value)}
            >
              <MenuItem value="all">All Portfolios</MenuItem>
              <MenuItem value="portfolio-1">Portfolio 1</MenuItem>
              <MenuItem value="portfolio-2">Portfolio 2</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 100 }}>
            <InputLabel>Period</InputLabel>
            <Select
              value={timeRange}
              label="Period"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="1W">1 Week</MenuItem>
              <MenuItem value="1M">1 Month</MenuItem>
              <MenuItem value="3M">3 Months</MenuItem>
              <MenuItem value="1Y">1 Year</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Portfolio Overview" />
          <Tab label="Yield Curves" />
          <Tab label="Performance Attribution" />
          <Tab label="Risk Analytics" />
          <Tab label="ML Insights" />
        </Tabs>
      </Box>

      <TabPanel value={activeTab} index={0}>
        {loadingAnalytics ? (
          <Box display="flex" justifyContent="center">
            <CircularProgress />
          </Box>
        ) : analyticsError ? (
          <Alert severity="error">Failed to load portfolio analytics</Alert>
        ) : (
          <Grid container spacing={3}>
            {/* Portfolio Summary Cards */}
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Total Value
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {formatCurrency(portfolioAnalytics?.summary?.total_value || 0)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Total P&L
                  </Typography>
                  <Typography 
                    variant="h4" 
                    color={portfolioAnalytics?.summary?.total_pnl >= 0 ? 'success.main' : 'error.main'}
                  >
                    {formatCurrency(portfolioAnalytics?.summary?.total_pnl || 0)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Modified Duration
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {portfolioAnalytics?.duration_metrics?.modified_duration?.toFixed(2) || '0.00'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Positions
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {portfolioAnalytics?.summary?.position_count || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Asset Allocation Breakdown */}
            <Grid item xs={12} md={6}>
              <Card sx={{ height: 400 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Asset Allocation by Type
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={portfolioAnalytics?.allocation?.by_instrument_type ? 
                          Object.entries(portfolioAnalytics.allocation.by_instrument_type).map(([key, value]: [string, any]) => ({
                            name: key.replace('_', ' ').toUpperCase(),
                            value: value.percentage
                          })) : []
                        }
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                      >
                        {portfolioAnalytics?.allocation?.by_instrument_type && 
                          Object.keys(portfolioAnalytics.allocation.by_instrument_type).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                          ))
                        }
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Sector Allocation */}
            <Grid item xs={12} md={6}>
              <Card sx={{ height: 400 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Sector Allocation
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={portfolioAnalytics?.allocation?.by_sector ? 
                        Object.entries(portfolioAnalytics.allocation.by_sector).map(([key, value]: [string, any]) => ({
                          sector: key,
                          percentage: value.percentage
                        })) : []
                      }
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="sector" />
                      <YAxis />
                      <Tooltip formatter={(value) => `${value}%`} />
                      <Bar dataKey="percentage" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Risk Metrics */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Risk Metrics
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={3}>
                      <Typography variant="body2" color="text.secondary">
                        Volatility
                      </Typography>
                      <Typography variant="h6">
                        {formatPercentage(portfolioAnalytics?.risk_metrics?.volatility || 0)}
                      </Typography>
                    </Grid>
                    <Grid item xs={3}>
                      <Typography variant="body2" color="text.secondary">
                        Sharpe Ratio
                      </Typography>
                      <Typography variant="h6">
                        {portfolioAnalytics?.risk_metrics?.sharpe_ratio?.toFixed(2) || '0.00'}
                      </Typography>
                    </Grid>
                    <Grid item xs={3}>
                      <Typography variant="body2" color="text.secondary">
                        Max Drawdown
                      </Typography>
                      <Typography variant="h6" color="error.main">
                        {formatPercentage(portfolioAnalytics?.risk_metrics?.max_drawdown || 0)}
                      </Typography>
                    </Grid>
                    <Grid item xs={3}>
                      <Typography variant="body2" color="text.secondary">
                        VaR (95%)
                      </Typography>
                      <Typography variant="h6" color="warning.main">
                        {formatPercentage(portfolioAnalytics?.risk_metrics?.var_95 || 0)}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        {loadingYieldCurves ? (
          <Box display="flex" justifyContent="center">
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card sx={{ height: 500 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Government Yield Curve
                  </Typography>
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={yieldCurves?.government || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="tenor_label" />
                      <YAxis />
                      <Tooltip formatter={(value) => `${value}%`} />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="yield" 
                        stroke="#8884d8" 
                        strokeWidth={2}
                        name="Yield (%)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        {loadingAttribution ? (
          <Box display="flex" justifyContent="center">
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Performance Attribution
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Security Selection
                      </Typography>
                      <Typography variant="h6">
                        {formatPercentage(attribution?.attribution?.selection || 0)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Asset Allocation
                      </Typography>
                      <Typography variant="h6">
                        {formatPercentage(attribution?.attribution?.allocation || 0)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Interaction Effect
                      </Typography>
                      <Typography variant="h6">
                        {formatPercentage(attribution?.attribution?.interaction || 0)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Total Active Return
                      </Typography>
                      <Typography variant="h6" color="primary">
                        {formatPercentage(attribution?.attribution?.total || 0)}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        <Typography variant="h6">Risk Analytics coming soon...</Typography>
      </TabPanel>

      <TabPanel value={activeTab} index={4}>
        <Typography variant="h6">ML Insights coming soon...</Typography>
      </TabPanel>
    </Box>
  );
};

export default AnalyticsDashboard;
