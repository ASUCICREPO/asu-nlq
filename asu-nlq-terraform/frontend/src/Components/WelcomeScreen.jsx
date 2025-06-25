import React from 'react';
import {
  Box,
  Typography,
  Container,
  useTheme,
  useMediaQuery,
  Fade
} from '@mui/material';
import SuggestionBox from './SuggestionBox';

const WelcomeScreen = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  return (
    <Fade in timeout={800}>
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'flex-start',
          padding: { xs: 2, sm: 3, md: 4 },
          backgroundColor: 'background.default',
          overflow: 'auto'
        }}
      >
        <Container maxWidth="lg">
          {/* Text Section */}
          <Box
            sx={{
              textAlign: 'center',
              mb: { xs: 4, md: 6 },
              mt: { xs: 8, md: 10 },
              maxWidth: { xs: '100%', sm: '900px', md: '1000px', lg: '1100px' }, // Expanded from 600px
              mx: 'auto'
            }}
          >
            <Typography
              variant={isMobile ? "h4" : "h3"}
              component="h1"
              sx={{
                fontWeight: 700,
                color: 'text.primary',
                mb: 2,
                fontSize: { xs: '1.75rem', md: '2.25rem' }
              }}
            >
              Hello Mike!
            </Typography>
            <Typography
              variant="h4"
              sx={{
                color: 'text.secondary',
                fontWeight: 400,
                textAlign: 'center',
                fontSize: { xs: '0.7rem', sm: '1.0rem', md: '1.25rem', lg: '1.5rem' },
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                width: '100%'
              }}
            >
              Ask questions about ASU enrollment, demographics, academic programs — all in plain English.
            </Typography>
          </Box>
          {/* Boxes Section */}
          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', md: 'row' },
              gap: 3,
              justifyContent: 'center',
              alignItems: 'stretch'
            }}
          >
            <SuggestionBox presetNumber={1} />
            <SuggestionBox presetNumber={2} />
            <SuggestionBox presetNumber={3} />
          </Box>
        </Container>
      </Box>
    </Fade>
  );
};

export default WelcomeScreen;