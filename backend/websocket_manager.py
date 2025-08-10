from fastapi import WebSocket
from typing import Dict, List
import json
import jwt
import os
from database import SessionLocal
from models.leave_requests import User

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

class ConnectionManager:
    def __init__(self):
        # Store active connections: {user_id: WebSocket}
        self.active_connections: Dict[int, WebSocket] = {}
        # Store user info: {user_id: {"name": str, "email": str, "role": str}}
        self.user_info: Dict[int, dict] = {}

    async def connect(self, websocket: WebSocket, token: str):
        """Connect a WebSocket with JWT authentication"""
        try:
            # Verify JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            email = payload.get("sub")

            if not user_id or not email:
                await websocket.close(code=4001, reason="Invalid token")
                return None

            # Verify user exists in database
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id, User.email == email).first()
                if not user or not user.validated:
                    await websocket.close(code=4002, reason="User not found or not validated")
                    return None

                # Accept the connection
                await websocket.accept()

                # Store connection and user info
                self.active_connections[user_id] = websocket
                self.user_info[user_id] = {
                    "name": user.name,
                    "email": user.email,
                    "role": user.role
                }

                # Send welcome message
                await self.send_personal_message(
                    {
                        "type": "connection_established",
                        "message": f"Welcome {user.name}! You are now connected.",
                        "user_id": user_id,
                        "user_info": self.user_info[user_id]
                    },
                    user_id
                )

                return user_id

            finally:
                db.close()

        except jwt.ExpiredSignatureError:
            await websocket.close(code=4003, reason="Token expired")
            return None
        except jwt.InvalidTokenError:
            await websocket.close(code=4004, reason="Invalid token")
            return None
        except Exception as e:
            await websocket.close(code=4005, reason=f"Authentication error: {str(e)}")
            return None

    def disconnect(self, user_id: int):
        """Disconnect a WebSocket"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_info:
            del self.user_info[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending message to user {user_id}: {e}")
                # Remove the connection if it's broken
                self.disconnect(user_id)

    async def send_notification_to_user(self, user_id: int, notification_type: str, data: dict):
        """Send a notification to a specific user"""
        message = {
            "type": "notification",
            "notification_type": notification_type,
            "data": data,
            "timestamp": data.get("timestamp")
        }
        await self.send_personal_message(message, user_id)

    async def broadcast_to_managers(self, message: dict):
        """Send a message to all connected managers"""
        for user_id, user_info in self.user_info.items():
            if user_info.get("role") == "manager":
                await self.send_personal_message(message, user_id)

    async def broadcast_to_all(self, message: dict):
        """Send a message to all connected users"""
        for user_id in self.active_connections:
            await self.send_personal_message(message, user_id)

    def get_connected_users(self) -> List[dict]:
        """Get list of connected users"""
        return [
            {"user_id": user_id, **user_info}
            for user_id, user_info in self.user_info.items()
        ]

    def is_user_connected(self, user_id: int) -> bool:
        """Check if a user is connected"""
        return user_id in self.active_connections

# Global connection manager instance
manager = ConnectionManager()
