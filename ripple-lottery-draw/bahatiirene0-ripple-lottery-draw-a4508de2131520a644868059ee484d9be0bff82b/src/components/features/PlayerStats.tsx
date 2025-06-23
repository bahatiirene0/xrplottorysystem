
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Trophy, Target, TrendingUp, Award, Star, Calendar } from 'lucide-react';

interface PlayerStatsProps {
  stats: {
    level: number;
    xp: number;
    xpToNext: number;
    totalWins: number;
    winRate: number;
    favoriteNumbers: number[];
    currentStreak: number;
    longestStreak: number;
    totalTickets: number;
    achievements: string[];
  };
}

export const PlayerStats: React.FC<PlayerStatsProps> = ({ stats }) => {
  const xpProgress = (stats.xp / stats.xpToNext) * 100;

  const achievements = [
    { id: 'first_win', name: 'First Winner', icon: Trophy, unlocked: stats.totalWins > 0 },
    { id: 'lucky_seven', name: 'Lucky Seven', icon: Star, unlocked: stats.currentStreak >= 7 },
    { id: 'high_roller', name: 'High Roller', icon: Award, unlocked: stats.totalTickets >= 100 },
    { id: 'consistent', name: 'Consistent Player', icon: Calendar, unlocked: stats.longestStreak >= 14 }
  ];

  return (
    <div className="space-y-6">
      {/* Player Level Card */}
      <Card className="bg-gradient-to-br from-blue-900/50 to-purple-900/50 border-blue-500/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Award className="h-5 w-5 text-yellow-400" />
            Player Level {stats.level}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-blue-300">
              <span>Experience Points</span>
              <span>{stats.xp} / {stats.xpToNext}</span>
            </div>
            <Progress value={xpProgress} className="h-3" />
            <p className="text-xs text-blue-400 text-center">
              {stats.xpToNext - stats.xp} XP until level {stats.level + 1}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-gray-800/50 border-gray-700">
          <CardContent className="p-4 text-center">
            <Trophy className="h-6 w-6 text-yellow-400 mx-auto mb-2" />
            <div className="text-xl font-bold text-white">{stats.totalWins}</div>
            <div className="text-xs text-gray-400">Total Wins</div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800/50 border-gray-700">
          <CardContent className="p-4 text-center">
            <TrendingUp className="h-6 w-6 text-green-400 mx-auto mb-2" />
            <div className="text-xl font-bold text-white">{stats.winRate}%</div>
            <div className="text-xs text-gray-400">Win Rate</div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800/50 border-gray-700">
          <CardContent className="p-4 text-center">
            <Target className="h-6 w-6 text-orange-400 mx-auto mb-2" />
            <div className="text-xl font-bold text-white">{stats.currentStreak}</div>
            <div className="text-xs text-gray-400">Current Streak</div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800/50 border-gray-700">
          <CardContent className="p-4 text-center">
            <Star className="h-6 w-6 text-purple-400 mx-auto mb-2" />
            <div className="text-xl font-bold text-white">{stats.longestStreak}</div>
            <div className="text-xs text-gray-400">Best Streak</div>
          </CardContent>
        </Card>
      </div>

      {/* Achievements */}
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white">Achievements</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {achievements.map((achievement) => {
              const IconComponent = achievement.icon;
              return (
                <div
                  key={achievement.id}
                  className={`p-3 rounded-lg border text-center transition-all ${
                    achievement.unlocked 
                      ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400' 
                      : 'bg-gray-700/30 border-gray-600 text-gray-500'
                  }`}
                >
                  <IconComponent className={`h-6 w-6 mx-auto mb-1 ${
                    achievement.unlocked ? 'text-yellow-400' : 'text-gray-500'
                  }`} />
                  <div className="text-xs font-medium">{achievement.name}</div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Favorite Numbers */}
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white">Your Lucky Numbers</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {stats.favoriteNumbers.map((number, index) => (
              <Badge key={index} variant="outline" className="text-blue-400 border-blue-400">
                {number}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
