import React, { useEffect, useRef } from 'react';
import { Box, Typography } from '@mui/material';
import MessageBubble from './MessageBubble';

const MessageList = ({ chatHistory }) => {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  // Combine and sort messages chronologically
  const getAllMessages = () => {
    const messages = [];
    
    // Get the maximum length to iterate through all messages
    const maxLength = Math.max(chatHistory.User.length, chatHistory.Assistant.length);
    
    for (let i = 0; i < maxLength; i++) {
      // Add user message if it exists at this index
      if (i < chatHistory.User.length) {
        messages.push({
          text: chatHistory.User[i],
          sender: 'user',
          id: `user-${i}`
        });
      }
      
      // Add assistant message if it exists at this index
      if (i < chatHistory.Assistant.length) {
        messages.push({
          text: chatHistory.Assistant[i],
          sender: 'assistant',
          id: `assistant-${i}`
        });
      }
    }
    
    return messages;
  };

  const messages = getAllMessages();

  return (
    <Box
      sx={{
        flex: 1,
        overflowY: 'auto',
        padding: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 1
      }}
    >
      {messages.length === 0 ? (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100%',
            color: 'text.secondary'
          }}
        >
          <Typography variant="body1">
            Start a conversation by typing a message below
          </Typography>
        </Box>
      ) : (
        messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message.text}
            sender={message.sender}
          />
        ))
      )}
      <div ref={messagesEndRef} />
    </Box>
  );
};

export default MessageList;