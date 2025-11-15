'use client';

import { useState, useEffect, useRef } from 'react';
import { Message } from '../types';
import { startChat, sendChatMessage } from '../utils/api';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    initializeChat();
  }, []);

  const initializeChat = async () => {
    try {
      setIsLoading(true);
      const response = await startChat();
      setSessionId(response.session_id);

      addBotMessage(response.message);
    } catch (error) {
      addBotMessage('Sorry, I encountered an error starting the chat. Please refresh the page.');
      console.error('Failed to start chat:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const addUserMessage = (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  const addBotMessage = (content: string, metadata?: Message['metadata']) => {
    const newMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'bot',
      content,
      timestamp: new Date(),
      metadata,
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  const handleSendMessage = async (message: string) => {
    if (!sessionId || isLoading) return;

    addUserMessage(message);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(sessionId, message);

      addBotMessage(response.message, response.metadata);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      addBotMessage(`Error: ${errorMessage}`);
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      <div className="bg-blue-600 text-white px-6 py-4 rounded-t-lg">
        <h1 className="text-2xl font-bold">Package Tracking Assistant</h1>
        <p className="text-sm opacity-90">Track your packages and file claims</p>
      </div>

      <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900 px-6 py-4 border-x border-gray-200 dark:border-gray-700">
        {messages.length === 0 && !isLoading && (
          <div className="text-center text-gray-500 dark:text-gray-400 mt-8">
            <p>Initializing chat...</p>
          </div>
        )}

        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-200 dark:bg-gray-700 rounded-lg px-4 py-2">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="bg-white dark:bg-gray-800 px-6 py-4 rounded-b-lg border-x border-b border-gray-200 dark:border-gray-700">
        <ChatInput
          onSend={handleSendMessage}
          disabled={isLoading || !sessionId}
          placeholder="Type your message..."
        />

        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          <p>Sample tracking numbers: AB123456789 (in transit), CD555666777 (lost), XY987654321 (delivered)</p>
        </div>
      </div>
    </div>
  );
}
