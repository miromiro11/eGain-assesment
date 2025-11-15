import fastapi
import uvicorn
from typing import Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import uuid
import re
from fastapi.middleware.cors import CORSMiddleware

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CookieStore:
    def __init__(self):
        self.store: Dict[str, Dict] = {}

    def set_cookie(self, key: str, value: str, max_age: Optional[int] = None):
        cookie_data = {
            "value": value,
            "created_at": datetime.now()
        }
        if max_age:
            cookie_data["expires_at"] = datetime.now() + timedelta(seconds=max_age)
        else:
            cookie_data["expires_at"] = None

        self.store[key] = cookie_data

    def get_cookie(self, key: str) -> Optional[str]:
        if key not in self.store:
            return None

        cookie_data = self.store[key]

        if cookie_data["expires_at"] and datetime.now() > cookie_data["expires_at"]:
            del self.store[key]
            return None

        return cookie_data["value"]

    def delete_cookie(self, key: str) -> bool:
        if key in self.store:
            del self.store[key]
            return True
        return False

    def clear_all(self):
        self.store.clear()

cookie_store = CookieStore()

package_data: Dict[str, Dict[str, str]] = {
    "AB123456789": {"status": "in_transit"},
    "XY987654321": {"status": "delivered"},
    "CD555666777": {"status": "lost"},
    "EF111222333": {"status": "in_transit"},
    "GH444555666": {"status": "lost"},
    "IJ777888999": {"status": "delivered"},
    "KL000111222": {"status": "in_transit"},
    "MN333444555": {"status": "lost"},
}

claims_data: Dict[str, Dict] = {}

conversation_state: Dict[str, Dict] = {}

class TrackRequest(BaseModel):
    session_id: str
    tracking_number: str

class ClaimRequest(BaseModel):
    session_id: str
    email: EmailStr
    tracking_number: str

class ChatMessageRequest(BaseModel):
    session_id: str
    message: str

def get_or_create_session(session_id: Optional[str] = None) -> str:
    if session_id and cookie_store.get_cookie(f"session_{session_id}"):
        return session_id

    new_session_id = str(uuid.uuid4())
    cookie_store.set_cookie(f"session_{new_session_id}", new_session_id, max_age=3600)
    return new_session_id

def validate_session(session_id: str) -> bool:
    return cookie_store.get_cookie(f"session_{session_id}") is not None

def validate_tracking_number(tracking_number: str) -> bool:
    pattern = r'^[A-Z]{2}\d{9}$'
    return bool(re.match(pattern, tracking_number))

@app.get("/")
def read_root(session_id: Optional[str] = None):
    session = get_or_create_session(session_id)
    return {
        "message": "Hello, World!",
        "session_id": session
    }

@app.get("/session")
def get_session(session_id: Optional[str] = None):
    session = get_or_create_session(session_id)
    return {"session_id": session}

def get_conversation_state(session_id: str) -> Dict:
    if session_id not in conversation_state:
        conversation_state[session_id] = {
            "step": "awaiting_tracking",
            "context": {}
        }
    return conversation_state[session_id]

def set_conversation_state(session_id: str, step: str, context: Dict = None):
    conversation_state[session_id] = {
        "step": step,
        "context": context or {}
    }

@app.get("/chat/start")
def chat_start(session_id: Optional[str] = None):
    session = get_or_create_session(session_id)
    set_conversation_state(session, "awaiting_tracking")
    return {
        "session_id": session,
        "message": "Hello! I'm your package tracking assistant. Please provide a tracking number to get started (e.g., AB123456789).",
        "bot_message": True
    }

@app.post("/chat/message")
def chat_message(request: ChatMessageRequest):
    if not validate_session(request.session_id):
        raise fastapi.HTTPException(
            status_code=401,
            detail="Invalid or expired session. Please start a new chat session."
        )

    state = get_conversation_state(request.session_id)
    user_message = request.message.strip()

    if state["step"] == "awaiting_tracking":
        return handle_tracking_input(request.session_id, user_message)

    elif state["step"] == "awaiting_claim_confirmation":
        return handle_claim_confirmation(request.session_id, user_message, state["context"])

    elif state["step"] == "awaiting_claim_email":
        return handle_claim_email(request.session_id, user_message, state["context"])

    else:
        set_conversation_state(request.session_id, "awaiting_tracking")
        return {
            "message": "I'm not sure what you're asking. Please provide a tracking number to track a package.",
            "bot_message": True
        }

def handle_tracking_input(session_id: str, tracking_number: str) -> Dict:
    if not validate_tracking_number(tracking_number):
        return {
            "message": "Invalid tracking number format. Please enter a valid tracking number (2 uppercase letters followed by 9 digits, e.g., AB123456789).",
            "bot_message": True,
            "error": "invalid_format"
        }

    if tracking_number not in package_data:
        return {
            "message": f"Tracking number {tracking_number} was not found in our system. Please verify the number and try again.",
            "bot_message": True,
            "error": "not_found"
        }

    status = package_data[tracking_number]["status"]

    if status == "in_transit":
        set_conversation_state(session_id, "awaiting_tracking")
        return {
            "message": f"Your package {tracking_number} is currently in transit and on its way to you. Is there anything else I can help you with? You can provide another tracking number.",
            "bot_message": True,
            "metadata": {
                "tracking_number": tracking_number,
                "status": status
            }
        }

    elif status == "delivered":
        set_conversation_state(session_id, "awaiting_tracking")
        return {
            "message": f"Your package {tracking_number} has been delivered. Is there anything else I can help you with? You can provide another tracking number.",
            "bot_message": True,
            "metadata": {
                "tracking_number": tracking_number,
                "status": status
            }
        }

    elif status == "lost":
        set_conversation_state(session_id, "awaiting_claim_confirmation", {
            "tracking_number": tracking_number
        })
        return {
            "message": f"Unfortunately, package {tracking_number} appears to be lost. Would you like to file a claim? (Please reply 'yes' or 'no')",
            "bot_message": True,
            "metadata": {
                "tracking_number": tracking_number,
                "status": status
            }
        }

    else:
        set_conversation_state(session_id, "awaiting_tracking")
        return {
            "message": f"Package status: {status}. Is there anything else I can help you with?",
            "bot_message": True,
            "metadata": {
                "tracking_number": tracking_number,
                "status": status
            }
        }

def handle_claim_confirmation(session_id: str, user_input: str, context: Dict) -> Dict:
    user_input_lower = user_input.lower()

    if user_input_lower in ["yes", "y", "yeah", "sure", "ok", "okay"]:
        set_conversation_state(session_id, "awaiting_claim_email", context)
        return {
            "message": "Great! To file the claim, please provide your email address.",
            "bot_message": True
        }

    elif user_input_lower in ["no", "n", "nah", "nope"]:
        set_conversation_state(session_id, "awaiting_tracking")
        return {
            "message": "Okay, no problem. Is there anything else I can help you with? You can provide another tracking number.",
            "bot_message": True
        }

    else:
        return {
            "message": "I didn't quite understand. Would you like to file a claim for your lost package? Please reply 'yes' or 'no'.",
            "bot_message": True
        }

def handle_claim_email(session_id: str, email: str, context: Dict) -> Dict:
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_regex, email):
        return {
            "message": "That doesn't look like a valid email address. Please provide a valid email (e.g., user@example.com).",
            "bot_message": True,
            "error": "invalid_email"
        }

    tracking_number = context.get("tracking_number")
    if not tracking_number:
        set_conversation_state(session_id, "awaiting_tracking")
        return {
            "message": "Sorry, I lost track of the tracking number. Please start over by providing the tracking number.",
            "bot_message": True,
            "error": "lost_context"
        }

    if tracking_number not in package_data or package_data[tracking_number]["status"] != "lost":
        set_conversation_state(session_id, "awaiting_tracking")
        return {
            "message": "Sorry, this package is no longer eligible for a claim. Please provide another tracking number if you need assistance.",
            "bot_message": True,
            "error": "not_eligible"
        }

    claim_id = str(uuid.uuid4())
    claims_data[claim_id] = {
        "claim_id": claim_id,
        "email": email,
        "tracking_number": tracking_number,
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }

    set_conversation_state(session_id, "awaiting_tracking")

    return {
        "message": f"Your claim has been successfully filed! We'll contact you at {email} with updates. Your claim ID is {claim_id}. Is there anything else I can help you with?",
        "bot_message": True,
        "metadata": {
            "claim_id": claim_id,
            "tracking_number": tracking_number,
            "email": email
        }
    }

@app.post("/chat/track")
def chat_track(request: TrackRequest):
    if not validate_session(request.session_id):
        raise fastapi.HTTPException(
            status_code=401,
            detail="Invalid or expired session. Please start a new chat session."
        )

    if not validate_tracking_number(request.tracking_number):
        return {
            "step": "invalid_format",
            "message": "Invalid tracking number format. Please enter a valid tracking number (2 uppercase letters followed by 9 digits, e.g., AB123456789).",
            "error": "invalid_format"
        }

    if request.tracking_number not in package_data:
        return {
            "step": "not_found",
            "message": f"Tracking number {request.tracking_number} was not found in our system. Please verify the number and try again.",
            "error": "not_found"
        }

    status = package_data[request.tracking_number]["status"]

    status_messages = {
        "in_transit": f"Your package {request.tracking_number} is currently in transit and on its way to you.",
        "delivered": f"Your package {request.tracking_number} has been delivered.",
        "lost": f"Unfortunately, package {request.tracking_number} appears to be lost. Would you like to file a claim?"
    }

    return {
        "step": "status_found",
        "tracking_number": request.tracking_number,
        "status": status,
        "message": status_messages.get(status, "Status unknown"),
        "can_claim": status == "lost"
    }

@app.get("/chat/status")
def chat_status(session_id: str, tracking: str):
    if not validate_session(session_id):
        raise fastapi.HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    if not validate_tracking_number(tracking):
        raise fastapi.HTTPException(
            status_code=400,
            detail="Invalid tracking number format"
        )

    if tracking not in package_data:
        raise fastapi.HTTPException(
            status_code=404,
            detail="Tracking number not found"
        )

    return {
        "tracking": tracking,
        "status": package_data[tracking]["status"]
    }

@app.post("/chat/claim")
def chat_claim(request: ClaimRequest):
    if not validate_session(request.session_id):
        raise fastapi.HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    if not validate_tracking_number(request.tracking_number):
        raise fastapi.HTTPException(
            status_code=400,
            detail="Invalid tracking number format"
        )

    if request.tracking_number not in package_data:
        raise fastapi.HTTPException(
            status_code=404,
            detail="Tracking number not found"
        )

    package_status = package_data[request.tracking_number]["status"]
    if package_status != "lost":
        return {
            "step": "claim_denied",
            "message": f"Claims can only be filed for lost packages. This package is currently: {package_status}",
            "error": "not_lost",
            "status": package_status
        }

    claim_id = str(uuid.uuid4())
    claims_data[claim_id] = {
        "claim_id": claim_id,
        "email": request.email,
        "tracking_number": request.tracking_number,
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }

    return {
        "step": "claim_created",
        "message": f"Your claim has been successfully filed. We'll contact you at {request.email} with updates.",
        "claim_id": claim_id,
        "tracking_number": request.tracking_number,
        "email": request.email
    }

@app.get("/chat/claim/{claim_id}")
def get_claim(claim_id: str, session_id: Optional[str] = None):
    if session_id and not validate_session(session_id):
        raise fastapi.HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    if claim_id not in claims_data:
        raise fastapi.HTTPException(
            status_code=404,
            detail="Claim not found"
        )

    return claims_data[claim_id]

@app.post("/cookies/{key}")
def set_cookie(key: str, value: str, max_age: Optional[int] = None):
    cookie_store.set_cookie(key, value, max_age)
    return {"status": "success", "key": key, "value": value}

@app.get("/cookies/{key}")
def get_cookie(key: str):
    value = cookie_store.get_cookie(key)
    if value is None:
        raise fastapi.HTTPException(status_code=404, detail="Cookie not found or expired")
    return {"key": key, "value": value}

@app.delete("/cookies/{key}")
def delete_cookie(key: str):
    deleted = cookie_store.delete_cookie(key)
    if not deleted:
        raise fastapi.HTTPException(status_code=404, detail="Cookie not found")
    return {"status": "success", "message": f"Cookie '{key}' deleted"}

@app.delete("/cookies")
def clear_all_cookies():
    cookie_store.clear_all()
    return {"status": "success", "message": "All cookies cleared"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
