import React from 'react';
import { Box, Paper, Typography, Avatar } from '@mui/material';
import { Person } from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import Logo from '../Assets/logo.svg';

const MessageBubble = ({ message, sender }) => {
  const isUser = sender === 'user';
  const isAssistant = sender === 'assistant';

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        alignItems: 'center',
        gap: isUser ? 1.5 : 2.5,
        mb: 1
      }}
    >
      {!isUser && (
        <Box
          sx={{
            width: 48,
            height: 48,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <img
            src={Logo}
            alt="Assistant Logo"
            style={{
              width: '56px',
              height: '56px'
            }}
          />
        </Box>
      )}
      <Paper
        elevation={0}
        sx={{
          maxWidth: '70%',
          padding: 2,
          backgroundColor: isUser ? '#8c1d40' : '#ffc627',
          color: isUser ? 'white' : 'black',
          borderRadius: '25px',
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
              <Box component="ul" sx={{ margin: '8px 0', paddingLeft: 2, textAlign: 'left' }} {...props} />
            ),
            ol: ({ node, ...props }) => (
              <Box component="ol" sx={{ margin: '8px 0', paddingLeft: 2, textAlign: 'left' }} {...props} />
            ),
            li: ({ node, ...props }) => (
              <Typography component="li" variant="body1" sx={{ marginBottom: 0.5, textAlign: 'left', display: 'list-item' }} {...props} />
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
        <Box
          sx={{
            width: 48,
            height: 48,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <Avatar
            sx={{
              width: 48,
              height: 48,
              bgcolor: '#8c1d40'
            }}
          >
            <Person fontSize="large" />
          </Avatar>
        </Box>
      )}
    </Box>
  );
};

export default MessageBubble;