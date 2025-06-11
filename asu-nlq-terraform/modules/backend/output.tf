output "websocket_api_endpoint" {
  description = "The endpoint URL of the WebSocket API for productionuction"
  value = aws_apigatewayv2_api.asu_nlq_chatbot_websocket_api_gateway.api_endpoint
}