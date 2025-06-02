import React from 'react';
import { Box, Chip, Typography } from '@mui/material';
import { Circle } from '@mui/icons-material';

const ConnectionStatus = ({ status }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'connected':
        return {
          color: 'success',
          label: 'Connected',
          dotColor: '#4caf50'
        };
      case 'connecting':
        return {
          color: 'warning',
          label: 'Connecting...',
          dotColor: '#ff9800'
        };
      case 'disconnected':
      default:
        return {
          color: 'default',
          label: 'Disconnected',
          dotColor: '#757575'
        };
    }
  };

  const statusConfig = getStatusConfig();

  return (
    <Box
      sx={{
        padding: 1,
        borderBottom: 1,
        borderColor: 'divider',
        backgroundColor: 'grey.50',
        display: 'flex',
        alignItems: 'center',
        gap: 1
      }}
    >
      <Typography variant="caption" color="text.secondary">
        DEBUG:
      </Typography>
      <Chip
        icon={
          <Circle
            sx={{
              fontSize: '12px !important',
              color: statusConfig.dotColor
            }}
          />
        }
        label={statusConfig.label}
        size="small"
        color={statusConfig.color}
        variant="outlined"
      />
    </Box>
  );
};

export default ConnectionStatus;