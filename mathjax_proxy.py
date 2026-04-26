#!/usr/bin/env python3
"""
Proxy server that forwards requests to the Slobby Wikipedia server at 127.0.0.1:8013,
but modifies HTML responses to render math formulas using MathJax instead of broken images.
Uses BeautifulSoup-based filter_logic for reliable HTML parsing.
"""

import asyncio
import httpx
import os
from aiohttp import web

# Import common filter logic using BeautifulSoup
from filter_logic import process_math_elements, add_mathjax_script

# Target Slobby server - use environment variables with defaults
TARGET_HOST = os.environ.get('TARGET_HOST', '127.0.0.1')
TARGET_PORT = int(os.environ.get('TARGET_PORT', '8013'))


def process_html_response(html_content: str) -> str:
    """Process HTML content to enable MathJax rendering."""
    # Use the common filter logic (BeautifulSoup-based)
    html_content = process_math_elements(html_content)
    # Add MathJax script
    html_content = add_mathjax_script(html_content)
    return html_content


async def handle_request(request: web.Request) -> web.Response:
    """Handle incoming requests by proxying to the target server."""
    
    # Get the path and query string
    path = request.path
    query_string = request.query_string
    
    # Build the target URL
    if query_string:
        target_url = f"http://{TARGET_HOST}:{TARGET_PORT}{path}?{query_string}"
    else:
        target_url = f"http://{TARGET_HOST}:{TARGET_PORT}{path}"
    
    try:
        # Forward the request to the target server
        async with httpx.AsyncClient() as client:
            # Get all headers except hop-by-hop headers
            headers = {
                key: value for key, value in request.headers.items()
                if key.lower() not in ('host', 'connection', 'keep-alive', 'transfer-encoding')
            }
            
            response = await client.get(
                target_url,
                headers=headers,
                timeout=30.0
            )
            
            # Get the response content
            content = response.content
            
            # Check if this is HTML content that needs processing
            content_type = response.headers.get('content-type', '')
            
            if 'text/html' in content_type:
                # Decode and process the HTML
                html_content = content.decode('utf-8')
                html_content = process_html_response(html_content)
                content = html_content.encode('utf-8')
            
            # Create response
            content_type = response.headers.get('content-type', 'text/html')
            # Remove charset from content_type if present (web.Response handles encoding separately)
            if ';' in content_type:
                content_type = content_type.split(';')[0].strip()
            
            response_obj = web.Response(
                body=content,
                status=response.status_code,
                content_type=content_type,
                charset='utf-8'
            )
            
            # Copy relevant headers
            for header in ('cache-control', 'expires', 'last-modified'):
                if header in response.headers:
                    response_obj.headers[header] = response.headers[header]
            
            return response_obj
            
    except httpx.ConnectError as e:
        return web.Response(
            text=f"Error: Cannot connect to target server at {TARGET_HOST}:{TARGET_PORT}. {str(e)}",
            status=502
        )
    except Exception as e:
        return web.Response(
            text=f"Error: {str(e)}",
            status=500
        )


async def handle_root(request: web.Request) -> web.Response:
    """Handle root path by redirecting to the lookup page."""
    return web.HTTPFound(f"/lookup")


def create_app() -> web.Application:
    """Create and configure the web application."""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/', handle_root)
    app.router.add_get('/lookup', handle_request)
    app.router.add_get('/dictionaries', handle_request)
    app.router.add_get('/slob/{path:.*}', handle_request)
    app.router.add_get('/~/{path:.*}', handle_request)
    app.router.add_get('/{path:.*}', handle_request)
    
    return app


def main():
    """Main entry point."""
    app = create_app()
    print(f"Starting MathJax proxy server...", flush=True)
    print(f"Target: http://{TARGET_HOST}:{TARGET_PORT}", flush=True)
    print(f"Listening on: http://0.0.0.0:8014", flush=True)
    print(f"\nMath formulas will be rendered using MathJax instead of broken images.", flush=True)
    print("Press Ctrl+C to stop.\n", flush=True)
    
    web.run_app(app, host='0.0.0.0', port=8014, print=None)


if __name__ == '__main__':
    main()
