import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Alert,
  Button,
  Tab,
  Tabs,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Warning,
  Error,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  Speed,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

import { riskService } from '../../services/api/riskService';
import { formatCurrency, formatPercentage } from '../../utils/formatting';

interface RiskMetrics {
  var_95_1d: number;
  var_99_1d: number;
  expected_shortfall_95: number;
  expected_shortfall_99: number;
  volatility: number;
  max_drawdown: number;
  sharpe_ratio: number;
}

interface RiskLimit {
  limit_id: string;
  limit_type: string;
  current_value: number;
  limit_value: number;
  utilization_pct: number;
  status: 'green' | 'yellow' | 'red';
}

interface StressTestResult {
  scenario_name: string;
  portfolio_impact_pct: number;
  portfolio_impact_absolute: number;
  confidence_level: number;
}

function TabPanel(props: { children?: React.ReactNode; index: number; value: number }) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const RiskMonitoring: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedPortfolio, setSelectedPortfolio] = useState('portfolio-1');
  const [stressTestDialogOpen, setStressTestDialogOpen] = useState(false);

  // Fetch risk metrics
  const { data: riskMetrics, isLoading: loadingRisk } = useQuery(
    ['riskMetrics', selectedPortfolio],
    () => riskService.getPortfolioRisk(selectedPortfolio),
    { refetchInterval: 30000 }
  );

  // Fetch risk limits
  const { data: riskLimits, isLoading: loadingLimits } = useQuery(
    ['riskLimits', selectedPortfolio],
    () => riskService.getRiskLimits(selectedPortfolio),
    { refetchInterval: 60000 }
  );

  // Fetch stress test results
  const { data: stressTests, isLoading: loadingStress } = useQuery(
    'stressTests',
    () => riskService.getStressTestResults(selectedPortfolio),
    { refetchInterval: 300000 }
  );

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const runStressTest = async () => {
    try {
      await riskService.runStressTest({
        portfolio_id: selectedPortfolio,
        scenarios: ['interest_rate_shock', 'credit_spread_widening', 'liquidity_crisis'],
        confidence_level: 0.95
      });
      setStressTestDialogOpen(false);
    } catch (error) {
      console.error('Stress test failed:', error);
    }
  };

  const getRiskColor = (status: string) => {
    switch (status) {
      case 'green': return 'success';
      case 'yellow': return 'warning';
      case 'red': return 'error';
      default: return 'primary';
    }
  };

  const getRiskIcon = (status: string) => {
    switch (status) {
      case 'green': return <CheckCircle color="success" />;
      case 'yellow': return <Warning color="warning" />;
      case 'red': return <Error color="error" />;
      default: return <Speed color="primary" />;
    }
  };

  return (
    <Box sx={{ width: '100%', height: '100vh', overflow: 'auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Risk Monitoring
        </Typography>
        <Button 
          variant="contained" 
          onClick={() => setStressTestDialogOpen(true)}
          disabled={loadingRisk}
        >
          Run Stress Test
        </Button>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Risk Overview" />
          <Tab label="VaR Analysis" />
          <Tab label="Stress Testing" />
          <Tab label="Risk Limits" />
        </Tabs>
      </Box>

      <TabPanel value={activeTab} index={0}>
        {loadingRisk ? (
          <LinearProgress />
        ) : (
          <Grid container spacing={3}>
            {/* Risk Summary Cards */}
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        1-Day VaR (95%)
                      </Typography>
                      <Typography variant="h4" color="error.main">
                        {formatCurrency(riskMetrics?.var_metrics?.var_95_1d || 0)}
                      </Typography>
                    </Box>
                    <TrendingDown color="error" fontSize="large" />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Expected Shortfall
                      </Typography>
                      <Typography variant="h4" color="warning.main">
                        {formatCurrency(riskMetrics?.var_metrics?.expected_shortfall_95 || 0)}
                      </Typography>
                    </Box>
                    <Warning color="warning" fontSize="large" />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Portfolio Volatility
                      </Typography>
                      <Typography variant="h4" color="info.main">
                        {formatPercentage(riskMetrics?.var_metrics?.volatility || 0)}
                      </Typography>
                    </Box>
                    <Speed color="info" fontSize="large" />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Sharpe Ratio
                      </Typography>
                      <Typography variant="h4" color="success.main">
                        {riskMetrics?.var_metrics?.sharpe_ratio?.toFixed(2) || '0.00'}
                      </Typography>
                    </Box>
                    <TrendingUp color="success" fontSize="large" />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* VaR Trend Chart */}
            <Grid item xs={12} lg={8}>
              <Card sx={{ height: 400 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    VaR Trend Analysis
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={riskMetrics?.historical_var || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip formatter={(value) => formatCurrency(value as number)} />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="var_95"
                        stroke="#f44336"
                        strokeWidth={2}
                        name="VaR 95%"
                      />
                      <Line
                        type="monotone"
                        dataKey="var_99"
                        stroke="#ff9800"
                        strokeWidth={2}
                        name="VaR 99%"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Risk Alerts */}
            <Grid item xs={12} lg={4}>
              <Card sx={{ height: 400 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Risk Alerts
                  </Typography>
                  <Box sx={{ maxHeight: 320, overflow: 'auto' }}>
                    {riskMetrics?.alerts?.map((alert: any, index: number) => (
                      <Alert
                        key={index}
                        severity={alert.severity}
                        sx={{ mb: 1 }}
                        icon={getRiskIcon(alert.severity)}
                      >
                        <Typography variant="body2">
                          {alert.message}
                        </Typography>
                      </Alert>
                    )) || (
                      <Alert severity="success">
                        No active risk alerts
                      </Alert>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Value at Risk Analysis
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Method</TableCell>
                        <TableCell align="right">1-Day VaR (95%)</TableCell>
                        <TableCell align="right">1-Day VaR (99%)</TableCell>
                        <TableCell align="right">10-Day VaR (95%)</TableCell>
                        <TableCell align="right">10-Day VaR (99%)</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell>Historical</TableCell>
                        <TableCell align="right">
                          {formatCurrency(riskMetrics?.var_metrics?.historical_var_95_1d || 0)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(riskMetrics?.var_metrics?.historical_var_99_1d || 0)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(riskMetrics?.var_metrics?.historical_var_95_10d || 0)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(riskMetrics?.var_metrics?.historical_var_99_10d || 0)}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Parametric</TableCell>
                        <TableCell align="right">
                          {formatCurrency(riskMetrics?.var_metrics?.parametric_var_95_1d || 0)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(riskMetrics?.var_metrics?.parametric_var_99_1d || 0)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(riskMetrics?.var_metrics?.parametric_var_95_10d || 0)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(riskMetrics?.var_metrics?.parametric_var_99_10d || 0)}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Monte Carlo</TableCell>
                        <TableCell align="right">
                          {formatCurrency(riskMetrics?.var_metrics?.monte_carlo_var_95_1d || 0)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(riskMetrics?.var_metrics?.monte_carlo_var_99_1d || 0)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(riskMetrics?.var_metrics?.monte_carlo_var_95_10d || 0)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(riskMetrics?.var_metrics?.monte_carlo_var_99_10d || 0)}
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        {loadingStress ? (
          <LinearProgress />
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Stress Test Results
                  </Typography>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={stressTests?.results || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="scenario_name" />
                      <YAxis />
                      <Tooltip formatter={(value) => `${value}%`} />
                      <Bar dataKey="portfolio_impact_pct" fill="#f44336" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        {loadingLimits ? (
          <LinearProgress />
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Risk Limits Status
                  </Typography>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Limit Type</TableCell>
                          <TableCell align="right">Current</TableCell>
                          <TableCell align="right">Limit</TableCell>
                          <TableCell align="right">Utilization</TableCell>
                          <TableCell align="center">Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {riskLimits?.limits?.map((limit: RiskLimit) => (
                          <TableRow key={limit.limit_id}>
                            <TableCell>{limit.limit_type.replace('_', ' ').toUpperCase()}</TableCell>
                            <TableCell align="right">
                              {formatCurrency(limit.current_value)}
                            </TableCell>
                            <TableCell align="right">
                              {formatCurrency(limit.limit_value)}
                            </TableCell>
                            <TableCell align="right">
                              <Box display="flex" alignItems="center">
                                <LinearProgress
                                  variant="determinate"
                                  value={limit.utilization_pct}
                                  color={getRiskColor(limit.status) as any}
                                  sx={{ width: 100, mr: 1 }}
                                />
                                {limit.utilization_pct.toFixed(1)}%
                              </Box>
                            </TableCell>
                            <TableCell align="center">
                              <Chip
                                icon={getRiskIcon(limit.status)}
                                label={limit.status.toUpperCase()}
                                color={getRiskColor(limit.status) as any}
                                size="small"
                              />
                            </TableCell>
                          </TableRow>
                        )) || (
                          <TableRow>
                            <TableCell colSpan={5} align="center">
                              No risk limit data available
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </TabPanel>

      {/* Stress Test Dialog */}
      <Dialog open={stressTestDialogOpen} onClose={() => setStressTestDialogOpen(false)}>
        <DialogTitle>Run Stress Test</DialogTitle>
        <DialogContent>
          <Typography>
            This will run comprehensive stress tests on the selected portfolio including:
          </Typography>
          <ul>
            <li>Interest Rate Shock (+/-200 bps)</li>
            <li>Credit Spread Widening (2x current spreads)</li>
            <li>Liquidity Crisis (20% haircut)</li>
          </ul>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStressTestDialogOpen(false)}>Cancel</Button>
          <Button onClick={runStressTest} variant="contained">
            Run Tests
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RiskMonitoring;
