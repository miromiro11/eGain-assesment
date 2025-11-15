# Package Tracking Chatbot

A conversational AI chatbot for tracking packages and filing claims for lost items.

## Setup Instructions

### Backend Setup

1. Navigate to backend folder:

```bash
cd backend
```

2. Install dependencies:

```bash
pip install fastapi==0.115.0 uvicorn==0.32.0 pydantic==2.12.4
```

3. Run the server:

```bash
python main.py
```

Server runs on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend folder:

```bash
cd frontend
```

2. Install dependencies:

```bash
yarn install
```

3. Run the development server:

```bash
yarn run dev
```

App runs on `http://localhost:3000`

## How It Works

The chatbot uses a state machine to manage conversations:

1. **Tracking State**: User enters a tracking number
2. **Lost Package Detection**: If package is lost, asks if they want to file a claim
3. **Claim Confirmation**: User confirms yes/no
4. **Email Collection**: Collects email for claim filing
5. **Claim Created**: Generates claim ID and resets to tracking state

### Tech Stack

- **Backend**: FastAPI (Python) with in-memory session storage
- **Frontend**: Next.js 16 + React 19 + TypeScript + Tailwind CSS
- **Communication**: REST API

### Sample Tracking Numbers

Use these to test different scenarios:

- `AB123456789` - Package in transit
- `CD555666777` - Lost package (triggers claim flow)
- `XY987654321` - Delivered package

## Example Usage

### 1. Tracking a Package

**User:** `AB123456789`

**Bot:** "Your package AB123456789 is currently in transit. It should arrive soon!"

### 2. Filing a Claim

**User:** `CD555666777`

**Bot:** "We're sorry, but package CD555666777 appears to be lost. Would you like to file a claim? (yes/no)"

**User:** `yes`

**Bot:** "Please provide your email address to file the claim."

**User:** `john@example.com`

**Bot:** "Your claim has been filed successfully! Your claim ID is: abc-123-def. You will receive updates at john@example.com"

### 3. Checking Package Status

**User:** `XY987654321`

**Bot:** "Good news! Your package XY987654321 has been delivered."

## Features

- Session-based conversation memory
- Tracking number validation (format: 2 letters + 9 digits)
- Email validation for claims
- Auto-scrolling chat interface
- Dark mode support
- Loading states with animated indicators
- Metadata display (tracking numbers, claim IDs)
