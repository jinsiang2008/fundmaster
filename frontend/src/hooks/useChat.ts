/**
 * Custom hooks for chat functionality
 */

import { useState, useCallback } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { ChatRequest, ChatMessage, UserProfile } from '../types/chat';

// Query keys
export const chatKeys = {
  all: ['chat'] as const,
  session: (sessionId: string) => [...chatKeys.all, 'session', sessionId] as const,
  messages: (sessionId: string) => [...chatKeys.all, 'messages', sessionId] as const,
};

/**
 * Hook for managing chat sessions and messages
 */
export function useChat(fundCode: string) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');

  // Create session mutation
  const createSession = useMutation({
    mutationFn: () => apiClient.createChatSession({ fund_code: fundCode }),
    onSuccess: (data) => {
      setSessionId(data.session_id);
    },
  });

  // Send message (non-streaming)
  const sendMessage = useMutation({
    mutationFn: (request: ChatRequest) => apiClient.sendChatMessage(request),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.message, timestamp: data.timestamp },
      ]);
    },
  });

  // Send message with streaming
  const sendMessageStream = useCallback(
    async (message: string, userProfile?: UserProfile) => {
      // Add user message immediately
      const userMessage: ChatMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      setIsStreaming(true);
      setStreamingContent('');

      try {
        const request: ChatRequest = {
          session_id: sessionId || undefined,
          fund_code: sessionId ? undefined : fundCode,
          message,
          user_profile: userProfile,
        };

        let fullContent = '';
        const newSessionId = await apiClient.sendChatMessageStream(request, (chunk) => {
          fullContent += chunk;
          setStreamingContent(fullContent);
        });

        // Update session ID if this was a new session
        if (!sessionId && newSessionId) {
          setSessionId(newSessionId);
        }

        // Add complete assistant message
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: fullContent,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (error) {
        console.error('Chat stream error:', error);
        const hint =
          error instanceof Error && error.message
            ? error.message
            : '抱歉，发生了错误，请稍后重试。';
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `抱歉，发生了错误：${hint}`,
            timestamp: new Date().toISOString(),
          },
        ]);
      } finally {
        setIsStreaming(false);
        setStreamingContent('');
      }
    },
    [sessionId, fundCode]
  );

  // Get chat history
  const { data: chatHistory } = useQuery({
    queryKey: chatKeys.messages(sessionId || ''),
    queryFn: () => apiClient.getChatMessages(sessionId!),
    enabled: !!sessionId,
  });

  // Reset chat
  const resetChat = useCallback(() => {
    setSessionId(null);
    setMessages([]);
    setStreamingContent('');
  }, []);

  return {
    sessionId,
    messages,
    isStreaming,
    streamingContent,
    createSession,
    sendMessage,
    sendMessageStream,
    chatHistory,
    resetChat,
  };
}

/**
 * Hook for updating user profile
 */
export function useUpdateUserProfile() {
  return useMutation({
    mutationFn: ({ sessionId, profile }: { sessionId: string; profile: UserProfile }) =>
      apiClient.updateUserProfile(sessionId, profile),
  });
}
