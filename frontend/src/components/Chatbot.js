import React, { useState } from 'react';
import axios from 'axios';
import './Chatbot.css';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (input.trim().toLowerCase() === 'exit') {
      setMessages([...messages, { sender: 'user', text: input }, { sender: 'bot', text: 'Thank you!' }]);
      setInput('');
      return;
    }

    const newMessages = [...messages, { sender: 'user', text: input }];
    setMessages(newMessages);

    try {
      const response = await axios.post('http://localhost:5000/ask', { query: input });
      const botResponse = response.data.response;
      setMessages([...newMessages, { sender: 'bot', text: botResponse }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages([...newMessages, { sender: 'bot', text: 'Sorry, something went wrong. Please try again.' }]);
    }

    setInput('');
  };

  return (
    <div className="chatbot">
      <div className="chatbot-header">RAG PDF </div>
      <div className="chatbot-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            <div className="message-bubble">
              {message.text}
            </div>
          </div>
        ))}
      </div>
      <div className="chatbot-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type a message..."
        />
        <button onClick={handleSend}>
            Send
        </button>
      </div>
    </div>
  );
};

export default Chatbot;
