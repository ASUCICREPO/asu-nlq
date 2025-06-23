import React from 'react';
import {
  Typography,
  Card,
  CardContent,
  Box
} from '@mui/material';

const SuggestionBox = ({ presetNumber }) => {
  const presets = {
    1: {
      boldText: '📚 Built on official ASU datasets',
      lowerText: 'Get reliable answers sourced from university-maintained data.'
    },
    2: {
      boldText: '🧠 Fast, natural responses',
      lowerText: 'Ask in plain English — no technical skills needed'
    },
    3: {
      boldText: '📈 Visual insights when it helps',
      lowerText: 'See trends, comparisons, and summaries as charts when relevant'
    }
  };

  const currentPreset = presets[presetNumber] || presets[1];

  return (
    <Card
      elevation={0}
      sx={{
        flex: 1,
        border: 1,
        borderColor: 'grey.400',
        borderRadius: 4,
        backgroundColor: 'grey.50',
        width: '100%',
        minWidth: 450,
        maxHeight: 180,
        transition: 'all 0.3s ease-in-out',
        '&:hover': {
          borderColor: 'grey.700',
          transform: 'translateY(-2px)',
          boxShadow: 2
        }
      }}
    >
      <CardContent sx={{ px: 5, py: 1.5 }}>
        {/* Upper Section - Bold Text */}
        <Typography
          variant="h6"
          sx={{
            fontWeight: 700,
            color: 'text.primary',
            mb: 2,
            textAlign: 'left'
          }}
        >
          {currentPreset.boldText}
        </Typography>
        {/* Lower Section - Unbolded Text */}
        <Typography
          variant="body1"
          sx={{
            color: 'text.primary',
            fontWeight: 400,
            textAlign: 'left'
          }}
        >
          {currentPreset.lowerText}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default SuggestionBox;