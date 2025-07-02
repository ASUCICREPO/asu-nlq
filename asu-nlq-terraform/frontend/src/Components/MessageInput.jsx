import React, { useState } from 'react';
import { Box, TextField, IconButton, InputAdornment } from '@mui/material';
import { Send, Refresh } from '@mui/icons-material';

const MessageInput = ({ onSendMessage, disabled = false }) => {
  const [inputText, setInputText] = useState('');
  const [isDisabled, setIsDisabled] = useState(false);

  const handleSend = async () => {
    const message = inputText.trim();
    if (!message || disabled) return;

    setIsDisabled(true);
    setInputText('');

    try {
      await onSendMessage(message);
    } catch (error) {
      console.error('Error sending message:', error);
      // TODO: Add user-facing error feedback
    } finally {
      setIsDisabled(false);
    }
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey && !disabled) {
      event.preventDefault();
      handleSend();
    }
  };

  const handleInputChange = (event) => {
    setInputText(event.target.value);
  };

  const isInputDisabled = isDisabled || disabled;

  return (
    <Box
      sx={{
        position: 'fixed',
        bottom: 100, // Significantly increased from 60 to 120px for much larger gap
        left: '9%',
        right: '9%',
        width: 'auto',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        gap: 1
      }}
    >
      <IconButton
        onClick={handleRefresh}
        sx={{
          backgroundColor: 'transparent',
          color: 'grey.700',
          '&:hover': {
            backgroundColor: 'grey.200',
            color: 'grey.800'
          }
        }}
        aria-label="Refresh page"
      >
        <Refresh />
      </IconButton>
      
      <TextField
        fullWidth
        multiline
        maxRows={4}
        variant="outlined"
        placeholder={disabled ? "Waiting for response..." : "Type your question here..."}
        value={inputText}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        disabled={isInputDisabled}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                onClick={handleSend}
                disabled={isInputDisabled || !inputText.trim()}
                sx={{
                  backgroundColor: 'transparent',
                  color: 'grey.700', // Changed to dark grey for rest state
                  '&:hover': {
                    backgroundColor: 'grey.200',
                    color: 'grey.800' // Slightly darker on hover
                  },
                  '&.Mui-disabled': {
                    backgroundColor: 'transparent',
                    color: 'grey.700'
                  }
                }}
                aria-label="Send message"
              >
                <Send />
              </IconButton>
            </InputAdornment>
          )
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: '50px', // Changed from 6 to 50px for practically circular ends
            backgroundColor: 'background.paper',
            color: 'black', // Set text color to black
            '& fieldset': {
              borderColor: '#d0d0d0',
              borderWidth: '2px',
              borderRadius: '50px' // Ensure the fieldset also has circular ends
            },
            '&:hover fieldset': {
              borderColor: '#b0b0b0'
            },
            '&.Mui-focused fieldset': {
              borderColor: '#a0a0a0'
            }
          },
          '& .MuiOutlinedInput-input': {
            paddingLeft: '24px' // Add left padding for cursor offset
          },
          '& .MuiOutlinedInput-input::placeholder': {
            color: '#333333',
            opacity: 1
          }
        }}
      />
    </Box>
  );
};

export default MessageInput;