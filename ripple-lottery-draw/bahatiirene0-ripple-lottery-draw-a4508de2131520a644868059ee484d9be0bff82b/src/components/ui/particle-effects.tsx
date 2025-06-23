
import React, { useEffect, useState } from 'react';

interface Particle {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  color: string;
  size: number;
}

interface ParticleEffectsProps {
  trigger: boolean;
  type?: 'confetti' | 'sparkles' | 'fireworks';
  duration?: number;
}

export const ParticleEffects: React.FC<ParticleEffectsProps> = ({ 
  trigger, 
  type = 'confetti', 
  duration = 3000 
}) => {
  const [particles, setParticles] = useState<Particle[]>([]);
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    if (trigger && !isActive) {
      setIsActive(true);
      generateParticles();
      
      const timer = setTimeout(() => {
        setIsActive(false);
        setParticles([]);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [trigger, duration, isActive]);

  const generateParticles = () => {
    const newParticles: Particle[] = [];
    const particleCount = type === 'fireworks' ? 50 : 30;
    
    for (let i = 0; i < particleCount; i++) {
      newParticles.push({
        id: i,
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 10,
        vy: (Math.random() - 0.5) * 10,
        life: 0,
        maxLife: 100 + Math.random() * 50,
        color: getRandomColor(type),
        size: Math.random() * 6 + 2,
      });
    }
    
    setParticles(newParticles);
    animateParticles(newParticles);
  };

  const getRandomColor = (effectType: string) => {
    const colors = {
      confetti: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b', '#eb4d4b'],
      sparkles: ['#ffd700', '#ffed4e', '#fff200', '#ffe135'],
      fireworks: ['#ff3838', '#ff9500', '#ffdd00', '#c7f464', '#5ce1e6', '#ff6b9d']
    };
    
    const colorSet = colors[effectType as keyof typeof colors] || colors.confetti;
    return colorSet[Math.floor(Math.random() * colorSet.length)];
  };

  const animateParticles = (currentParticles: Particle[]) => {
    const animate = () => {
      setParticles(prevParticles => 
        prevParticles.map(particle => ({
          ...particle,
          x: particle.x + particle.vx,
          y: particle.y + particle.vy,
          vy: particle.vy + 0.3, // gravity
          life: particle.life + 1,
        })).filter(particle => particle.life < particle.maxLife)
      );
    };

    const interval = setInterval(animate, 16);
    setTimeout(() => clearInterval(interval), duration);
  };

  if (!isActive || particles.length === 0) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {particles.map(particle => (
        <div
          key={particle.id}
          className="absolute rounded-full animate-pulse"
          style={{
            left: `${particle.x}px`,
            top: `${particle.y}px`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            backgroundColor: particle.color,
            opacity: 1 - (particle.life / particle.maxLife),
            transform: type === 'sparkles' ? 'rotate(45deg)' : 'none',
          }}
        />
      ))}
    </div>
  );
};
