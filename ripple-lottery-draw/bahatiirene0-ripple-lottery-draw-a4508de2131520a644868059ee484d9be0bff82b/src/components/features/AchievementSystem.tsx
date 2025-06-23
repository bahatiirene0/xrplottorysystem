
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Trophy, Star, Target, Zap, Crown, Gift, Lock } from 'lucide-react';
import { motion } from 'framer-motion';

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<any>;
  category: 'wins' | 'participation' | 'social' | 'special';
  progress: number;
  maxProgress: number;
  unlocked: boolean;
  unlockedAt?: number;
  reward: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

interface AchievementSystemProps {
  playerStats: {
    totalWins: number;
    totalTickets: number;
    currentStreak: number;
    longestStreak: number;
    totalSpent: number;
    referrals: number;
  };
}

export const AchievementSystem: React.FC<AchievementSystemProps> = ({ playerStats }) => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [recentUnlock, setRecentUnlock] = useState<Achievement | null>(null);

  useEffect(() => {
    const allAchievements: Achievement[] = [
      {
        id: 'first_ticket',
        name: 'First Steps',
        description: 'Purchase your first lottery ticket',
        icon: Zap,
        category: 'participation',
        progress: Math.min(playerStats.totalTickets, 1),
        maxProgress: 1,
        unlocked: playerStats.totalTickets >= 1,
        reward: '5 XRP Bonus',
        rarity: 'common'
      },
      {
        id: 'first_win',
        name: 'Lucky Beginner',
        description: 'Win your first prize',
        icon: Trophy,
        category: 'wins',
        progress: Math.min(playerStats.totalWins, 1),
        maxProgress: 1,
        unlocked: playerStats.totalWins >= 1,
        reward: '10 XRP Bonus',
        rarity: 'common'
      },
      {
        id: 'ticket_collector',
        name: 'Ticket Collector',
        description: 'Purchase 100 lottery tickets',
        icon: Target,
        category: 'participation',
        progress: Math.min(playerStats.totalTickets, 100),
        maxProgress: 100,
        unlocked: playerStats.totalTickets >= 100,
        reward: '50 XRP Bonus',
        rarity: 'rare'
      },
      {
        id: 'win_streak_5',
        name: 'Hot Streak',
        description: 'Win 5 draws in a row',
        icon: Star,
        category: 'wins',
        progress: Math.min(playerStats.currentStreak, 5),
        maxProgress: 5,
        unlocked: playerStats.longestStreak >= 5,
        reward: '25 XRP Bonus',
        rarity: 'rare'
      },
      {
        id: 'high_roller',
        name: 'High Roller',
        description: 'Spend 1000 XRP on tickets',
        icon: Crown,
        category: 'participation',
        progress: Math.min(playerStats.totalSpent, 1000),
        maxProgress: 1000,
        unlocked: playerStats.totalSpent >= 1000,
        reward: '100 XRP Bonus + VIP Status',
        rarity: 'epic'
      },
      {
        id: 'social_butterfly',
        name: 'Social Butterfly',
        description: 'Refer 10 friends to the platform',
        icon: Gift,
        category: 'social',
        progress: Math.min(playerStats.referrals, 10),
        maxProgress: 10,
        unlocked: playerStats.referrals >= 10,
        reward: '200 XRP Bonus',
        rarity: 'epic'
      },
      {
        id: 'legend',
        name: 'Lottery Legend',
        description: 'Win 50 draws total',
        icon: Crown,
        category: 'wins',
        progress: Math.min(playerStats.totalWins, 50),
        maxProgress: 50,
        unlocked: playerStats.totalWins >= 50,
        reward: '500 XRP + Legendary Badge',
        rarity: 'legendary'
      }
    ];

    // Check for new unlocks
    const previousAchievements = achievements;
    const newUnlocks = allAchievements.filter(
      achievement => achievement.unlocked && 
      !previousAchievements.find(prev => prev.id === achievement.id && prev.unlocked)
    );

    if (newUnlocks.length > 0 && previousAchievements.length > 0) {
      setRecentUnlock(newUnlocks[0]);
      setTimeout(() => setRecentUnlock(null), 5000);
    }

    setAchievements(allAchievements);
  }, [playerStats, achievements]);

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'text-gray-400 border-gray-400';
      case 'rare': return 'text-blue-400 border-blue-400';
      case 'epic': return 'text-purple-400 border-purple-400';
      case 'legendary': return 'text-yellow-400 border-yellow-400';
      default: return 'text-gray-400 border-gray-400';
    }
  };

  const getRarityBg = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'bg-gray-500/10';
      case 'rare': return 'bg-blue-500/10';
      case 'epic': return 'bg-purple-500/10';
      case 'legendary': return 'bg-yellow-500/10';
      default: return 'bg-gray-500/10';
    }
  };

  const unlockedCount = achievements.filter(a => a.unlocked).length;
  const completionPercentage = (unlockedCount / achievements.length) * 100;

  return (
    <div className="space-y-6">
      {/* Achievement Unlock Notification */}
      {recentUnlock && (
        <motion.div
          initial={{ opacity: 0, y: -50, scale: 0.8 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.8 }}
          className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50"
        >
          <Card className="bg-gradient-to-r from-yellow-400/20 to-orange-500/20 border-yellow-400/50">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="text-yellow-400">
                  <recentUnlock.icon className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-white font-bold">Achievement Unlocked!</p>
                  <p className="text-yellow-300 text-sm">{recentUnlock.name}</p>
                  <p className="text-gray-300 text-xs">{recentUnlock.reward}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Achievement Overview */}
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Trophy className="h-5 w-5 text-yellow-400" />
            Achievements
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-300">Progress</span>
            <span className="text-white font-bold">{unlockedCount} / {achievements.length}</span>
          </div>
          <Progress value={completionPercentage} className="h-3" />
          <p className="text-gray-400 text-sm text-center">
            {completionPercentage.toFixed(1)}% Complete
          </p>
        </CardContent>
      </Card>

      {/* Achievement Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {achievements.map((achievement) => {
          const IconComponent = achievement.icon;
          const progressPercentage = (achievement.progress / achievement.maxProgress) * 100;
          
          return (
            <Card 
              key={achievement.id}
              className={`transition-all duration-300 hover:scale-105 ${
                achievement.unlocked 
                  ? `${getRarityBg(achievement.rarity)} border-2 ${getRarityColor(achievement.rarity).split(' ')[1]}`
                  : 'bg-gray-800/30 border-gray-600'
              }`}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${
                    achievement.unlocked 
                      ? getRarityBg(achievement.rarity)
                      : 'bg-gray-700/50'
                  }`}>
                    {achievement.unlocked ? (
                      <IconComponent className={`h-6 w-6 ${getRarityColor(achievement.rarity).split(' ')[0]}`} />
                    ) : (
                      <Lock className="h-6 w-6 text-gray-500" />
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className={`font-medium ${
                        achievement.unlocked ? 'text-white' : 'text-gray-400'
                      }`}>
                        {achievement.name}
                      </h4>
                      <Badge 
                        variant="outline" 
                        className={`text-xs ${getRarityColor(achievement.rarity)}`}
                      >
                        {achievement.rarity.toUpperCase()}
                      </Badge>
                    </div>
                    
                    <p className={`text-xs mb-2 ${
                      achievement.unlocked ? 'text-gray-300' : 'text-gray-500'
                    }`}>
                      {achievement.description}
                    </p>
                    
                    {!achievement.unlocked && (
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-400">Progress</span>
                          <span className="text-gray-300">
                            {achievement.progress} / {achievement.maxProgress}
                          </span>
                        </div>
                        <Progress value={progressPercentage} className="h-1" />
                      </div>
                    )}
                    
                    {achievement.unlocked && (
                      <div className="mt-2">
                        <Badge variant="secondary" className="text-xs">
                          {achievement.reward}
                        </Badge>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
