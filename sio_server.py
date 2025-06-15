import socketio
import uvicorn

# Create Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = socketio.ASGIApp(sio)

# Store connected users
connected_users = {}

@sio.event
async def connect(sid, environ):
    print(f"User connected: {sid}")

@sio.event
async def join(sid, data):
    connected_users[data['username']] = sid
    await sio.emit('user_joined', {'username': data['username']})

@sio.event
async def send_message(sid, data):
    print(f"Message from {data['sender']} to {data['receiver']}: {data['message']}")
    
    # Emit back to receiver if online
    receiver_sid = connected_users.get(data['receiver'])
    if receiver_sid:
        await sio.emit('receive_message', data, to=receiver_sid)

@sio.event
async def disconnect(sid):
    print(f"User disconnected: {sid}")
    for username, user_sid in list(connected_users.items()):
        if user_sid == sid:
            del connected_users[username]
            break

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)
