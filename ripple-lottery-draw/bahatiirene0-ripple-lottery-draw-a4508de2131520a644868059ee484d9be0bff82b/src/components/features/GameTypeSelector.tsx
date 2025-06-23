
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dice6, Zap, Users, Star, Clock, Trophy } from 'lucide-react';

interface GameType {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<any>;
  minTicketPrice: number;
  maxPrize: number;
  drawFrequency: string;
  playerCount: number;
  isActive: boolean;
  features: string[];
}

interface GameTypeSelectorProps {
  onSelectGame: (gameType: GameType) => void;
  selectedGame?: string;
}

export const GameTypeSelector: React.FC<GameTypeSelectorProps> = ({
  onSelectGame,
  selectedGame
}) => {
  const gameTypes: GameType[] = [
    {
      id: 'quick_pick',
      name: 'Quick Pick',
      description: 'Fast 3-minute draws with instant results',
      icon: Zap,
      minTicketPrice: 5,
      maxPrize: 1000,
      drawFrequency: 'Every 3 minutes',
      playerCount: 1247,
      isActive: true,
      features: ['Instant Draw', 'Auto Numbers', 'Quick Payout']
    },
    {
      id: 'mega_draw',
      name: 'Mega Draw',
      description: 'Huge jackpots with daily draws',
      icon: Trophy,
      minTicketPrice: 25,
      maxPrize: 50000,
      drawFrequency: 'Daily at 9 PM',
      playerCount: 892,
      isActive: true,
      features: ['Massive Jackpot', 'Choose Numbers', 'Rollover Prizes']
    },
    {
      id: 'instant_win',
      name: 'Instant Win',
      description: 'Scratch card style instant prizes',
      icon: Star,
      minTicketPrice: 10,
      maxPrize: 5000,
      drawFrequency: 'Immediate',
      playerCount: 634,
      isActive: true,
      features: ['Instant Result', 'Multiple Prizes', 'No Waiting']
    },
    {
      id: 'syndicate',
      name: 'Group Play',
      description: 'Pool tickets with other players',
      icon: Users,
      minTicketPrice: 5,
      maxPrize: 25000,
      drawFrequency: 'Weekly',
      playerCount: 2156,
      isActive: true,
      features: ['Shared Cost', 'Better Odds', 'Social Play']
    }
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-2">Choose Your Game</h2>
        <p className="text-gray-400">Select from our variety of lottery games</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {gameTypes.map((game) => {
          const IconComponent = game.icon;
          const isSelected = selectedGame === game.id;
          
          return (
            <Card 
              key={game.id}
              className={`cursor-pointer transition-all duration-300 hover:scale-105 ${
                isSelected 
                  ? 'border-blue-500 bg-blue-500/10' 
                  : 'border-gray-600 bg-gray-800/50 hover:border-gray-500'
              }`}
              onClick={() => onSelectGame(game)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <IconComponent className={`h-6 w-6 ${
                    isSelected ? 'text-blue-400' : 'text-gray-400'
                  }`} />
                  {game.isActive && (
                    <Badge variant="outline" className="text-green-400 border-green-400 text-xs">
                      LIVE
                    </Badge>
                  )}
                </div>
                <CardTitle className="text-white text-lg">{game.name}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-gray-400 text-sm">{game.description}</p>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Min Ticket:</span>
                    <span className="text-blue-400">{game.minTicketPrice} XRP</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Max Prize:</span>
                    <span className="text-green-400">{game.maxPrize.toLocaleString()} XRP</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Frequency:</span>
                    <span className="text-purple-400">{game.drawFrequency}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Players:</span>
                    <span className="text-orange-400">{game.playerCount.toLocaleString()}</span>
                  </div>
                </div>

                <div className="space-y-1">
                  <p className="text-gray-400 text-xs">Features:</p>
                  <div className="flex flex-wrap gap-1">
                    {game.features.map((feature, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {feature}
                      </Badge>
                    ))}
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
