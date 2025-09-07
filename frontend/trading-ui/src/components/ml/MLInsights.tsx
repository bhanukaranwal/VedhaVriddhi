import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  Alert,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Psychology,
  Analytics,
  Refresh,
  Info,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
} from 'recharts';
import { useQuery } from 'react-query';
import { formatPercentage, formatNumber } from '../../utils/formatting';

interface MLPrediction {
  model_type: string;
  prediction: number;
  confidence: number;
  horizon_days: number;
  features_used: number;
  timestamp: string;
  model_version: string;
}

interface ModelPerformance {
  model_type: string;
  accuracy: number;
  mse: number;
  mae: number;
  r2_score: number;
  last_trained: string;
  training_samples: number;
}

const MLInsights: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<string>('yield_forecast');
  const [predictionHorizon, setPredictionHorizon] = useState<number>(1);

  // Available models
  const modelTypes = [
    { value: 'yield_forecast', label: 'Yield Forecasting' },
    { value: 'credit_spread_prediction', label: 'Credit Spread Prediction' },
    { value: 'default_probability', label: 'Default Probability' },
    { value: 'price_movement', label: 'Price Movement' },
    { value: 'volatility_forecast', label: 'Volatility Forecasting' },
  ];

  // Fetch ML predictions
  const { data: predictions, isLoading: predictionsLoading, refetch: refetchPredictions } = useQuery(
    ['mlPredictions', selectedModel, predictionHorizon],
    async () => {
      const response = await fetch(`/api/ml/predictions?model=${selectedModel}&horizon=${predictionHorizon}`);
      return response.json();
    },
    { refetchInterval: 300000 } // 5 minutes
  );

  // Fetch model performance metrics
  const { data: performance, isLoading: performanceLoading } = useQuery(
    ['mlPerformance'],
    async () => {
      const response = await fetch('/api/ml/performance');
      return response.json();
    },
    { refetchInterval: 600000 } // 10 minutes
  );

  // Fetch feature importance
  const { data: featureImportance, isLoading: featuresLoading } = useQuery(
    ['mlFeatures', selectedModel],
    async () => {
      const response = await fetch(`/api/ml/features?model=${selectedModel}`);
      return response.json();
    },
    { refetchInterval: 600000 }
  );

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  const getTrendIcon = (prediction: number) => {
    return prediction > 0 ? (
      <TrendingUp color="success" />
    ) : (
      <TrendingDown color="error" />
    );
  };

  const handleRefresh = () => {
    refetchPredictions();
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box display="flex" alignItems="center" gap={1}>
          <Psychology color="primary" />
          <Typography variant="h5" fontWeight="bold">
            ML Insights & Predictions
          </Typography>
        </Box>
        
        <Box display="flex" gap={2}>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Model Type</InputLabel>
            <Select
              value={selectedModel}
              label="Model Type"
              onChange={(e) => setSelectedModel(e.target.value)}
            >
              {modelTypes.map((model) => (
                <MenuItem key={model.value} value={model.value}>
                  {model.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Horizon</InputLabel>
            <Select
              value={predictionHorizon}
              label="Horizon"
              onChange={(e) => setPredictionHorizon(Number(e.target.value))}
            >
              <MenuItem value={1}>1 Day</MenuItem>
              <MenuItem value={7}>1 Week</MenuItem>
              <MenuItem value={30}>1 Month</MenuItem>
              <MenuItem value={90}>3 Months</MenuItem>
            </Select>
          </FormControl>
          
          <IconButton onClick={handleRefresh} disabled={predictionsLoading}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* Predictions Grid */}
      <Grid container spacing={3}>
        {/* Main Prediction Card */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: 300 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <Analytics color="primary" />
                Current Prediction
              </Typography>
              
              {predictionsLoading ? (
                <LinearProgress />
              ) : predictions ? (
                <Box>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    {getTrendIcon(predictions.prediction)}
                    <Typography variant="h3" color="primary">
                      {predictions.prediction > 0 ? '+' : ''}{formatNumber(predictions.prediction, '0.0000')}
                    </Typography>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {selectedModel.replace('_', ' ').toUpperCase()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {predictionHorizon} day horizon
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Confidence Level
                    </Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <LinearProgress
                        variant="determinate"
                        value={predictions.confidence * 100}
                        color={getConfidenceColor(predictions.confidence)}
                        sx={{ width: 100, height: 8, borderRadius: 4 }}
                      />
                      <Chip
                        label={getConfidenceLabel(predictions.confidence)}
                        size="small"
                        color={getConfidenceColor(predictions.confidence) as any}
                        variant="outlined"
                      />
                      <Typography variant="body2">
                        {formatPercentage(predictions.confidence)}
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Model: {predictions.model_version} • Features: {predictions.features_used}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Generated: {new Date(predictions.timestamp).toLocaleString()}
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Alert severity="info">No predictions available</Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Prediction Trend Chart */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: 300 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Prediction Trend
              </Typography>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={predictions?.historical_predictions || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <RechartsTooltip />
                  <Line 
                    type="monotone" 
                    dataKey="prediction" 
                    stroke="#1976d2" 
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="actual" 
                    stroke="#4caf50" 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Model Performance */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: 400 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Model Performance
              </Typography>
              
              {performanceLoading ? (
                <LinearProgress />
              ) : performance ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Model</TableCell>
                        <TableCell align="right">Accuracy</TableCell>
                        <TableCell align="right">R² Score</TableCell>
                        <TableCell align="right">Last Trained</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {performance.map((model: ModelPerformance) => (
                        <TableRow key={model.model_type}>
                          <TableCell>
                            <Typography variant="body2">
                              {model.model_type.replace('_', ' ')}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Box display="flex" alignItems="center" justifyContent="flex-end">
                              <LinearProgress
                                variant="determinate"
                                value={model.accuracy * 100}
                                color={model.accuracy > 0.8 ? 'success' : 'warning'}
                                sx={{ width: 40, height: 4, mr: 1 }}
                              />
                              <Typography variant="body2">
                                {formatPercentage(model.accuracy)}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2">
                              {formatNumber(model.r2_score, '0.000')}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" color="text.secondary">
                              {new Date(model.last_trained).toLocaleDateString()}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Alert severity="info">No performance data available</Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Feature Importance */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: 400 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                Feature Importance
                <Tooltip title="Features ranked by their impact on model predictions">
                  <Info fontSize="small" color="disabled" />
                </Tooltip>
              </Typography>
              
              {featuresLoading ? (
                <LinearProgress />
              ) : featureImportance ? (
                <Box>
                  {featureImportance.slice(0, 8).map((feature: any, index: number) => (
                    <Box key={feature.name} mb={1}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                        <Typography variant="body2">
                          {feature.name.replace('_', ' ')}
                        </Typography>
                        <Typography variant="body2" color="primary">
                          {formatPercentage(feature.importance)}
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={feature.importance * 100}
                        color="primary"
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                    </Box>
                  ))}
                </Box>
              ) : (
                <Alert severity="info">No feature importance data available</Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Prediction Confidence Distribution */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Model Insights & Recommendations
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Alert severity="info" sx={{ height: '100%' }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Market Outlook
                    </Typography>
                    <Typography variant="body2">
                      Based on current yield forecasting models, expect moderate volatility in the bond market over the next week.
                    </Typography>
                  </Alert>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Alert severity="warning" sx={{ height: '100%' }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Risk Alert
                    </Typography>
                    <Typography variant="body2">
                      Credit spread prediction model shows increasing spreads for BBB-rated securities. Consider position adjustments.
                    </Typography>
                  </Alert>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Alert severity="success" sx={{ height: '100%' }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Opportunity
                    </Typography>
                    <Typography variant="body2">
                      ML models indicate attractive entry points for 5-7 year government securities with high confidence.
                    </Typography>
                  </Alert>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default MLInsights;
