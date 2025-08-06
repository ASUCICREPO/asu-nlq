import React, { useState } from 'react';
import { Box, Paper } from '@mui/material';
import ChatHeader from './ChatHeader';
import WelcomeScreen from './WelcomeScreen';
import ActiveChatView from './ActiveChatView';
import MessageInput from './MessageInput';
import webSocketManager from '../Utilities/websocketManager';

const ChatContainer = () => {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isInputDisabled, setIsInputDisabled] = useState(false); // Separate state for input control
  const [currentInfoMessage, setCurrentInfoMessage] = useState(null);
  
  // Determine if we should show welcome screen or active chat
  const showWelcomeScreen = messages.length === 0;

  const handleSendMessage = async (message) => {
    // Add user message to messages array
    const userMessage = {
      role: "user",
      content: [
        {
          text: message
        }
      ]
    };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);

    try {
      setIsStreaming(true);
      setIsInputDisabled(true); // Disable input until response is complete
      setCurrentInfoMessage(null); // Clear any previous info message
      
      // Add placeholder for assistant message that will be updated as it streams
      const assistantMessage = {
        role: "assistant",
        content: [
          {
            text: ""
          }
        ]
      };
      const messagesWithPlaceholder = [...newMessages, assistantMessage];
      setMessages(messagesWithPlaceholder);

      // Define callback for when bot message chunks are received
      const onBotMessageReceived = (botMessage, isNewMessage = false) => {
        // Clear info message when actual response starts coming in (but don't re-enable input yet)
        if (botMessage && botMessage.trim().length > 0) {
          setCurrentInfoMessage(null);
          setIsStreaming(false);
        }
        
        // Update messages based on whether this is a new message or updating existing
        setMessages(prevMessages => {
          if (isNewMessage) {
            // Create a completely new assistant message
            const newAssistantMessage = {
              role: "assistant",
              content: [
                {
                  text: botMessage
                }
              ]
            };
            return [...prevMessages, newAssistantMessage];
          } else {
            // Update existing assistant message (original logic)
            // We should always have at least the user message + assistant placeholder by now
            if (prevMessages.length === 0) {
              console.warn('No messages found when trying to update assistant response');
              return prevMessages;
            }

            const lastMessage = prevMessages[prevMessages.length - 1];
            // If last message isn't from assistant, we might need to add one
            if (lastMessage?.role !== 'assistant') {
              console.log('Last message is not assistant, adding new assistant message');
              const newAssistantMessage = {
                role: "assistant",
                content: [
                  {
                    text: botMessage
                  }
                ]
              };
              return [...prevMessages, newAssistantMessage];
            }

            // Update existing assistant message
            const newMessages = prevMessages.slice(0, -1); // All messages except last
            const updatedLastMessage = {
              role: "assistant",
              content: [
                {
                  text: botMessage
                }
              ]
            };
            return [...newMessages, updatedLastMessage];
          }
        });
      };

      // Define callback for info messages
      const onInfoReceived = (infoMessage) => {
        setCurrentInfoMessage(infoMessage);
      };

      // Define callback for when message is complete
      const onMessageComplete = () => {
        console.log('Message fully received, re-enabling input');
        setIsInputDisabled(false); // Re-enable input only when message is complete
      };

      // WebSocket call with all callbacks
      await webSocketManager.sendMessageAndWaitForResponse(
        message,
        newMessages,
        onBotMessageReceived,
        onInfoReceived,
        onMessageComplete
      );
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove the placeholder message on error
      setMessages(prevMessages => {
        const filteredMessages = [...prevMessages];
        if (filteredMessages[filteredMessages.length - 1]?.role === 'assistant' &&
            filteredMessages[filteredMessages.length - 1]?.content[0]?.text === '') {
          filteredMessages.pop();
        }
        return filteredMessages;
      });
      // Re-enable input on error
      setIsStreaming(false);
      setIsInputDisabled(false); // Re-enable input on error
      setCurrentInfoMessage(null);
    }
  };

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column', // Changed to column for new layout
        width: '100vw'
      }}
    >
      {/* ChatHeader - 9% Padding */}
      <Box
        sx={{
          width: '100%',
          flexShrink: 0,
          paddingX: '7%' // Fixed 9% padding on both sides
        }}
      >
        <ChatHeader />
      </Box>
      
      {/* Main Content Area - Matches Header Padding */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          paddingX: '7%' // Same padding as header
        }}
      >
        <Paper
          elevation={0}
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            borderRadius: 0
          }}
        >
          {/* Middle Content Area - Conditional rendering */}
          <Box
            sx={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              paddingBottom: '180px' // Reserve space for the fixed MessageInput (100px bottom + 80px margin)
            }}
          >
            {showWelcomeScreen ? (
              <WelcomeScreen />
            ) : (
              <ActiveChatView 
                messages={messages} 
                currentInfoMessage={currentInfoMessage}
                isStreaming={isStreaming}
              />
            )}
          </Box>
          
          {/* Input Section - Always visible */}
          <MessageInput 
            onSendMessage={handleSendMessage} 
            disabled={isInputDisabled}
            isResponding={isStreaming}        
          />
        </Paper>
      </Box>
    </Box>
  );
};

export default ChatContainer;