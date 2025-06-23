import React from 'react';
import {
  Box,
  Typography,
  IconButton,
  AppBar,
  Toolbar,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  AccountCircle
} from '@mui/icons-material';
import Logo from '../Assets/logo.svg';
import AsuLogo from '../Assets/asu_logo.png';

const ChatHeader = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleRightIconClick = () => {
    // TODO: Implement functionality for right icon
    console.log('Right icon clicked');
  };

  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        backgroundColor: 'background.paper',
        color: 'text.primary'
      }}
    >
      <Toolbar
        sx={{
          minHeight: '129.6px !important', // 144px * 0.9 = 129.6px
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        {/* Left section - Logo and SunQuery */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1.62, // 1.8 * 0.9 = 1.62
            flex: isMobile ? 1 : 0
          }}
        >
          <img
            src={Logo}
            alt="SunQuery Logo"
            style={{
              width: '54px', // 60px * 0.9 = 54px
              height: '54px' // 60px * 0.9 = 54px
            }}
          />
          <Typography
            variant="h4"
            component="div"
            sx={{
              fontWeight: 600,
              color: 'text.primary'
            }}
          >
            SunQuery
          </Typography>
        </Box>

        {/* Center section - ASU NLQ Assistant */}
        <Box
          sx={{
            position: 'absolute',
            left: '50%',
            transform: 'translateX(-50%)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center'
          }}
        >
          <Typography
            variant="h4"
            component="div"
            sx={{
              fontWeight: 600,
              color: 'text.primary',
              textAlign: 'center'
            }}
          >
            ASU NLQ Assistant
          </Typography>
        </Box>

        {/* Right section - ASU Logo */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            flex: isMobile ? 1 : 0
          }}
        >
          <img
            src={AsuLogo}
            alt="ASU Logo"
            style={{
              height: '100px'
            }}
          />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default ChatHeader;