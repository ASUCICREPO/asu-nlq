import React, { useState } from 'react';
import { Box, Paper } from '@mui/material';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import ConnectionStatus from './ConnectionStatus';
import webSocketManager from '../Utilities/websocketManager';
import { DEBUG } from '../Utilities/constants';

const ChatContainer = () => {
  const [messages, setMessages] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [isStreaming, setIsStreaming] = useState(false);

  const handleSendMessage = async (message) => {
    // Add user message to messages array
    const userMessage = {
      role: "user",
      content: [
        {
          text: message
        }
      ]
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);

    try {
      setConnectionStatus('connecting');
      setIsStreaming(true);

      // Add placeholder for assistant message that will be updated as it streams
      const assistantMessage = {
        role: "assistant",
        content: [
          {
            text: ""
          }
        ]
      };
      
      const messagesWithPlaceholder = [...newMessages, assistantMessage];
      setMessages(messagesWithPlaceholder);

      // Define callback for when bot message chunks are received
      const onBotMessageReceived = (botMessage) => {
        // Update the last message (assistant message) with the streaming content
        setMessages(prevMessages => {
          // We should always have at least the user message + assistant placeholder by now
          if (prevMessages.length === 0) {
            console.warn('No messages found when trying to update assistant response');
            return prevMessages;
          }
          
          const lastMessage = prevMessages[prevMessages.length - 1];
          
          // If last message isn't from assistant, we might need to add one
          if (lastMessage?.role !== 'assistant') {
            console.log('Last message is not assistant, adding new assistant message');
            const newAssistantMessage = {
              role: "assistant",
              content: [
                {
                  text: botMessage
                }
              ]
            };
            return [...prevMessages, newAssistantMessage];
          }
          
          // Update existing assistant message
          const newMessages = prevMessages.slice(0, -1); // All messages except last
          const updatedLastMessage = {
            role: "assistant",
            content: [
              {
                text: botMessage
              }
            ]
          };
          
          return [...newMessages, updatedLastMessage];
        });
      };

      await webSocketManager.sendMessageAndWaitForResponse(
        message,
        newMessages,
        onBotMessageReceived
      );

      setConnectionStatus('connected');
    } catch (error) {
      console.error('Failed to send message:', error);
      setConnectionStatus('disconnected');
      
      // Remove the placeholder message on error
      setMessages(prevMessages => {
        const filteredMessages = [...prevMessages];
        if (filteredMessages[filteredMessages.length - 1]?.role === 'assistant' && 
            filteredMessages[filteredMessages.length - 1]?.content[0]?.text === '') {
          filteredMessages.pop();
        }
        return filteredMessages;
      });
      
      // TODO: Add error handling UI feedback
    } finally {
      setIsStreaming(false);
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
        <MessageList messages={messages} />
        <MessageInput onSendMessage={handleSendMessage} disabled={isStreaming} />
      </Paper>
    </Box>
  );
};

export default ChatContainer;