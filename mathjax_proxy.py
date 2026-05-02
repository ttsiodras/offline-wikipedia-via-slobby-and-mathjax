#!/usr/bin/env python3
"""
Proxy server that forwards requests to the Slobby Wikipedia server at 127.0.0.1:8013,
but modifies HTML responses to render math formulas using MathJax instead of broken images.
Uses BeautifulSoup-based filter_logic for reliable HTML parsing.
"""

import asyncio
import logging
import os
from aiohttp import web
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import common filter logic using BeautifulSoup
from filter_logic import process_html_response

# Target Slobby server - use environment variables with defaults
TARGET_HOST = os.environ.get('TARGET_HOST', '127.0.0.1')
TARGET_PORT = int(os.environ.get('TARGET_PORT', '8013'))
PROXY_PORT = int(os.environ.get('PROXY_PORT', '8014'))

# HTTP client timeout configuration
HTTP_TIMEOUT = 30.0  # seconds

# Hop-by-hop headers to exclude from forwarding
HOP_BY_HOP_HEADERS = {
    'host', 'connection', 'keep-alive', 'transfer-encoding',
    'proxy-authenticate', 'proxy-authorization', 'te', 'trailers',
    'upgrade', 'expect'
}


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

    logger.debug(f"Proxying {request.method} {path} to {target_url}")

    try:
        # Forward the request to the target server using the shared client
        response = await request.app['http_client'].request(
            request.method,
            target_url,
            headers={
                key: value for key, value in request.headers.items()
                if key.lower() not in HOP_BY_HOP_HEADERS
            },
            timeout=HTTP_TIMEOUT
        )

        # Get the response content
        content = response.content

        # Check if this is HTML content that needs processing
        content_type = response.headers.get('content-type', '')

        if 'text/html' in content_type:
            # Decode and process the HTML
            try:
                html_content = content.decode('utf-8')
                html_content = process_html_response(html_content)
                content = html_content.encode('utf-8')
                logger.debug(f"Processed HTML for {path}")
            except UnicodeDecodeError as e:
                logger.warning(f"Failed to decode HTML for {path}: {e}")

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
        logger.error(f"Cannot connect to target server at {TARGET_HOST}:{TARGET_PORT}: {e}")
        return web.Response(
            text=f"Error: Cannot connect to target server at {TARGET_HOST}:{TARGET_PORT}.",
            status=502
        )
    except httpx.TimeoutException as e:
        logger.error(f"Timeout waiting for target server at {TARGET_HOST}:{TARGET_PORT}: {e}")
        return web.Response(
            text=f"Error: Timeout connecting to target server.",
            status=504
        )
    except Exception as e:
        logger.error(f"Error proxying request to {target_url}: {e}")
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


async def startup_handler(app):
    """Initialize HTTP client on startup."""
    app['http_client'] = httpx.AsyncClient(
        timeout=HTTP_TIMEOUT,
        follow_redirects=False  # Don't follow redirects, return them to client
    )
    logger.info(f"HTTP client initialized with {HTTP_TIMEOUT}s timeout")


async def shutdown_handler(app):
    """Cleanup HTTP client on shutdown."""
    if 'http_client' in app:
        await app['http_client'].aclose()
        logger.info("HTTP client closed")


def main():
    """Main entry point."""
    app = create_app()

    # Add startup/shutdown handlers
    app.on_startup.append(startup_handler)
    app.on_cleanup.append(shutdown_handler)

    logger.info("Starting MathJax proxy server...")
    logger.info(f"Target: http://{TARGET_HOST}:{TARGET_PORT}")
    logger.info(f"Listening on: http://0.0.0.0:{PROXY_PORT}")
    logger.info("Math formulas will be rendered using MathJax instead of broken images.")
    logger.info("Press Ctrl+C to stop.")

    web.run_app(app, host='0.0.0.0', port=PROXY_PORT, print=None)


if __name__ == '__main__':
    main()
