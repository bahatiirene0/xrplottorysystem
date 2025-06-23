
import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Users, MessageCircle, Crown, Gift } from 'lucide-react';

interface ChatMessage {
  id: string;
  user: string;
  message: string;
  timestamp: number;
  type: 'message' | 'win' | 'system' | 'draw';
  amount?: number;
  isVip?: boolean;
}

interface LiveChatProps {
  isVisible: boolean;
  onToggle: () => void;
}

export const LiveChat: React.FC<LiveChatProps> = ({ isVisible, onToggle }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [onlineUsers] = useState(1247);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Mock initial messages
  useEffect(() => {
    const initialMessages: ChatMessage[] = [
      {
        id: '1',
        user: 'LottoBot',
        message: 'Welcome to XRP Lotto Live Chat! Next draw in 2:45',
        timestamp: Date.now() - 300000,
        type: 'system'
      },
      {
        id: '2',
        user: 'CryptoKing',
        message: 'Just bought 5 tickets for the next draw! 🎲',
        timestamp: Date.now() - 240000,
        type: 'message',
        isVip: true
      },
      {
        id: '3',
        user: 'LuckyPlayer',
        message: 'Won 250 XRP! 🎉',
        timestamp: Date.now() - 180000,
        type: 'win',
        amount: 250
      },
      {
        id: '4',
        user: 'XRPFan',
        message: 'Good luck everyone! May the best numbers win',
        timestamp: Date.now() - 120000,
        type: 'message'
      },
      {
        id: '5',
        user: 'DrawBot',
        message: 'Draw #12847 completed! Winner: wallet_789 (1,250 XRP)',
        timestamp: Date.now() - 60000,
        type: 'draw',
        amount: 1250
      }
    ];
    setMessages(initialMessages);
  }, []);

  // Auto scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = () => {
    if (newMessage.trim()) {
      const message: ChatMessage = {
        id: Date.now().toString(),
        user: 'You',
        message: newMessage,
        timestamp: Date.now(),
        type: 'message'
      };
      setMessages(prev => [...prev, message]);
      setNewMessage('');

      // Simulate responses
      setTimeout(() => {
        const responses = [
          'Nice pick! Good luck! 🍀',
          'May your numbers be lucky! 🎲',
          'Welcome to the community! 🎉',
          'Great choice! The odds are in your favor! ⭐',
          'Let\'s go! Big win incoming! 💰'
        ];
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        const botMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          user: 'Player' + Math.floor(Math.random() * 1000),
          message: randomResponse,
          timestamp: Date.now(),
          type: 'message'
        };
        setMessages(prev => [...prev, botMessage]);
      }, 1000 + Math.random() * 2000);
    }
  };

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'win': return <Gift className="h-3 w-3 text-yellow-400" />;
      case 'system': return <MessageCircle className="h-3 w-3 text-blue-400" />;
      case 'draw': return <Crown className="h-3 w-3 text-purple-400" />;
      default: return null;
    }
  };

  if (!isVisible) {
    return (
      <Button
        onClick={onToggle}
        className="fixed bottom-4 right-4 rounded-full w-14 h-14 bg-blue-600 hover:bg-blue-700 z-40"
      >
        <MessageCircle className="h-6 w-6" />
      </Button>
    );
  }

  return (
    <Card className="fixed bottom-4 right-4 w-80 h-96 bg-gray-800/95 border-gray-600 z-40 flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-white text-sm flex items-center gap-2">
            <MessageCircle className="h-4 w-4" />
            Live Chat
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-green-400 border-green-400 text-xs">
              <Users className="h-3 w-3 mr-1" />
              {onlineUsers.toLocaleString()}
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggle}
              className="h-6 w-6 p-0 text-gray-400 hover:text-white"
            >
              ×
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col p-3 pt-0">
        <ScrollArea className="flex-1 pr-3">
          <div className="space-y-2">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`p-2 rounded text-xs ${
                  msg.type === 'system' 
                    ? 'bg-blue-500/20 border border-blue-500/30' 
                    : msg.type === 'win'
                    ? 'bg-yellow-500/20 border border-yellow-500/30'
                    : msg.type === 'draw'
                    ? 'bg-purple-500/20 border border-purple-500/30'
                    : msg.user === 'You'
                    ? 'bg-green-500/20 border border-green-500/30 ml-4'
                    : 'bg-gray-700/50'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-1">
                    {getMessageIcon(msg.type)}
                    <span className={`font-medium ${
                      msg.isVip ? 'text-yellow-400' : 'text-blue-400'
                    }`}>
                      {msg.user}
                      {msg.isVip && <Crown className="h-3 w-3 inline ml-1" />}
                    </span>
                  </div>
                  <span className="text-gray-500 text-xs">
                    {formatTime(msg.timestamp)}
                  </span>
                </div>
                <p className="text-gray-200">
                  {msg.message}
                  {msg.amount && (
                    <span className="text-green-400 font-bold ml-1">
                      {msg.amount} XRP
                    </span>
                  )}
                </p>
              </div>
            ))}
            <div ref={scrollRef} />
          </div>
        </ScrollArea>
        
        <div className="flex gap-2 mt-3">
          <Input
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 bg-gray-700 border-gray-600 text-white text-xs"
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            maxLength={100}
          />
          <Button
            onClick={handleSendMessage}
            size="sm"
            className="px-3"
            disabled={!newMessage.trim()}
          >
            <Send className="h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
