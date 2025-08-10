from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from websocket_manager import manager
from datetime import datetime
import json

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """WebSocket endpoint for real-time notifications"""
    user_id = None
    try:
        # Connect with JWT authentication
        user_id = await manager.connect(websocket, token)
        
        if user_id is None:
            return  # Connection failed, already closed by manager
        
        # Keep the connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from the client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, user_id)
                
                elif message.get("type") == "get_connected_users":
                    # Only managers can see connected users
                    user_info = manager.user_info.get(user_id, {})
                    if user_info.get("role") == "manager":
                        await manager.send_personal_message({
                            "type": "connected_users",
                            "users": manager.get_connected_users()
                        }, user_id)
                    else:
                        await manager.send_personal_message({
                            "type": "error",
                            "message": "Unauthorized: Only managers can view connected users"
                        }, user_id)
                
                else:
                    # Unknown message type
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown message type: {message.get('type')}"
                    }, user_id)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, user_id)
                
    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(user_id)
            print(f"User {user_id} disconnected")
    except Exception as e:
        if user_id:
            manager.disconnect(user_id)
        print(f"WebSocket error: {e}")

@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status (for debugging)"""
    return {
        "connected_users_count": len(manager.active_connections),
        "connected_users": manager.get_connected_users(),
        "status": "WebSocket endpoint is running"
    }
