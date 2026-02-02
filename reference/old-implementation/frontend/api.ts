import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// WebSocket 连接类
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private onMessageCallback: ((data: any) => void) | null = null;
  private onErrorCallback: ((error: Event) => void) | null = null;
  private onCloseCallback: (() => void) | null = null;
  private isManualClose = false;
  private isConnecting = false; // 添加连接状态标志

  constructor(researchId: string) {
    this.url = `ws://${API_BASE_URL.split('://')[1]}/api/v1/research/ws/${researchId}`;
  }

  connect(
    onMessage: (data: any) => void,
    onError?: (error: Event) => void,
    onClose?: () => void
  ) {
    // 保存回调
    this.onMessageCallback = onMessage;
    this.onErrorCallback = onError || null;
    this.onCloseCallback = onClose || null;
    this.isManualClose = false;

    // 如果正在连接，不要重复连接
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.createConnection();
  }

  private createConnection() {
    // 防止重复连接
    if (this.isConnecting) {
      return;
    }

    this.isConnecting = true;

    try {
      // 关闭旧连接
      if (this.ws) {
        this.ws.close();
        this.ws = null;
      }

      this.ws = new WebSocket(this.url);

      // 连接成功
      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.isConnecting = false;

        // 清除重连定时器
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
      };

      // 接收消息
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.onMessageCallback?.(data);
        } catch (error) {
          console.error('❌ Failed to parse WebSocket message:', error);
        }
      };

      // 连接错误
      this.ws.onerror = (error) => {
        console.warn('⚠️  WebSocket error:', error);
        this.isConnecting = false;
        this.onErrorCallback?.(error);
      };

      // 连接关闭
      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket closed');
        this.isConnecting = false;
        this.onCloseCallback?.();

        // 如果不是手动关闭且连接已建立过，尝试重连
        if (!this.isManualClose && event.code !== 1000) {
          // 只在之前成功连接过的情况下才重连
          this.reconnectTimer = setTimeout(() => {
            console.log('🔄 Attempting to reconnect...');
            this.createConnection();
          }, 3000);
        }
      };
    } catch (error) {
      console.error('❌ WebSocket connection error:', error);
      this.isConnecting = false;
    }
  }

  disconnect() {
    console.log('🛑 Disconnecting WebSocket...');
    this.isManualClose = true;
    this.isConnecting = false;

    // 清除重连定时器
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    // 关闭连接
    if (this.ws) {
      try {
        this.ws.close(1000, 'Component unmounted');
      } catch (error) {
        // 忽略关闭时的错误
      }
      this.ws = null;
    }

    // 清除回调
    this.onMessageCallback = null;
    this.onErrorCallback = null;
    this.onCloseCallback = null;
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('⚠️  WebSocket is not connected');
    }
  }

  // 获取连接状态
  getReadyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }
}
