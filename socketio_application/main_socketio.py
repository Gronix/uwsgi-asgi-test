import asyncio
import collections
import os
import socketio
import urllib.parse


debug_mode = os.environ.get('SOCKETIO_DEBUG', True)

sio = socketio.AsyncServer(
    async_mode='asgi',
    logger=True,
    engineio_logger=True,
    cors_allowed_origins='*',  # <- WARNING: dont do this into production
)

TOKEN_SIDS = collections.defaultdict(set)
MSG_COUNT = collections.defaultdict(int)


async def notify_room(room):
    if debug_mode:
        print(f'Start sending notification into {room}', flush=True)
    while len(TOKEN_SIDS[room]) > 0:
        if debug_mode:
            print(f'Emit message into room "{room}"', flush=True)
        msg = f"Bump message #{MSG_COUNT[room]}"
        MSG_COUNT[room] += 1
        await sio.emit('message', data=msg, room=room, namespace='/chat')
        await asyncio.sleep(3.0)

    if debug_mode:
        print(f'Stop sending notifications into {room} (sent {MSG_COUNT[room]})', flush=True)
    MSG_COUNT.pop(room)


class TestNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ):
        if debug_mode:
            print(f'Get new connection: {sid} \n{environ}\n\n', flush=True)
        token = urllib.parse.parse_qs(environ.get('QUERY_STRING', '')).get('token', [''])[0]
        TOKEN_SIDS[token].add(sid)
        async with sio.session(sid) as user_session:
            # start sending notifications
            user_session['token'] = token
            sio.enter_room(sid, token, self.namespace)
            if len(TOKEN_SIDS[token]) == 1:
                sio.start_background_task(notify_room, token)

    async def on_disconnect(self, sid):
        async with sio.session(sid) as user_session:
            # stop sending notifications
            token = user_session['token']
            TOKEN_SIDS[token].remove(sid)
            sio.leave_room(sid, room=token, namespace=self.namespace)
            if debug_mode:
                print(f'Connection closed: {sid}\n\n', flush=True)

    async def on_message(self, sid, data):
        if debug_mode:
            print(f'Get new message event from: {sid}\nwith data:\n{data}\n\n', flush=True)
        async with sio.session(sid) as user_session:
            token = user_session.get('token', sid)
            await self.emit('message', f'{sid} send: {data}', room=token, namespace=self.namespace)


sio.register_namespace(TestNamespace('/chat'))

app = socketio.ASGIApp(sio, static_files={'': 'index.html'})

print('x' * 1000, flush=True)
