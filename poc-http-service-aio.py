from aiohttp import web


async def handle_root(request):
    """Handle root endpoint"""
    return web.Response(text="Hello, World!")


async def handle_json(request):
    """Return JSON response"""
    data = {
        "message": "Hello from aiohttp!",
        "status": "success",
        "timestamp": "2024-01-01T12:00:00Z"
    }
    return web.json_response(data)


async def handle_post(request):
    """Handle POST request"""
    try:
        # Parse JSON from request body
        data = await request.json()
        response_data = {
            "received": data,
            "processed": True
        }
        return web.json_response(response_data, status=201)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)


async def handle_greet(request):
    """Handle path parameter"""
    name = request.match_info.get('name', 'Anonymous')
    return web.Response(text=f"Hello, {name}!")


async def handle_query(request):
    """Handle query parameters"""
    name = request.query.get('name', 'World')
    age = request.query.get('age', 'unknown')
    return web.json_response({
        "greeting": f"Hello {name}!",
        "age": age
    })


# Create application and setup routes
app = web.Application()

# Add routes
app.router.add_get('/', handle_root)
app.router.add_get('/json', handle_json)
app.router.add_post('/api/data', handle_post)
app.router.add_get('/greet/{name}', handle_greet)
app.router.add_get('/query', handle_query)

if __name__ == '__main__':
    # Configure and run server
    web.run_app(
        app,
        host='127.0.0.1',
        port=1967,
        access_log=None  # Remove for production logging
    )
