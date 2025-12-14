import React, { useState, useRef, useEffect } from 'react';
import { usePersonalization } from '../../context/PersonalizationContext';

const Chatbot = ({ currentChapter }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const { preferences } = usePersonalization();

  // Load conversation history when component mounts
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const response = await fetch('/api/ai/history', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });

        if (response.ok) {
          const historyData = await response.json();
          setHistory(historyData);
        }
      } catch (error) {
        console.error('Error loading chat history:', error);
      }
    };

    loadHistory();
  }, []);

  // Function to scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message to the chat
    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Prepare context from the current chapter
      const context = currentChapter ? {
        chapter_title: currentChapter.title,
        chapter_content: currentChapter.content?.substring(0, 1000), // Limit content size
        module_title: currentChapter.module_title
      } : null;

      // Call the backend API to get the chatbot response
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          question: inputValue,
          chapter_id: currentChapter?.id || null,
          context: context
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add bot response to the chat
      const botMessage = {
        id: Date.now() + 1,
        text: data.answer,
        sender: 'bot',
        timestamp: new Date(),
        references: data.references,
        confidence: data.confidence
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error getting chat response:', error);

      // Add error message to the chat
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }
  };

  const formatConfidence = (confidence) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <h3>AI Learning Assistant</h3>
        <p>Ask questions about {currentChapter?.title || 'the textbook content'}</p>
      </div>
      
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <p>Hello! I'm your AI learning assistant. Ask me questions about the textbook content and I'll do my best to help.</p>
          </div>
        ) : (
          messages.map((message) => (
            <div 
              key={message.id} 
              className={`message ${message.sender}-message ${preferences.theme || 'light'}-theme`}
            >
              <div className="message-content">
                <p>{message.text}</p>
                {message.references && message.references.length > 0 && (
                  <div className="references">
                    <p><strong>References:</strong></p>
                    <ul>
                      {message.references.slice(0, 3).map((ref, idx) => (
                        <li key={idx}>{ref.title}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {message.confidence && (
                  <div className="confidence">
                    <small>Confidence: {formatConfidence(message.confidence)} ({(message.confidence * 100).toFixed(0)}%)</small>
                  </div>
                )}
              </div>
              <div className="message-timestamp">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message bot-message">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask a question about the content..."
          disabled={isLoading}
          aria-label="Type your message"
        />
        <button 
          type="submit" 
          disabled={!inputValue.trim() || isLoading}
          aria-label="Send message"
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default Chatbot;