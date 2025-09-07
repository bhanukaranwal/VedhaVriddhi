import { useState, useEffect, useCallback, useRef } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

interface WebSocketConfig {
  url?: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  topic?: string;
}

export const useWebSocket = (
  endpoint: string,
  config: WebSocketConfig = {}
) => {
  const { token } = useSelector((state: RootState) => state.auth);
  
  const {
    url = process.env.REACT_APP_WS_URL || 'ws://localhost:8002',
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    heartbeatInterval = 30000,
  } = config;

  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'Disconnected' | 'Connected' | 'Connecting'>('Disconnected');
  const [error, setError] = useState<string | null>(null);

  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const heartbeatIntervalRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);
  const shouldConnectRef = useRef(true);

  const connect = useCallback(() => {
    if (!token || !shouldConnectRef.current) return;

    setConnectionStatus('Connecting');
    setError(null);

    try {
      const wsUrl = `${url}${endpoint}${token ? `?token=${token}` : ''}`;
      const newSocket = new WebSocket(wsUrl);

      newSocket.onopen = () => {
        console.log(`WebSocket connected to ${endpoint}`);
        setConnectionStatus('Connected');
        setSocket(newSocket);
        reconnectAttemptsRef.current = 0;
        
        // Start heartbeat
        heartbeatIntervalRef.current = setInterval(() => {
          if (newSocket.readyState === WebSocket.OPEN) {
            newSocket.send(JSON.stringify({ type: 'ping' }));
          }
        }, heartbeatInterval);
      };

      newSocket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          // Handle pong responses
          if (message.type === 'pong') {
            return;
          }
          
          setLastMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      newSocket.onclose = (event) => {
        console.log(`WebSocket disconnected from ${endpoint}:`, event.code, event.reason);
        setConnectionStatus('Disconnected');
        setSocket(null);
        
        // Clear heartbeat
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
        }

        // Attempt to reconnect if not a manual disconnect
        if (shouldConnectRef.current && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`Attempting to reconnect... (${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      newSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
        setConnectionStatus('Disconnected');
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setError('Failed to create WebSocket connection');
      setConnectionStatus('Disconnected');
    }
  }, [endpoint, token, url, reconnectInterval, maxReconnectAttempts, heartbeatInterval]);

  const disconnect = useCallback(() => {
    shouldConnectRef.current = false;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }
    
    if (socket) {
      socket.close();
    }
  }, [socket]);

  const sendMessage = useCallback((message: any) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
      return true;
    } else {
      console.warn('WebSocket is not connected');
      return false;
    }
  }, [socket]);

  const subscribe = useCallback((topic: string) => {
    return sendMessage({
      type: 'subscribe',
      topic,
      timestamp: new Date().toISOString(),
    });
  }, [sendMessage]);

  const unsubscribe = useCallback((topic: string) => {
    return sendMessage({
      type: 'unsubscribe',
      topic,
      timestamp: new Date().toISOString(),
    });
  }, [sendMessage]);

  // Connect when token is available
  useEffect(() => {
    if (token) {
      shouldConnectRef.current = true;
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [token, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      shouldConnectRef.current = false;
      disconnect();
    };
  }, [disconnect]);

  return {
    socket,
    lastMessage,
    connectionStatus,
    error,
    sendMessage,
    subscribe,
    unsubscribe,
    connect,
    disconnect,
  };
};
