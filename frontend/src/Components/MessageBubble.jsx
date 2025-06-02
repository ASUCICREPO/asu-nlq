import React from 'react';
import { Box, Paper, Typography, Avatar } from '@mui/material';
import { Person, SmartToy } from '@mui/icons-material';

const MessageBubble = ({ message, sender }) => {
  const isUser = sender === 'user';
  const isAssistant = sender === 'assistant';

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        alignItems: 'flex-start',
        gap: 1,
        mb: 1
      }}
    >
      {!isUser && (
        <Avatar
          sx={{
            width: 32,
            height: 32,
            bgcolor: 'primary.main'
          }}
        >
          <SmartToy fontSize="small" />
        </Avatar>
      )}
      <Paper
        elevation={1}
        sx={{
          maxWidth: '70%',
          padding: 1.5,
          backgroundColor: isUser ? 'primary.main' : 'grey.100',
          color: isUser ? 'primary.contrastText' : 'text.primary',
          borderRadius: 2,
          borderTopRightRadius: isUser ? 0.5 : 2,
          borderTopLeftRadius: isUser ? 2 : 0.5,
          minHeight: isAssistant && !message ? '24px' : 'auto' // Show placeholder for empty streaming messages
        }}
      >
        <Typography 
          variant="body1" 
          sx={{ 
            wordWrap: 'break-word',
            whiteSpace: 'pre-wrap' // Preserve line breaks and whitespace
          }}
        >
          {message || (isAssistant ? '...' : '')}
        </Typography>
      </Paper>
      {isUser && (
        <Avatar
          sx={{
            width: 32,
            height: 32,
            bgcolor: 'secondary.main'
          }}
        >
          <Person fontSize="small" />
        </Avatar>
      )}
    </Box>
  );
};

export default MessageBubble;