
import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Bell, X, Trophy, Clock, Users, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Notification {
  id: string;
  type: 'win' | 'draw' | 'jackpot' | 'reminder' | 'social';
  title: string;
  message: string;
  timestamp: number;
  isRead: boolean;
  actionUrl?: string;
  amount?: number;
}

interface NotificationCenterProps {
  isVisible: boolean;
  onToggle: () => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({
  isVisible,
  onToggle
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    // Mock notifications
    const mockNotifications: Notification[] = [
      {
        id: '1',
        type: 'win',
        title: 'Congratulations! 🎉',
        message: 'You won 150 XRP in the Quick Pick draw!',
        timestamp: Date.now() - 300000,
        isRead: false,
        amount: 150
      },
      {
        id: '2',
        type: 'draw',
        title: 'Draw Starting Soon',
        message: 'Mega Draw starts in 5 minutes. Get your tickets now!',
        timestamp: Date.now() - 180000,
        isRead: false
      },
      {
        id: '3',
        type: 'jackpot',
        title: 'Jackpot Alert! 💰',
        message: 'Mega Draw jackpot reached 50,000 XRP!',
        timestamp: Date.now() - 120000,
        isRead: true
      },
      {
        id: '4',
        type: 'social',
        title: 'Friend Joined',
        message: 'CryptoFriend joined your syndicate group',
        timestamp: Date.now() - 60000,
        isRead: false
      },
      {
        id: '5',
        type: 'reminder',
        title: 'Don\'t Miss Out!',
        message: 'You haven\'t played in 2 days. New draws available!',
        timestamp: Date.now() - 30000,
        isRead: false
      }
    ];

    setNotifications(mockNotifications);
    setUnreadCount(mockNotifications.filter(n => !n.isRead).length);

    // Simulate new notifications
    const interval = setInterval(() => {
      const newNotification: Notification = {
        id: Date.now().toString(),
        type: Math.random() > 0.5 ? 'draw' : 'jackpot',
        title: Math.random() > 0.5 ? 'New Draw Available!' : 'Jackpot Growing!',
        message: Math.random() > 0.5 
          ? 'Quick Pick draw starting in 3 minutes'
          : 'Current jackpot: ' + Math.floor(Math.random() * 10000 + 5000) + ' XRP',
        timestamp: Date.now(),
        isRead: false
      };

      setNotifications(prev => [newNotification, ...prev.slice(0, 9)]);
      setUnreadCount(prev => prev + 1);
    }, 30000); // New notification every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, isRead: true } : n)
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
    setUnreadCount(0);
  };

  const deleteNotification = (id: string) => {
    const notification = notifications.find(n => n.id === id);
    setNotifications(prev => prev.filter(n => n.id !== id));
    if (notification && !notification.isRead) {
      setUnreadCount(prev => Math.max(0, prev - 1));
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'win': return <Trophy className="h-4 w-4 text-yellow-400" />;
      case 'draw': return <Clock className="h-4 w-4 text-blue-400" />;
      case 'jackpot': return <Zap className="h-4 w-4 text-purple-400" />;
      case 'social': return <Users className="h-4 w-4 text-green-400" />;
      case 'reminder': return <Bell className="h-4 w-4 text-orange-400" />;
      default: return <Bell className="h-4 w-4 text-gray-400" />;
    }
  };

  const formatTime = (timestamp: number) => {
    const diff = Date.now() - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  if (!isVisible) {
    return (
      <Button
        onClick={onToggle}
        variant="ghost"
        size="sm"
        className="relative rounded-full w-10 h-10 p-0"
      >
        <Bell className="h-4 w-4" />
        {unreadCount > 0 && (
          <Badge 
            variant="destructive" 
            className="absolute -top-1 -right-1 h-5 w-5 text-xs p-0 flex items-center justify-center"
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </Badge>
        )}
      </Button>
    );
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="absolute top-full right-0 mt-2 w-80 z-50"
      >
        <Card className="bg-gray-800/95 border-gray-600 backdrop-blur-sm">
          <CardContent className="p-0">
            <div className="p-4 border-b border-gray-600">
              <div className="flex items-center justify-between">
                <h3 className="text-white font-medium">Notifications</h3>
                <div className="flex items-center gap-2">
                  {unreadCount > 0 && (
                    <Button
                      onClick={markAllAsRead}
                      variant="ghost"
                      size="sm"
                      className="text-xs text-blue-400 hover:text-blue-300"
                    >
                      Mark all read
                    </Button>
                  )}
                  <Button
                    onClick={onToggle}
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0 text-gray-400 hover:text-white"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>

            <div className="max-h-80 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-4 text-center text-gray-400">
                  <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No notifications yet</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {notifications.map((notification) => (
                    <motion.div
                      key={notification.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      className={`p-3 hover:bg-gray-700/50 cursor-pointer transition-colors ${
                        !notification.isRead ? 'bg-blue-500/10 border-l-2 border-l-blue-500' : ''
                      }`}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 mt-0.5">
                          {getNotificationIcon(notification.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <p className="text-white text-sm font-medium truncate">
                              {notification.title}
                            </p>
                            <Button
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteNotification(notification.id);
                              }}
                              variant="ghost"
                              size="sm"
                              className="h-4 w-4 p-0 text-gray-500 hover:text-red-400"
                            >
                              <X className="h-3 w-3" />
                            </Button>
                          </div>
                          <p className="text-gray-300 text-xs mb-1">
                            {notification.message}
                            {notification.amount && (
                              <span className="text-green-400 font-bold ml-1">
                                {notification.amount} XRP
                              </span>
                            )}
                          </p>
                          <p className="text-gray-500 text-xs">
                            {formatTime(notification.timestamp)}
                          </p>
                        </div>
                        {!notification.isRead && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-2" />
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </AnimatePresence>
  );
};
