import { WEBSOCKET_API } from './constants.jsx';

class WebSocketManager {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.isConnecting = false;
    this.messageCallback = null;
  }

  // Connect to WebSocket
  connect() {
    return new Promise((resolve, reject) => {
      if (this.isConnected || this.isConnecting) {
        resolve();
        return;
      }

      this.isConnecting = true;
      
      try {
        this.ws = new WebSocket(WEBSOCKET_API);

        this.ws.onopen = () => {
          this.isConnected = true;
          this.isConnecting = false;
          console.log('WebSocket connection established');
          resolve();
        };

        this.ws.onclose = (event) => {
          this.isConnected = false;
          this.isConnecting = false;
          console.log('WebSocket connection closed:', event.code, event.reason);
        };

        this.ws.onerror = (error) => {
          this.isConnected = false;
          this.isConnecting = false;
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onmessage = (event) => {
          console.log('WebSocket message received:', event.data);
          try {
            const data = JSON.parse(event.data);
            if (data.message && this.messageCallback) {
              this.messageCallback(data.message);
            }
            // Close connection after receiving one packet
            this.close();
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  // Send message with chat history
  sendMessage(message, chatHistory) {
    return new Promise((resolve, reject) => {
      if (!this.isConnected) {
        reject(new Error('WebSocket is not connected'));
        return;
      }

      const packet = {
        action: 'sendMessage', // Route name for API Gateway
        message: message,
        chatHistory: chatHistory
      };

      try {
        this.ws.send(JSON.stringify(packet));
        console.log('Message sent:', packet);
        resolve();
      } catch (error) {
        console.error('Error sending message:', error);
        reject(error);
      }
    });
  }

  // Close WebSocket connection
  close() {
    if (this.ws && this.isConnected) {
      this.ws.close();
      console.log('WebSocket connection closed manually');
    }
  }

  // Get connection status
  getConnectionStatus() {
    if (this.isConnecting) return 'connecting';
    if (this.isConnected) return 'connected';
    return 'disconnected';
  }

  // Complete send message workflow (connect -> send -> wait for response -> close)
  async sendMessageAndWaitForResponse(message, chatHistory, onMessageReceived) {
    try {
      this.messageCallback = onMessageReceived;
      await this.connect();
      await this.sendMessage(message, chatHistory);
      // Connection will be closed automatically when response is received
      return true;
    } catch (error) {
      console.error('Error in sendMessageAndWaitForResponse:', error);
      this.close(); // Ensure cleanup on error
      throw error;
    }
  }
}

// Create singleton instance
const webSocketManager = new WebSocketManager();

export default webSocketManager;