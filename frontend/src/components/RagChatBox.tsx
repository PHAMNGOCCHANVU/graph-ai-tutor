// src/components/RagChatBox.tsx
"use client";
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Sparkles, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getRagExplanationStreamUrl } from '@/services/api';

interface ChatMessage {
  role: 'user' | 'ai' | 'system';
  content: string;
}

interface RagChatBoxProps {
  sessionId: string | null;
  stepIndex: number;
}

export default function RagChatBox({ sessionId, stepIndex }: RagChatBoxProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'system',
      content: 'Chào bạn! Tôi là AI Tutor. Nhấn "Giải thích bước hiện tại" để tôi phân tích thuật toán cho bạn.',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamText, setCurrentStreamText] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastStepIndexRef = useRef<number>(-1);

  // Auto-scroll khi có tin nhắn mới
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentStreamText]);

  // Cleanup EventSource khi unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  // Debounce: khi stepIndex thay đổi, chờ 500ms rồi mới gọi API
  useEffect(() => {
    if (!sessionId || stepIndex < 0) return;

    // Nếu stepIndex giống lần trước, bỏ qua
    if (stepIndex === lastStepIndexRef.current) return;
    lastStepIndexRef.current = stepIndex;

    // Clear timer cũ
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Set timer mới
    debounceTimerRef.current = setTimeout(() => {
      fetchExplanation(stepIndex);
    }, 500);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, stepIndex]);

  const fetchExplanation = useCallback(
    (step: number, question?: string) => {
      if (!sessionId) return;

      // Close previous connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      setIsStreaming(true);
      setCurrentStreamText('');

      const url = getRagExplanationStreamUrl(sessionId, step, question);
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // Add user message if there's a question
      if (question) {
        setMessages((prev) => [...prev, { role: 'user', content: question }]);
      }

      let fullText = '';

      eventSource.addEventListener('meta', (event) => {
        // Metadata received, can parse if needed
        console.log('SSE meta:', event.data);
      });

      eventSource.addEventListener('chunk', (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.text) {
            fullText += data.text;
            setCurrentStreamText(fullText);
          }
        } catch {
          // Ignore parse errors
        }
      });

      eventSource.addEventListener('done', () => {
        eventSource.close();
        eventSourceRef.current = null;
        setIsStreaming(false);

        if (fullText) {
          setMessages((prev) => [...prev, { role: 'ai', content: fullText }]);
        }
        setCurrentStreamText('');
      });

      eventSource.onerror = () => {
        eventSource.close();
        eventSourceRef.current = null;
        setIsStreaming(false);

        // Fallback message nếu stream lỗi
        if (!fullText) {
          setMessages((prev) => [
            ...prev,
            {
              role: 'ai',
              content:
                'Xin lỗi, tôi không thể kết nối đến dịch vụ giải thích. Vui lòng thử lại sau.',
            },
          ]);
        }
        setCurrentStreamText('');
      };
    },
    [sessionId]
  );

  const handleExplainStep = () => {
    if (!sessionId || isStreaming) return;
    lastStepIndexRef.current = stepIndex;
    fetchExplanation(stepIndex);
  };

  const handleSendQuestion = () => {
    if (!inputValue.trim() || !sessionId || isStreaming) return;

    const question = inputValue.trim();
    setInputValue('');
    lastStepIndexRef.current = stepIndex;
    fetchExplanation(stepIndex, question);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendQuestion();
    }
  };

  return (
    <div className="flex-1 bg-slate-800 rounded-xl border border-slate-700 flex flex-col overflow-hidden shadow-2xl">
      {/* Header */}
      <div className="p-4 border-b border-slate-700 bg-slate-800/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isStreaming ? 'bg-green-500 animate-pulse' : 'bg-pink-500'}`}></div>
          <span className="text-sm font-bold tracking-tight uppercase">AI Tutor</span>
          {isStreaming && (
            <span className="text-[10px] text-green-400 ml-2">đang trả lời...</span>
          )}
        </div>
        <span className="text-[10px] text-slate-500 font-mono">
          Bước {stepIndex >= 0 ? stepIndex : '-'}
        </span>
      </div>

      {/* Messages area */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4 scrollbar-thin scrollbar-thumb-slate-700">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[90%] p-3 rounded-2xl text-xs leading-relaxed shadow-sm ${
                msg.role === 'user'
                  ? 'bg-pink-600 text-white rounded-tr-none'
                  : msg.role === 'system'
                  ? 'bg-slate-700/30 border border-slate-600 text-slate-400 italic rounded-tl-none'
                  : 'bg-slate-700/50 border border-slate-600 text-slate-200 rounded-tl-none'
              }`}
            >
              {msg.role === 'ai' ? (
                <div className="prose prose-invert prose-xs max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                </div>
              ) : (
                msg.content
              )}
            </div>
          </div>
        ))}

        {/* Streaming text */}
        {isStreaming && currentStreamText && (
          <div className="flex justify-start">
            <div className="max-w-[90%] p-3 rounded-2xl text-xs leading-relaxed shadow-sm bg-slate-700/50 border border-slate-600 text-slate-200 rounded-tl-none">
              <div className="prose prose-invert prose-xs max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {currentStreamText}
                </ReactMarkdown>
              </div>
              <span className="inline-block w-2 h-4 bg-pink-500 ml-1 animate-pulse" />
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Footer */}
      <div className="p-4 bg-slate-900/50 border-t border-slate-700 space-y-3">
        {/* Explain button */}
        <button
          onClick={handleExplainStep}
          disabled={!sessionId || isStreaming}
          className="w-full py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-[10px] font-bold text-pink-400 flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isStreaming ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <Sparkles size={14} />
          )}
          {isStreaming ? 'ĐANG GIẢI THÍCH...' : 'GIẢI THÍCH BƯỚC HIỆN TẠI'}
        </button>

        {/* Input */}
        <div className="relative">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhập câu hỏi..."
            disabled={!sessionId || isStreaming}
            className="w-full bg-slate-800 border border-slate-600 rounded-full px-4 py-2 text-xs outline-none focus:border-pink-500 transition-colors pr-10 disabled:opacity-50"
          />
          <button
            onClick={handleSendQuestion}
            disabled={!inputValue.trim() || !sessionId || isStreaming}
            className="absolute right-3 top-2 text-slate-500 hover:text-pink-400 transition-colors disabled:opacity-50"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}