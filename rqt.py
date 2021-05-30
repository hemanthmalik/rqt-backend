import asyncio
from functools import partial, wraps

from quart import (
    copy_current_websocket_context, Quart, render_template, 
    request, websocket
)

app = Quart(__name__)

connected_websockets = set()

def collect_websocket(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        global connected_websockets
        queue = asyncio.Queue()
        connected_websockets.add(queue)
        try:
            return await func(queue, *args, **kwargs)
        finally:
            connected_websockets.remove(queue)
    return wrapper

async def broadcast(message):
    global connected_websockets 
    for queue in connected_websockets:
        await queue.put(message)

@app.route('/')
async def index():
    return await render_template('main.html')

@app.websocket('/ws')
@collect_websocket
async def ws(queue):
    await websocket.accept()
    while True:
        data = await queue.get()
        await websocket.send_json(data)

@app.route('/telepath', methods=['POST'])
async def telepath():   
    data = await request.get_json()
    await broadcast(data.get('message', 'blank message'))
    return {}

if __name__ == '__main__':
    app.run(port=5000)