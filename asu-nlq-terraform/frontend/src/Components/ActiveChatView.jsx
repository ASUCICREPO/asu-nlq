import React, { useEffect, useRef } from 'react';
import { Box, Typography } from '@mui/material';
import MessageBubble from './MessageBubble';

const MessageList = ({ messages, currentInfoMessage, isStreaming }) => {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive OR when info message changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentInfoMessage]);

  return (
    <Box
      sx={{
        flex: 1,
        overflow: 'auto',
        padding: 2,
        margin: '20px 0', // Increased margin top and bottom
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}
    >
      {messages.map((message, index) => {
        // Extract the text content from the message structure
        const messageText = message.content?.[0]?.text || '';
        const sender = message.role; // 'user' or 'assistant'
        
        // Check if this is the last assistant message and we have an info message to show
        const isLastAssistantMessage = sender === 'assistant' && index === messages.length - 1;
        const shouldShowInfoInThisMessage = isLastAssistantMessage && currentInfoMessage && isStreaming;
        
        // If this is the last assistant message and we have an info message, show the info instead of the empty content
        const displayText = shouldShowInfoInThisMessage && !messageText.trim() 
          ? currentInfoMessage 
          : messageText;
        
        // Determine if this message should have info message animation
        const isInfoMessage = shouldShowInfoInThisMessage && !messageText.trim();
        
        return (
          <MessageBubble
            key={index}
            message={displayText}
            sender={sender}
            isInfoMessage={isInfoMessage}
          />
        );
      })}
      
      <div ref={messagesEndRef} />
    </Box>
  );
};

export default MessageList;