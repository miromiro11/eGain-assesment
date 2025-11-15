export interface ChatStartResponse {
  session_id: string;
  step: string;
  message: string;
}

export interface TrackResponse {
  step: string;
  tracking_number?: string;
  status?: string;
  message: string;
  can_claim?: boolean;
  error?: string;
}

export interface ClaimResponse {
  step: string;
  message: string;
  claim_id?: string;
  tracking_number?: string;
  email?: string;
  error?: string;
  status?: string;
}

export interface ClaimDetails {
  claim_id: string;
  email: string;
  tracking_number: string;
  created_at: string;
  status: string;
}

export interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  metadata?: {
    tracking_number?: string;
    status?: string;
    claim_id?: string;
  };
}

export type ChatStep = 'initial' | 'tracking' | 'tracking_result' | 'claim_prompt' | 'claim_email' | 'claim_complete';

export interface ChatState {
  messages: Message[];
  sessionId: string | null;
  currentStep: ChatStep;
  currentTrackingNumber: string | null;
  isLoading: boolean;
}
