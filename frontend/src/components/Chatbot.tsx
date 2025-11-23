import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Loader2 } from 'lucide-react';
import api from '../services/api';

interface Message {
    text: string;
    isUser: boolean;
}

const Chatbot: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        { text: "Hello! I'm your AI assistant. I can help you with petition submission, status tracking, and general questions. How can I help you today?", isUser: false },
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput('');
        setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
        setIsLoading(true);

        try {
            // Build conversation history (last 5 messages)
            const conversationHistory = messages.slice(-5).map(msg => ({
                role: msg.isUser ? 'user' : 'assistant',
                content: msg.text
            }));

            const response = await api.post('/ai/chat/', {
                message: userMessage,
                conversation_history: conversationHistory,
                timestamp: new Date().toISOString()
            });

            setMessages(prev => [...prev, {
                text: response.data.response,
                isUser: false
            }]);
        } catch (error) {
            console.error('Chatbot error:', error);
            setMessages(prev => [...prev, {
                text: "I'm sorry, I encountered an error. Please try again or contact support if the issue persists.",
                isUser: false
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleQuickAction = async (action: string) => {
        const quickMessages: Record<string, string> = {
            'submit': 'How do I submit a petition?',
            'status': 'What do the petition statuses mean?',
            'urgency': 'How is urgency determined?',
            'departments': 'What departments are available?'
        };

        const message = quickMessages[action];
        if (message) {
            setInput(message);
            // Trigger send after a short delay to show the message in input
            setTimeout(() => {
                handleSend();
            }, 100);
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-50">
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="bg-indigo-600 text-white p-4 rounded-full shadow-lg hover:bg-indigo-700 transition-all hover:scale-110"
                    aria-label="Open chat"
                >
                    <MessageCircle className="w-6 h-6" />
                </button>
            )}

            {isOpen && (
                <div className="bg-white rounded-lg shadow-2xl w-96 h-[500px] flex flex-col border border-gray-200">
                    <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white p-4 rounded-t-lg flex justify-between items-center">
                        <div>
                            <h3 className="font-semibold">AI Assistant</h3>
                            <p className="text-xs text-indigo-100">Powered by Google Gemini</p>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="text-white hover:text-gray-200 transition-colors"
                            aria-label="Close chat"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Quick Actions */}
                    {messages.length === 1 && (
                        <div className="p-3 bg-gray-50 border-b border-gray-200">
                            <p className="text-xs text-gray-600 mb-2">Quick help:</p>
                            <div className="flex flex-wrap gap-2">
                                <button
                                    onClick={() => handleQuickAction('submit')}
                                    className="text-xs bg-white border border-gray-300 rounded-full px-3 py-1 hover:bg-indigo-50 hover:border-indigo-300 transition-colors"
                                >
                                    How to submit
                                </button>
                                <button
                                    onClick={() => handleQuickAction('status')}
                                    className="text-xs bg-white border border-gray-300 rounded-full px-3 py-1 hover:bg-indigo-50 hover:border-indigo-300 transition-colors"
                                >
                                    Status meanings
                                </button>
                                <button
                                    onClick={() => handleQuickAction('departments')}
                                    className="text-xs bg-white border border-gray-300 rounded-full px-3 py-1 hover:bg-indigo-50 hover:border-indigo-300 transition-colors"
                                >
                                    Departments
                                </button>
                            </div>
                        </div>
                    )}

                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[85%] rounded-lg p-3 text-sm whitespace-pre-wrap ${msg.isUser
                                            ? 'bg-indigo-600 text-white rounded-br-none shadow-md'
                                            : 'bg-gray-100 text-gray-800 rounded-bl-none shadow-sm'
                                        }`}
                                >
                                    {msg.text}
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-gray-100 rounded-lg p-3 text-sm shadow-sm">
                                    <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <div className="p-4 border-t border-gray-200 bg-gray-50">
                        <div className="flex space-x-2">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                                placeholder="Type your message..."
                                disabled={isLoading}
                                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                            />
                            <button
                                onClick={handleSend}
                                disabled={isLoading || !input.trim()}
                                className="bg-indigo-600 text-white p-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                aria-label="Send message"
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        </div>
                        <p className="text-xs text-gray-500 mt-2 text-center">
                            AI responses may not always be accurate
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Chatbot;
