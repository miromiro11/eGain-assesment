import { ChatStartResponse, TrackResponse, ClaimResponse, ClaimDetails } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export async function startChat(sessionId?: string): Promise<ChatStartResponse> {
  const endpoint = sessionId ? `/chat/start?session_id=${sessionId}` : '/chat/start';
  return apiFetch<ChatStartResponse>(endpoint);
}

export async function sendChatMessage(
  sessionId: string,
  message: string
): Promise<{
  message: string;
  bot_message: boolean;
  metadata?: {
    tracking_number?: string;
    status?: string;
    claim_id?: string;
    email?: string;
  };
  error?: string;
}> {
  return apiFetch('/chat/message', {
    method: 'POST',
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
    }),
  });
}

export async function trackPackage(
  sessionId: string,
  trackingNumber: string
): Promise<TrackResponse> {
  return apiFetch<TrackResponse>('/chat/track', {
    method: 'POST',
    body: JSON.stringify({
      session_id: sessionId,
      tracking_number: trackingNumber,
    }),
  });
}

export async function fileClaim(
  sessionId: string,
  email: string,
  trackingNumber: string
): Promise<ClaimResponse> {
  return apiFetch<ClaimResponse>('/chat/claim', {
    method: 'POST',
    body: JSON.stringify({
      session_id: sessionId,
      email: email,
      tracking_number: trackingNumber,
    }),
  });
}

export async function getClaimDetails(
  claimId: string,
  sessionId?: string
): Promise<ClaimDetails> {
  const endpoint = sessionId
    ? `/chat/claim/${claimId}?session_id=${sessionId}`
    : `/chat/claim/${claimId}`;
  return apiFetch<ClaimDetails>(endpoint);
}

export async function getSession(sessionId?: string): Promise<{ session_id: string }> {
  const endpoint = sessionId ? `/session?session_id=${sessionId}` : '/session';
  return apiFetch<{ session_id: string }>(endpoint);
}
