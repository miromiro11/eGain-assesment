import { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.type === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
        {message.metadata && (
          <div className="mt-2 pt-2 border-t border-gray-300 dark:border-gray-600 text-xs opacity-80">
            {message.metadata.tracking_number && (
              <p>Tracking: {message.metadata.tracking_number}</p>
            )}
            {message.metadata.status && (
              <p>Status: {message.metadata.status}</p>
            )}
            {message.metadata.claim_id && (
              <p>Claim ID: {message.metadata.claim_id}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
