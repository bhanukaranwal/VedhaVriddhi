import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Order {
  id: string;
  clientOrderId: string;
  symbol: string;
  side: 'buy' | 'sell';
  orderType: string;
  quantity: number;
  price?: number;
  filledQuantity: number;
  remainingQuantity: number;
  status: string;
  timestamp: string;
  userId: string;
  accountId: string;
  timeInForce: string;
  metadata: Record<string, any>;
}

interface OrderState {
  orders: Order[];
  activeOrders: Order[];
  orderHistory: Order[];
  selectedOrder: Order | null;
  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;
  lastUpdated: string | null;
}

const initialState: OrderState = {
  orders: [],
  activeOrders: [],
  orderHistory: [],
  selectedOrder: null,
  isLoading: false,
  isSubmitting: false,
  error: null,
  lastUpdated: null,
};

const orderSlice = createSlice({
  name: 'orders',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setSubmitting: (state, action: PayloadAction<boolean>) => {
      state.isSubmitting = action.payload;
    },
    setOrders: (state, action: PayloadAction<Order[]>) => {
      state.orders = action.payload;
      state.activeOrders = action.payload.filter(order => 
        ['pending', 'partially_filled'].includes(order.status)
      );
      state.orderHistory = action.payload.filter(order => 
        ['filled', 'cancelled', 'rejected', 'expired'].includes(order.status)
      );
      state.lastUpdated = new Date().toISOString();
      state.isLoading = false;
    },
    addOrder: (state, action: PayloadAction<Order>) => {
      const newOrder = action.payload;
      state.orders.unshift(newOrder);
      
      if (['pending', 'partially_filled'].includes(newOrder.status)) {
        state.activeOrders.unshift(newOrder);
      } else {
        state.orderHistory.unshift(newOrder);
      }
      
      state.lastUpdated = new Date().toISOString();
    },
    updateOrder: (state, action: PayloadAction<Order>) => {
      const updatedOrder = action.payload;
      const index = state.orders.findIndex(order => order.id === updatedOrder.id);
      
      if (index !== -1) {
        state.orders[index] = updatedOrder;
        
        // Update active orders
        const activeIndex = state.activeOrders.findIndex(order => order.id === updatedOrder.id);
        const historyIndex = state.orderHistory.findIndex(order => order.id === updatedOrder.id);
        
        if (['pending', 'partially_filled'].includes(updatedOrder.status)) {
          if (activeIndex === -1) {
            state.activeOrders.unshift(updatedOrder);
          } else {
            state.activeOrders[activeIndex] = updatedOrder;
          }
          // Remove from history if it was there
          if (historyIndex !== -1) {
            state.orderHistory.splice(historyIndex, 1);
          }
        } else {
          if (historyIndex === -1) {
            state.orderHistory.unshift(updatedOrder);
          } else {
            state.orderHistory[historyIndex] = updatedOrder;
          }
          // Remove from active if it was there
          if (activeIndex !== -1) {
            state.activeOrders.splice(activeIndex, 1);
          }
        }
        
        // Update selected order if it's the same
        if (state.selectedOrder?.id === updatedOrder.id) {
          state.selectedOrder = updatedOrder;
        }
      }
      
      state.lastUpdated = new Date().toISOString();
    },
    removeOrder: (state, action: PayloadAction<string>) => {
      const orderId = action.payload;
      state.orders = state.orders.filter(order => order.id !== orderId);
      state.activeOrders = state.activeOrders.filter(order => order.id !== orderId);
      state.orderHistory = state.orderHistory.filter(order => order.id !== orderId);
      
      if (state.selectedOrder?.id === orderId) {
        state.selectedOrder = null;
      }
      
      state.lastUpdated = new Date().toISOString();
    },
    setSelectedOrder: (state, action: PayloadAction<Order | null>) => {
      state.selectedOrder = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
      state.isSubmitting = false;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearOrders: (state) => {
      state.orders = [];
      state.activeOrders = [];
      state.orderHistory = [];
      state.selectedOrder = null;
      state.lastUpdated = null;
    },
  },
});

export const {
  setLoading,
  setSubmitting,
  setOrders,
  addOrder,
  updateOrder,
  removeOrder,
  setSelectedOrder,
  setError,
  clearError,
  clearOrders,
} = orderSlice.actions;

export default orderSlice.reducer;
