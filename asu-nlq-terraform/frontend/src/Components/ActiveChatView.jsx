import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import MessageBubble from './MessageBubble';

const MessageList = ({ messages }) => {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <Box
      sx={{
        flex: 1,
        overflow: 'auto',
        padding: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 1
      }}
    >
      {messages.map((message, index) => {
        // Extract the text content from the message structure
        const messageText = message.content?.[0]?.text || '';
        const sender = message.role; // 'user' or 'assistant'
        
        return (
          <MessageBubble
            key={index}
            message={messageText}
            sender={sender}
          />
        );
      })}
      <div ref={messagesEndRef} />
    </Box>
  );
};

export default MessageList;