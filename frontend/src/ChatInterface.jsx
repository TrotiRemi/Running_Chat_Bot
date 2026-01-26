import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './ChatInterface.css';

function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Bonjour! Je suis votre assistant de plans d'entraînement. Comment puis-je vous aider?",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;

    // Ajouter le message utilisateur
    const userMessage = {
      id: messages.length + 1,
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError('');

    try {
      // Envoyer au backend
      const apiUrl = 'http://localhost:5000';
      const response = await axios.post(`${apiUrl}/api/chat`, {
        message: userMessage.text
      });

      // Ajouter la réponse du bot
      const botMessage = {
        id: messages.length + 2,
        text: response.data.bot_response,
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur de connexion au serveur');
      console.error('Erreur:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('fr-FR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>🏃 Running Plan Assistant</h1>
        <p>Votre assistant pour les plans d'entraînement</p>
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.sender}`}
          >
            <div className="message-content">
              <p>{message.text}</p>
              <span className="message-time">{formatTime(message.timestamp)}</span>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message bot">
            <div className="message-content loading">
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
            <p>⚠️ {error}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={sendMessage}>
        <div className="input-container">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Écrivez votre question..."
            disabled={isLoading}
            className="chat-input"
          />
          <button 
            type="submit" 
            disabled={isLoading || !inputValue.trim()}
            className="send-button"
          >
            {isLoading ? '⏳' : '➤'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatInterface;
