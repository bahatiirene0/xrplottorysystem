
import React, { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

interface JackpotMeterProps {
  currentAmount: number;
  targetAmount: number;
  drawType: string;
  nextDrawTime: number;
}

export const JackpotMeter: React.FC<JackpotMeterProps> = ({
  currentAmount,
  targetAmount,
  drawType,
  nextDrawTime
}) => {
  const [displayAmount, setDisplayAmount] = useState(currentAmount);
  const [isGrowing, setIsGrowing] = useState(false);

  useEffect(() => {
    if (currentAmount !== displayAmount) {
      setIsGrowing(true);
      const timer = setTimeout(() => {
        setDisplayAmount(currentAmount);
        setIsGrowing(false);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [currentAmount, displayAmount]);

  const progressPercentage = (currentAmount / targetAmount) * 100;
  
  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card className="bg-gradient-to-br from-purple-900/50 via-blue-900/50 to-purple-900/50 border-purple-500/30 overflow-hidden">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-purple-400" />
            <h3 className="text-lg font-semibold text-white">{drawType} Jackpot</h3>
          </div>
          <Badge variant="outline" className="text-green-400 border-green-400">
            <Zap className="h-3 w-3 mr-1" />
            LIVE
          </Badge>
        </div>

        <div className="space-y-4">
          <div className="text-center">
            <motion.div
              animate={isGrowing ? { scale: [1, 1.1, 1], color: ['#ffffff', '#ffd700', '#ffffff'] } : {}}
              transition={{ duration: 0.5 }}
              className="text-3xl md:text-4xl font-bold text-white mb-2"
            >
              {displayAmount.toLocaleString()} XRP
            </motion.div>
            <p className="text-purple-300 text-sm">
              Next draw in {formatTime(nextDrawTime)}
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm text-purple-300">
              <span>Progress to Mega Jackpot</span>
              <span>{progressPercentage.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-purple-900/50 rounded-full h-3 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progressPercentage}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                className="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-yellow-500 rounded-full relative"
              >
                <div className="absolute inset-0 bg-white/20 animate-pulse rounded-full" />
              </motion.div>
            </div>
            <div className="text-center text-xs text-purple-400">
              Mega Jackpot at {targetAmount.toLocaleString()} XRP
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
