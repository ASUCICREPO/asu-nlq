import React from 'react';
import { Box, Paper, Typography, Avatar } from '@mui/material';
import { Person, SmartToy } from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';

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
        <ReactMarkdown
          components={{
            p: ({ node, ...props }) => (
              <Typography
                variant="body1"
                component="p"
                sx={{
                  wordWrap: 'break-word',
                  textAlign: 'left',
                  margin: 0,
                  '&:not(:last-child)': { marginBottom: 1 }
                }}
                {...props}
              />
            ),
            code: ({ node, inline, ...props }) => (
              <Typography
                component={inline ? 'code' : 'pre'}
                sx={{
                  fontFamily: 'monospace',
                  backgroundColor: 'rgba(0, 0, 0, 0.04)',
                  padding: inline ? '2px 4px' : '8px',
                  borderRadius: 1,
                  fontSize: inline ? 'inherit' : '0.875rem',
                  display: inline ? 'inline' : 'block',
                  whiteSpace: inline ? 'nowrap' : 'pre-wrap',
                  overflowX: inline ? 'auto' : 'auto'
                }}
                {...props}
              />
            ),
            strong: ({ node, ...props }) => (
              <Typography component="strong" sx={{ fontWeight: 'bold' }} {...props} />
            ),
            em: ({ node, ...props }) => (
              <Typography component="em" sx={{ fontStyle: 'italic' }} {...props} />
            ),
            ul: ({ node, ...props }) => (
              <Box component="ul" sx={{ margin: '8px 0', paddingLeft: 2 }} {...props} />
            ),
            ol: ({ node, ...props }) => (
              <Box component="ol" sx={{ margin: '8px 0', paddingLeft: 2 }} {...props} />
            ),
            li: ({ node, ...props }) => (
              <Typography component="li" variant="body1" sx={{ marginBottom: 0.5 }} {...props} />
            ),
            h1: ({ node, ...props }) => (
              <Typography variant="h6" component="h1" sx={{ fontWeight: 'bold', margin: '8px 0 4px 0' }} {...props} />
            ),
            h2: ({ node, ...props }) => (
              <Typography variant="subtitle1" component="h2" sx={{ fontWeight: 'bold', margin: '8px 0 4px 0' }} {...props} />
            ),
            h3: ({ node, ...props }) => (
              <Typography variant="subtitle2" component="h3" sx={{ fontWeight: 'bold', margin: '6px 0 2px 0' }} {...props} />
            ),
            blockquote: ({ node, ...props }) => (
              <Box
                component="blockquote"
                sx={{
                  borderLeft: '4px solid #ccc',
                  paddingLeft: 2,
                  margin: '8px 0',
                  fontStyle: 'italic',
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }}
                {...props}
              />
            )
          }}
        >
          {message || (isAssistant ? '...' : '')}
        </ReactMarkdown>
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