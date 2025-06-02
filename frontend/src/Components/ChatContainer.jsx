import React, { useState } from 'react';
import { Box, Paper } from '@mui/material';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import ConnectionStatus from './ConnectionStatus';
import webSocketManager from '../Utilities/websocketManager';
import { DEBUG } from '../Utilities/constants';

const ChatContainer = () => {
  const [chatHistory, setChatHistory] = useState({
    User: [],
    Assistant: []
  });
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  const handleSendMessage = async (message) => {
    // Add user message to chat history
    const newChatHistory = {
      ...chatHistory,
      User: [...chatHistory.User, message]
    };
    setChatHistory(newChatHistory);

    try {
      setConnectionStatus('connecting');
      
      // Define callback for when bot message is received
      const onBotMessageReceived = (botMessage) => {
        setChatHistory(prevHistory => ({
          ...prevHistory,
          Assistant: [...prevHistory.Assistant, botMessage]
        }));
        setConnectionStatus('disconnected');
      };

      await webSocketManager.sendMessageAndWaitForResponse(
        message, 
        newChatHistory, 
        onBotMessageReceived
      );
      
      setConnectionStatus('connected');
      
    } catch (error) {
      console.error('Failed to send message:', error);
      setConnectionStatus('disconnected');
      // TODO: Add error handling UI feedback
    }
  };

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        width: '100vw'
      }}
    >
      <Paper
        elevation={0}
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          borderRadius: 0
        }}
      >
        {DEBUG && (
          <ConnectionStatus status={connectionStatus} />
        )}
        
        <MessageList chatHistory={chatHistory} />
        
        <MessageInput onSendMessage={handleSendMessage} />
      </Paper>
    </Box>
  );
};

export default ChatContainer;