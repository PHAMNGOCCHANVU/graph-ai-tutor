// src/components/RagChatBox.tsx
"use client";
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Sparkles, Loader2, X, MessageSquare } from 'lucide-react';
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
  description?: string; // Giải thích mặc định từ backend (không cần AI)
}

export default function RagChatBox({ sessionId, stepIndex, description }: RagChatBoxProps) {
  const [isOpen, setIsOpen] = useState(false);
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
    };
  }, []);

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
    if (!isOpen) setIsOpen(true);
    fetchExplanation(stepIndex);
  };

  const handleSendQuestion = () => {
    if (!inputValue.trim() || !sessionId || isStreaming) return;

    const question = inputValue.trim();
    setInputValue('');
    fetchExplanation(stepIndex, question);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendQuestion();
    }
  };

  // Nút chat nổi (khi đóng)
  if (!isOpen) {
    return (
      <>
        {/* Nút giải thích — góc trên phải canvas */}
        <button
          onClick={handleExplainStep}
          disabled={!sessionId || isStreaming}
          className="absolute top-4 right-4 z-50 flex items-center gap-2 bg-pink-600 hover:bg-pink-500 text-white px-4 py-2.5 rounded-full text-xs font-bold shadow-2xl transition-all active:scale-95 disabled:opacity-50"
        >
          <Sparkles size={16} />
          GIẢI THÍCH BƯỚC {stepIndex}
        </button>

        {/* Nút mở chat AI — góc dưới phải màn hình */}
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-pink-600 hover:bg-pink-500 rounded-full flex items-center justify-center shadow-2xl transition-all active:scale-90"
        >
          <MessageSquare size={24} className="text-white" />
        </button>
      </>
    );
  }

  return (
    <>
      {/* Nút giải thích — góc trên phải canvas (khi chat mở) */}
      <button
        onClick={handleExplainStep}
        disabled={!sessionId || isStreaming}
        className="absolute top-4 right-4 z-50 flex items-center gap-2 bg-pink-600 hover:bg-pink-500 text-white px-4 py-2.5 rounded-full text-xs font-bold shadow-2xl transition-all active:scale-95 disabled:opacity-50"
      >
        <Sparkles size={16} />
        GIẢI THÍCH BƯỚC {stepIndex}
      </button>

      {/* Khung chat floating */}
      <div className="fixed bottom-6 right-6 z-50 w-[380px] h-[520px] bg-slate-800 rounded-2xl border border-slate-700 flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-3 border-b border-slate-700 bg-slate-800/50 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isStreaming ? 'bg-green-500 animate-pulse' : 'bg-pink-500'}`}></div>
            <span className="text-sm font-bold tracking-tight uppercase">AI Tutor</span>
            {isStreaming && (
              <span className="text-[10px] text-green-400 ml-1">đang trả lời...</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-slate-500 font-mono">
              Bước {stepIndex >= 0 ? stepIndex : '-'}
            </span>
            <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-white transition-colors">
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Giải thích mặc định (không cần AI) */}
        {description && !isStreaming && messages.length <= 1 && (
          <div className="px-3 pt-3 shrink-0">
            <div className="bg-slate-700/40 border border-slate-600 rounded-xl p-3 text-xs text-slate-300 leading-relaxed">
              <div className="font-bold text-pink-400 mb-1 text-[10px] uppercase tracking-wider">Giải thích bước {stepIndex}</div>
              {description}
            </div>
          </div>
        )}

        {/* Messages area */}
        <div className="flex-1 p-3 overflow-y-auto space-y-3 scrollbar-thin scrollbar-thumb-slate-700 min-h-0">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[90%] p-2.5 rounded-2xl text-xs leading-relaxed shadow-sm ${
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
              <div className="max-w-[90%] p-2.5 rounded-2xl text-xs leading-relaxed shadow-sm bg-slate-700/50 border border-slate-600 text-slate-200 rounded-tl-none">
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
        <div className="p-3 bg-slate-900/50 border-t border-slate-700 shrink-0">
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
              className="absolute right-2.5 top-1.5 text-slate-500 hover:text-pink-400 transition-colors disabled:opacity-50"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </>
  );
}