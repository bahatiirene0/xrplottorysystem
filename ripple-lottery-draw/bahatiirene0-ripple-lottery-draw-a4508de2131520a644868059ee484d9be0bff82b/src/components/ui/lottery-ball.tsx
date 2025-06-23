
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface LotteryBallProps {
  number: number;
  isDrawing?: boolean;
  delay?: number;
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

export const LotteryBall: React.FC<LotteryBallProps> = ({
  number,
  isDrawing = false,
  delay = 0,
  size = 'md',
  color = 'blue'
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (isDrawing) {
      const timer = setTimeout(() => setIsVisible(true), delay);
      return () => clearTimeout(timer);
    }
  }, [isDrawing, delay]);

  const sizeClasses = {
    sm: 'w-12 h-12 text-sm',
    md: 'w-16 h-16 text-lg',
    lg: 'w-20 h-20 text-xl'
  };

  const colorClasses = {
    blue: 'bg-gradient-to-br from-blue-400 to-blue-600',
    green: 'bg-gradient-to-br from-green-400 to-green-600',
    purple: 'bg-gradient-to-br from-purple-400 to-purple-600',
    gold: 'bg-gradient-to-br from-yellow-400 to-yellow-600',
    red: 'bg-gradient-to-br from-red-400 to-red-600'
  };

  return (
    <motion.div
      initial={{ scale: 0, rotate: -180, opacity: 0 }}
      animate={isVisible ? { 
        scale: 1, 
        rotate: 0, 
        opacity: 1,
        y: [0, -20, 0]
      } : {}}
      transition={{ 
        duration: 0.8, 
        ease: "easeOut",
        y: { repeat: Infinity, duration: 2 }
      }}
      className={`
        ${sizeClasses[size]} 
        ${colorClasses[color as keyof typeof colorClasses] || colorClasses.blue}
        rounded-full flex items-center justify-center
        text-white font-bold shadow-lg
        border-2 border-white/30
        relative overflow-hidden
      `}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/30 to-transparent rounded-full" />
      <span className="relative z-10 drop-shadow-sm">{number}</span>
    </motion.div>
  );
};
