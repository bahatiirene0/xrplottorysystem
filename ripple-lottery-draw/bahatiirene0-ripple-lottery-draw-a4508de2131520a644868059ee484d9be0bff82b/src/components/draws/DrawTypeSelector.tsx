
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Timer, Clock, Calendar, Crown } from "lucide-react";

interface DrawType {
  id: string;
  name: string;
  interval: string;
  nextDraw: string;
  participants: number;
  prizePool: number;
  icon: any;
  color: string;
  isActive: boolean;
}

interface DrawTypeSelectorProps {
  onSelectDraw: (drawType: DrawType) => void;
  selectedDraw: string;
}

export const DrawTypeSelector = ({ onSelectDraw, selectedDraw }: DrawTypeSelectorProps) => {
  const drawTypes: DrawType[] = [
    {
      id: 'quick',
      name: 'Quick Draw',
      interval: 'Every 3 minutes',
      nextDraw: '2:45',
      participants: 25,
      prizePool: 150,
      icon: Timer,
      color: 'from-green-400 to-blue-500',
      isActive: true
    },
    {
      id: 'hourly',
      name: 'Hourly Draw',
      interval: 'Every hour',
      nextDraw: '42:15',
      participants: 150,
      prizePool: 2500,
      icon: Clock,
      color: 'from-orange-400 to-red-500',
      isActive: true
    },
    {
      id: 'daily',
      name: 'Daily Jackpot',
      interval: 'Every 24 hours',
      nextDraw: '18:24:30',
      participants: 850,
      prizePool: 50000,
      icon: Calendar,
      color: 'from-purple-400 to-pink-500',
      isActive: true
    },
    {
      id: 'mega',
      name: 'Mega Jackpot',
      interval: 'Weekly',
      nextDraw: '5d 12:30:45',
      participants: 2400,
      prizePool: 500000,
      icon: Crown,
      color: 'from-yellow-400 to-orange-500',
      isActive: false
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {drawTypes.map((draw) => {
        const IconComponent = draw.icon;
        const isSelected = selectedDraw === draw.id;
        
        return (
          <Card 
            key={draw.id} 
            className={`cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-xl ${
              isSelected 
                ? 'bg-gradient-to-br from-gray-700/80 to-gray-800/80 border-blue-400 shadow-lg shadow-blue-400/20' 
                : 'bg-gray-800/50 border-gray-700 hover:border-gray-600'
            } ${!draw.isActive ? 'opacity-50 cursor-not-allowed' : ''}`}
            onClick={() => draw.isActive && onSelectDraw(draw)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className={`p-2 rounded-lg bg-gradient-to-r ${draw.color} bg-opacity-20`}>
                  <IconComponent className={`h-5 w-5 bg-gradient-to-r ${draw.color} bg-clip-text`} />
                </div>
                {!draw.isActive && (
                  <Badge variant="secondary" className="text-xs">
                    Coming Soon
                  </Badge>
                )}
              </div>
              <CardTitle className="text-lg text-white">{draw.name}</CardTitle>
              <p className="text-sm text-gray-400">{draw.interval}</p>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Next Draw</span>
                <span className="text-sm font-mono text-blue-400">{draw.nextDraw}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Participants</span>
                <span className="text-sm text-green-400">{draw.participants}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Prize Pool</span>
                <span className="text-sm font-semibold text-purple-400">{draw.prizePool.toLocaleString()} XRP</span>
              </div>
              {isSelected && (
                <div className="pt-2 border-t border-gray-600">
                  <Badge className="bg-blue-500/20 text-blue-400 text-xs">
                    Active
                  </Badge>
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};
