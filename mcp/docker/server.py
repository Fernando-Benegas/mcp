from fastmcp import FastMCP, Context

# Create an MCP server with a descriptive name
mcp = FastMCP(
    name="Weather Service",
    instructions="""
    This server provides weather information and greeting capabilities.
    
    Use the say_hello tool to check connectivity.
    Use the get_weather tool to fetch current weather for a given location.
    """
)
# Basic greeting tool
@mcp.tool()
def say_hello(name: str = "World") -> str:
    """A simple tool that greets a person by name"""
    return f"Hello, {name}! This is your MCP server running on Python! 🚀"
# Weather information tool
@mcp.tool()
async def get_weather(city: str, country: str = "US") -> str:
    """
    Get current weather information for a city
    
    Args:
        city: Name of the city
        country: Country code (default: US)
    """
    # This is a mock implementation - in a real app, you'd call a weather API
    import random
    conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy"]
    temp = random.randint(40, 90)
    
    return f"Current weather in {city}, {country}: {random.choice(conditions)}, {temp}°F"
# Run the server when executed directly
if __name__ == "__main__":
    import os
    
    # Set default host and port
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8080"))
    
    # Determine transport from environment
    transport = os.environ.get("MCP_TRANSPORT", "sse")
    
    print(f"Starting server with transport={transport}, host={host}, port={port}")
    mcp.run(transport=transport, host=host, port=port)

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Health check handler
async def health_handler(request):
    """Handle health check requests"""
    return JSONResponse({"status": "healthy"})
# Run the server with both transport protocols
if __name__ == "__main__":
    import os
    
    # Set default host and port
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8080"))
    
    # Determine transport from environment
    transport = os.environ.get("MCP_TRANSPORT", "sse")
    
    print(f"Starting server with transport={transport}, host={host}, port={port}")
    
    if transport in ["sse", "streamable-http"]:
        # Create routes and middleware
        routes = [
            Route("/health", endpoint=health_handler, methods=["GET"])
        ]
        
        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["GET", "POST", "OPTIONS"],
                allow_headers=["*", "Mcp-Session-Id", "Last-Event-Id"],
                expose_headers=["Mcp-Session-Id"]
            )
        ]
        
        # Create the Starlette app
        app = Starlette(routes=routes, middleware=middleware)
        
        # Generate MCP app based on transport
        if transport == "sse":
            # Handle old HTTP+SSE protocol
            mcp_app = mcp.sse_app()
            mcp_path = "/sse"
            messages_path = "/messages"
            print("Starting with SSE transport at /sse endpoint")
            
            # Define the ASGI application to handle routing
            async def combined_app(scope, receive, send):
                path = scope.get("path", "")
                
                if path == "/health":
                    # Route health checks
                    await app(scope, receive, send)
                elif path == mcp_path:
                    # Route SSE requests
                    await mcp_app(scope, receive, send)
                elif path.startswith(messages_path):
                    # Handle messages in the old HTTP+SSE protocol
                    method = scope.get("method", "")
                    if method == "POST":
                        await mcp_app(scope, receive, send)
                    else:
                        await app(scope, receive, send)
                else:
                    # Default handling
                    await app(scope, receive, send)
        
        else:  # streamable-http
            # Handle new Streamable HTTP protocol
            mcp_app = mcp.sse_app()  # Still uses sse_app but handles it differently
            mcp_path = "/mcp"
            print("Starting with Streamable HTTP transport at /mcp endpoint")
            
            # Define the ASGI application
            async def combined_app(scope, receive, send):
                path = scope.get("path", "")
                
                if path == "/health":
                    # Route health checks
                    await app(scope, receive, send)
                elif path == mcp_path:
                    # For streamable HTTP, handle both GET and POST at a single endpoint
                    method = scope.get("method", "")
                    
                    if method in ["GET", "POST"]:
                        # Handle both methods through the MCP app
                        await mcp_app(scope, receive, send)
                    else:
                        await app(scope, receive, send)
                else:
                    # Default handling
                    await app(scope, receive, send)
        
        # Run the combined app
        uvicorn.run(
            combined_app,
            host=host,
            port=port,
            log_level="info"
        )
    else:
        # For other transports like stdio
        mcp.run(transport=transport, host=host, port=port)