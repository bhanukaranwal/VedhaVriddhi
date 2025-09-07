import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { ApolloProvider } from '@apollo/client';
import { QueryClient, QueryClientProvider } from 'react-query';

import { store } from './store';
import { apolloClient } from './services/graphql';
import { useAuth } from './hooks/useAuth';

// Layout Components
import MainLayout from './components/layout/MainLayout';
import LoginPage from './pages/auth/LoginPage';

// Trading Components
import TradingDashboard from './pages/trading/TradingDashboard';
import OrderEntry from './pages/trading/OrderEntry';
import OrderBook from './pages/trading/OrderBook';
import Positions from './pages/trading/Positions';
import Portfolio from './pages/trading/Portfolio';

// Analytics Components
import Analytics from './pages/analytics/Analytics';
import RiskDashboard from './pages/analytics/RiskDashboard';
import PerformanceReports from './pages/analytics/PerformanceReports';

// Market Data Components
import MarketData from './pages/market/MarketData';
import YieldCurves from './pages/market/YieldCurves';

// Admin Components
import Administration from './pages/admin/Administration';

// Error Components
import ErrorBoundary from './components/common/ErrorBoundary';
import NotFound from './pages/NotFound';

// Theme configuration
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
      light: '#ff5983',
      dark: '#9a0036',
    },
    background: {
      default: '#0a0e1a',
      paper: '#1a1d29',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0b3b8',
    },
    error: {
      main: '#f44336',
    },
    warning: {
      main: '#ff9800',
    },
    success: {
      main: '#4caf50',
    },
    info: {
      main: '#2196f3',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    fontSize: 14,
    h1: {
      fontSize: '2.5rem',
      fontWeight: 300,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 300,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 400,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 400,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
    },
    body1: {
      fontSize: '0.875rem',
    },
    body2: {
      fontSize: '0.75rem',
    },
    caption: {
      fontSize: '0.75rem',
      color: '#b0b3b8',
    },
    overline: {
      fontSize: '0.75rem',
      fontWeight: 400,
      letterSpacing: '0.5px',
      textTransform: 'uppercase',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1a1d29',
          borderBottom: '1px solid #2a2d3a',
        },
      },
    },
    MuiDataGrid: {
      styleOverrides: {
        root: {
          border: 'none',
          '& .MuiDataGrid-cell': {
            borderColor: '#2a2d3a',
          },
          '& .MuiDataGrid-columnHeaders': {
            backgroundColor: '#2a2d3a',
            borderColor: '#2a2d3a',
          },
          '& .MuiDataGrid-footerContainer': {
            borderColor: '#2a2d3a',
          },
        },
      },
    },
  },
  shape: {
    borderRadius: 8,
  },
  spacing: 8,
});

// React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        height="100vh"
        bgcolor="background.default"
      >
        <div>Loading...</div>
      </Box>
    );
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

// Main App Component
const AppContent: React.FC = () => {
  return (
    <Router>
      <Box sx={{ display: 'flex', height: '100vh' }}>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          
          {/* Protected Routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <MainLayout>
                <TradingDashboard />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/trading/*" element={
            <ProtectedRoute>
              <MainLayout>
                <Routes>
                  <Route index element={<TradingDashboard />} />
                  <Route path="order-entry" element={<OrderEntry />} />
                  <Route path="order-book" element={<OrderBook />} />
                  <Route path="positions" element={<Positions />} />
                  <Route path="portfolio" element={<Portfolio />} />
                </Routes>
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/analytics/*" element={
            <ProtectedRoute>
              <MainLayout>
                <Routes>
                  <Route index element={<Analytics />} />
                  <Route path="risk" element={<RiskDashboard />} />
                  <Route path="performance" element={<PerformanceReports />} />
                </Routes>
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/market
