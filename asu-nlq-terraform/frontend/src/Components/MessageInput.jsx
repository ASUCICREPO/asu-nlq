import React, { useState } from 'react';
import { Box, TextField, IconButton, Paper } from '@mui/material';
import { Send } from '@mui/icons-material';

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

  const handleKeyPress = (event) => {
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
    <Paper
      elevation={0}
      sx={{
        borderTop: 1,
        borderColor: 'divider',
        padding: 2
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: 1
        }}
      >
        <TextField
          fullWidth
          multiline
          maxRows={4}
          variant="outlined"
          placeholder={disabled ? "Waiting for response..." : "Type your message..."}
          value={inputText}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          disabled={isInputDisabled}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 3
            }
          }}
        />
        <IconButton
          color="primary"
          onClick={handleSend}
          disabled={isInputDisabled || !inputText.trim()}
          sx={{
            bgcolor: 'primary.main',
            color: 'white',
            '&:hover': {
              bgcolor: 'primary.dark'
            },
            '&.Mui-disabled': {
              bgcolor: 'grey.300',
              color: 'grey.500'
            }
          }}
        >
          <Send />
        </IconButton>
      </Box>
    </Paper>
  );
};

export default MessageInput;