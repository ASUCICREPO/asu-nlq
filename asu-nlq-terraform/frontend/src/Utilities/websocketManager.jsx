import { WEBSOCKET_API } from './constants.jsx';

class WebSocketManager {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.isConnecting = false;
    this.messageCallback = null;
    this.currentMessage = ''; // Track the current streaming message
    this.hasContent = false; // Track if current message has content for break token validation
    this.shouldCreateNewMessage = false; // Track if next delta should create new message
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
          try {
            const data = JSON.parse(event.data);
            this.handleStreamingMessage(data);
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

  // Handle different types of streaming messages
  handleStreamingMessage(data) {
    if (data.type === 'messageStart') {
      // Reset current message for new message
      this.currentMessage = '';
      this.hasContent = false;
      this.shouldCreateNewMessage = false;
      console.log('Message start received');
    } 
    else if (data.type === 'contentBlockDelta') {
      // Simple delta processing - just accumulate text
      const deltaText = data.data.delta.text;
      
      // Only process if deltaText has actual content
      if (deltaText && deltaText.length > 0) {
        this.currentMessage += deltaText;
        this.hasContent = true;
        
        // Check if this should create a new message (after break token)
        const isNewMessage = this.shouldCreateNewMessage;
        
        // Reset the flag after using it
        if (this.shouldCreateNewMessage) {
          this.shouldCreateNewMessage = false;
        }
        
        // Update the UI with the current accumulated message
        if (this.messageCallback) {
          this.messageCallback(this.currentMessage, isNewMessage);
        }
      } else {
        console.log('Empty delta text received, skipping update');
      }
    }
    else if (data.type === 'breakTokenType') {
      // Only process if we have content from previous contentBlockDelta
      if (this.hasContent && this.currentMessage.length > 0) {
        console.log('Break token received - finalizing current message and preparing for new one');
        
        // Finalize current message
        if (this.messageCallback) {
          this.messageCallback(this.currentMessage, false);
        }
        
        // Reset for next message and flag that next delta should create new message
        this.currentMessage = '';
        this.hasContent = false;
        this.shouldCreateNewMessage = true;
        
        // Next contentBlockDelta will create a new message
      } else {
        console.log('Break token ignored - no preceding content');
      }
    }
    else if (data.type === 'messageStop') {
      // Message is complete, close connection
      console.log('Message stop received, final message:', this.currentMessage);
      this.close();
    }
    else {
      // Handle legacy format or other message types
      if (data.message && this.messageCallback) {
        this.messageCallback(data.message, false);
        this.close(); // Close for non-streaming messages
      }
    }
  }

  // Send message with chat history
  sendMessage(message, messages) {
    return new Promise((resolve, reject) => {
      if (!this.isConnected) {
        reject(new Error('WebSocket is not connected'));
        return;
      }

      const packet = {
        action: 'sendMessage', // Route name for API Gateway
        message: message,
        messages: messages
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
    // Reset current message state
    this.currentMessage = '';
    this.hasContent = false;
    this.shouldCreateNewMessage = false;
  }

  // Get connection status
  getConnectionStatus() {
    if (this.isConnecting) return 'connecting';
    if (this.isConnected) return 'connected';
    return 'disconnected';
  }

  // Complete send message workflow (connect -> send -> wait for response -> close on messageStop)
  async sendMessageAndWaitForResponse(message, messages, onMessageReceived) {
    try {
      this.messageCallback = onMessageReceived;
      await this.connect();
      await this.sendMessage(message, messages);
      // Connection will be closed automatically when messageStop is received
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