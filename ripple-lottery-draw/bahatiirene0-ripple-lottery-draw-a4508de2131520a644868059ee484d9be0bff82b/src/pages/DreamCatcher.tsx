
import { useState, useEffect } from 'react';
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Crown, Wallet, Users, TrendingUp, Star } from "lucide-react";

const DreamCatcher = () => {
  const [isSpinning, setIsSpinning] = useState(false);
  const [selectedBets, setSelectedBets] = useState<{[key: string]: number}>({});
  const [winningSegment, setWinningSegment] = useState<string | null>(null);
  const [rotation, setRotation] = useState(0);
  const [betAmount, setBetAmount] = useState(10);

  const wheelSegments = [
    { value: '1', multiplier: 1, color: 'blue', count: 23 },
    { value: '2', multiplier: 2, color: 'green', count: 15 },
    { value: '5', multiplier: 5, color: 'orange', count: 7 },
    { value: '10', multiplier: 10, color: 'red', count: 4 },
    { value: '20', multiplier: 20, color: 'purple', count: 2 },
    { value: '40', multiplier: 40, color: 'gold', count: 1 },
    { value: 'Coin Flip', multiplier: 0, color: 'silver', count: 1 },
    { value: 'Cash Hunt', multiplier: 0, color: 'rainbow', count: 1 }
  ];

  const totalSegments = 54;

  const spinWheel = () => {
    if (isSpinning || Object.keys(selectedBets).length === 0) return;
    
    setIsSpinning(true);
    setWinningSegment(null);
    
    // Create weighted array for realistic probability
    const weightedSegments: string[] = [];
    wheelSegments.forEach(segment => {
      for (let i = 0; i < segment.count; i++) {
        weightedSegments.push(segment.value);
      }
    });
    
    // Generate random winning segment
    const randomIndex = Math.floor(Math.random() * weightedSegments.length);
    const winner = weightedSegments[randomIndex];
    
    // Calculate rotation (multiple full spins + position)
    const degreesPerSegment = 360 / totalSegments;
    const targetPosition = randomIndex * degreesPerSegment;
    const targetRotation = 360 * 6 + targetPosition;
    
    setRotation(prev => prev + targetRotation);
    
    // Show result after animation
    setTimeout(() => {
      setWinningSegment(winner);
      setIsSpinning(false);
    }, 5000);
  };

  const placeBet = (segment: string, amount: number) => {
    if (isSpinning) return;
    
    setSelectedBets(prev => ({
      ...prev,
      [segment]: (prev[segment] || 0) + amount
    }));
  };

  const clearBets = () => {
    if (isSpinning) return;
    setSelectedBets({});
  };

  const getTotalBet = () => {
    return Object.values(selectedBets).reduce((sum, bet) => sum + bet, 0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-yellow-400 to-amber-500 bg-clip-text text-transparent mb-4">
            Dream Catcher
          </h1>
          <p className="text-lg text-gray-300 max-w-2xl mx-auto">
            Spin the wheel of fortune and catch your dreams with massive multipliers and bonus rounds.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Active Players</CardTitle>
              <Users className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-400">1,247</div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Total Bets</CardTitle>
              <TrendingUp className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-400">25,850 XRP</div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Your Balance</CardTitle>
              <Wallet className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-400">1,250 XRP</div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Dream Catcher Wheel */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Crown className="h-5 w-5 text-yellow-400" />
                Dream Wheel
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center">
              <div className="relative w-80 h-80 mb-6">
                {/* Wheel Base */}
                <div className="absolute inset-0 rounded-full bg-gradient-to-r from-yellow-600 to-amber-800 shadow-2xl"></div>
                
                {/* Wheel Segments */}
                <div 
                  className="absolute inset-4 rounded-full border-4 border-yellow-400 transition-transform duration-[5000ms] ease-out overflow-hidden"
                  style={{ 
                    transform: `rotate(${rotation}deg)`,
                  }}
                >
                  {/* Create visual segments */}
                  {Array.from({ length: totalSegments }, (_, index) => {
                    const angle = (index / totalSegments) * 360;
                    const segmentIndex = Math.floor(index / (totalSegments / 8));
                    const segment = wheelSegments[segmentIndex % wheelSegments.length];
                    
                    let bgColor = '#1f2937'; // default
                    switch (segment.color) {
                      case 'blue': bgColor = '#2563eb'; break;
                      case 'green': bgColor = '#16a34a'; break;
                      case 'orange': bgColor = '#ea580c'; break;
                      case 'red': bgColor = '#dc2626'; break;
                      case 'purple': bgColor = '#9333ea'; break;
                      case 'gold': bgColor = '#d97706'; break;
                      case 'silver': bgColor = '#6b7280'; break;
                      case 'rainbow': bgColor = '#ec4899'; break;
                    }
                    
                    return (
                      <div
                        key={index}
                        className="absolute w-full h-full"
                        style={{
                          background: `conic-gradient(from ${angle}deg, ${bgColor} 0deg, ${bgColor} ${360/totalSegments}deg, transparent ${360/totalSegments}deg)`,
                        }}
                      />
                    );
                  })}
                  
                  {/* Segment Values */}
                  {wheelSegments.map((segment, index) => (
                    <div
                      key={segment.value}
                      className="absolute text-white text-xs font-bold w-8 h-8 flex items-center justify-center"
                      style={{
                        transform: `rotate(${(index / wheelSegments.length) * 360}deg) translateY(-120px) rotate(-${(index / wheelSegments.length) * 360}deg)`,
                        transformOrigin: '50% 120px'
                      }}
                    >
                      {segment.value === 'Coin Flip' ? 'CF' : segment.value === 'Cash Hunt' ? 'CH' : segment.value}
                    </div>
                  ))}
                </div>
                
                {/* Center Star */}
                <div className="absolute top-1/2 left-1/2 w-8 h-8 transform -translate-x-1/2 -translate-y-1/2">
                  <Star className="w-8 h-8 text-yellow-400 fill-yellow-400" />
                </div>
                
                {/* Pointer */}
                <div className="absolute top-2 left-1/2 w-0 h-0 border-l-6 border-r-6 border-b-8 border-l-transparent border-r-transparent border-b-yellow-400 transform -translate-x-1/2"></div>
              </div>

              {winningSegment && (
                <div className="text-center mb-4 animate-scale-in">
                  <Badge className="bg-yellow-500 text-black text-lg px-4 py-2">
                    Winner: {winningSegment}
                    {wheelSegments.find(s => s.value === winningSegment)?.multiplier && 
                      ` (${wheelSegments.find(s => s.value === winningSegment)?.multiplier}x)`
                    }
                  </Badge>
                </div>
              )}

              <div className="flex gap-4">
                <Button 
                  onClick={spinWheel} 
                  disabled={isSpinning || Object.keys(selectedBets).length === 0}
                  className="bg-yellow-600 hover:bg-yellow-700 text-black font-bold"
                >
                  {isSpinning ? 'Spinning...' : 'Spin Wheel'}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={clearBets}
                  disabled={isSpinning}
                >
                  Clear Bets
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Betting Board */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle>Place Your Bets</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Quick Bet Amount: {betAmount} XRP
                </label>
                <div className="flex gap-2 mb-4">
                  {[1, 5, 10, 25, 50].map(amount => (
                    <Button
                      key={amount}
                      variant="outline"
                      size="sm"
                      onClick={() => setBetAmount(amount)}
                      className={betAmount === amount ? 'bg-yellow-500/20 border-yellow-500' : ''}
                      disabled={isSpinning}
                    >
                      {amount}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Betting Options */}
              <div className="grid grid-cols-2 gap-3 mb-6">
                {wheelSegments.map(segment => (
                  <div key={segment.value} className="space-y-2">
                    <Button
                      onClick={() => placeBet(segment.value, betAmount)}
                      disabled={isSpinning}
                      className={`
                        w-full py-4 text-white font-bold rounded transition-all duration-200
                        ${segment.color === 'blue' ? 'bg-blue-600 hover:bg-blue-700' :
                          segment.color === 'green' ? 'bg-green-600 hover:bg-green-700' :
                          segment.color === 'orange' ? 'bg-orange-600 hover:bg-orange-700' :
                          segment.color === 'red' ? 'bg-red-600 hover:bg-red-700' :
                          segment.color === 'purple' ? 'bg-purple-600 hover:bg-purple-700' :
                          segment.color === 'gold' ? 'bg-yellow-600 hover:bg-yellow-700 text-black' :
                          segment.color === 'silver' ? 'bg-gray-600 hover:bg-gray-700' :
                          'bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600'
                        }
                        ${selectedBets[segment.value] ? 'ring-2 ring-yellow-400' : ''}
                      `}
                    >
                      <div className="text-center">
                        <div className="text-lg">{segment.value}</div>
                        {segment.multiplier > 0 && (
                          <div className="text-sm opacity-80">{segment.multiplier}:1</div>
                        )}
                      </div>
                    </Button>
                    
                    {selectedBets[segment.value] && (
                      <div className="text-center text-sm text-yellow-400">
                        Bet: {selectedBets[segment.value]} XRP
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {getTotalBet() > 0 && (
                <div className="p-4 bg-gray-700/50 rounded">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Total Bet:</span>
                    <span className="text-yellow-400 font-bold text-lg">{getTotalBet()} XRP</span>
                  </div>
                  <div className="text-sm text-gray-400 mt-1">
                    {Object.entries(selectedBets).map(([segment, amount]) => (
                      <div key={segment}>
                        {segment}: {amount} XRP
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default DreamCatcher;
