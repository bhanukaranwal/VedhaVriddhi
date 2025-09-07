import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import { combineReducers } from '@reduxjs/toolkit';

// Import all slices
import authSlice from './slices/authSlice';
import orderSlice from './slices/orderSlice';
import tradeSlice from './slices/tradeSlice';
import positionSlice from './slices/positionSlice';
import portfolioSlice from './slices/portfolioSlice';
import marketDataSlice from './slices/marketDataSlice';
import analyticsSlice from './slices/analyticsSlice';
import riskSlice from './slices/riskSlice';
import complianceSlice from './slices/complianceSlice';
import notificationSlice from './slices/notificationSlice';
import uiSlice from './slices/uiSlice';
import workspaceSlice from './slices/workspaceSlice';
import settingsSlice from './slices/settingsSlice';

const rootReducer = combineReducers({
  auth: authSlice,
  orders: orderSlice,
  trades: tradeSlice,
  positions: positionSlice,
  portfolio: portfolioSlice,
  marketData: marketDataSlice,
  analytics: analyticsSlice,
  risk: riskSlice,
  compliance: complianceSlice,
  notifications: notificationSlice,
  ui: uiSlice,
  workspace: workspaceSlice,
  settings: settingsSlice,
});

// Persist configuration
const persistConfig = {
  key: 'vedhavriddhi',
  storage,
  whitelist: ['auth', 'settings', 'workspace'], // Only persist certain slices
  blacklist: ['marketData', 'notifications'], // Don't persist real-time data
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
        ignoredActionsPaths: ['meta.arg', 'payload.timestamp'],
        ignoredPaths: ['items.dates'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
