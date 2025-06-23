import { useState, useEffect } from 'react';
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RotateCcw, Wallet, Users, TrendingUp } from "lucide-react";

const Roulette = () => {
  const [isSpinning, setIsSpinning] = useState(false);
  const [selectedNumbers, setSelectedNumbers] = useState<number[]>([]);
  const [winningNumber, setWinningNumber] = useState<number | null>(null);
  const [rotation, setRotation] = useState(0);
  const [betAmount, setBetAmount] = useState(10);
  const [ballRotation, setBallRotation] = useState(0);
  const [showResult, setShowResult] = useState(false);

  const rouletteNumbers = [
    { number: 0, color: 'green' },
    { number: 32, color: 'red' }, { number: 15, color: 'black' }, { number: 19, color: 'red' },
    { number: 4, color: 'black' }, { number: 21, color: 'red' }, { number: 2, color: 'black' },
    { number: 25, color: 'red' }, { number: 17, color: 'black' }, { number: 34, color: 'red' },
    { number: 6, color: 'black' }, { number: 27, color: 'red' }, { number: 13, color: 'black' },
    { number: 36, color: 'red' }, { number: 11, color: 'black' }, { number: 30, color: 'red' },
    { number: 8, color: 'black' }, { number: 23, color: 'red' }, { number: 10, color: 'black' },
    { number: 5, color: 'red' }, { number: 24, color: 'black' }, { number: 16, color: 'red' },
    { number: 33, color: 'black' }, { number: 1, color: 'red' }, { number: 20, color: 'black' },
    { number: 14, color: 'red' }, { number: 31, color: 'black' }, { number: 9, color: 'red' },
    { number: 22, color: 'black' }, { number: 18, color: 'red' }, { number: 29, color: 'black' },
    { number: 7, color: 'red' }, { number: 28, color: 'black' }, { number: 12, color: 'red' },
    { number: 35, color: 'black' }, { number: 3, color: 'red' }, { number: 26, color: 'black' }
  ];

  const spinWheel = () => {
    if (isSpinning) return;
    
    setIsSpinning(true);
    setWinningNumber(null);
    setShowResult(false);
    
    // Generate random winning number
    const randomIndex = Math.floor(Math.random() * rouletteNumbers.length);
    const winner = rouletteNumbers[randomIndex];
    
    // Calculate rotation with more spins and easing
    const degreesPerNumber = 360 / rouletteNumbers.length;
    const baseSpins = 8; // More spins for realism
    const randomSpin = Math.random() * 360; // Add randomness
    const targetRotation = (baseSpins * 360) + randomSpin + (randomIndex * degreesPerNumber);
    
    // Ball spins opposite direction
    const ballSpins = 5;
    const ballTargetRotation = -(ballSpins * 360) - randomSpin;
    
    setRotation(prev => prev + targetRotation);
    setBallRotation(prev => prev + ballTargetRotation);
    
    // Show result after animation with bounce effect
    setTimeout(() => {
      setWinningNumber(winner.number);
      setShowResult(true);
      setIsSpinning(false);
    }, 5000);
  };

  const toggleNumber = (number: number) => {
    if (isSpinning) return;
    
    if (selectedNumbers.includes(number)) {
      setSelectedNumbers(selectedNumbers.filter(n => n !== number));
    } else {
      setSelectedNumbers([...selectedNumbers, number]);
    }
  };

  const getNumberColor = (number: number) => {
    const numData = rouletteNumbers.find(n => n.number === number);
    return numData?.color || 'black';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in">
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-red-400 to-orange-500 bg-clip-text text-transparent mb-4">
            Live Roulette
          </h1>
          <p className="text-lg text-gray-300 max-w-2xl mx-auto">
            Experience the thrill of classic European roulette with realistic physics and instant XRP payouts.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8 animate-slide-up">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Active Players</CardTitle>
              <Users className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-400">847</div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Total Bets</CardTitle>
              <TrendingUp className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-400">12,450 XRP</div>
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

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {/* Enhanced Roulette Wheel */}
          <Card className="bg-gray-800/50 border-gray-700 animate-slide-up">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <RotateCcw className="h-5 w-5 text-red-400" />
                Roulette Wheel
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center">
              <div className="relative w-80 h-80 lg:w-96 lg:h-96 mb-6">
                {/* Outer Ring */}
                <div className="absolute inset-0 rounded-full bg-gradient-to-br from-yellow-600 via-yellow-700 to-yellow-800 shadow-2xl animate-pulse-subtle"></div>
                
                {/* Wheel Base with Wood Texture */}
                <div className="absolute inset-2 rounded-full bg-gradient-radial from-amber-800 via-amber-900 to-yellow-900 shadow-inner"></div>
                
                {/* Numbers Wheel */}
                <div 
                  className={`absolute inset-6 rounded-full border-4 border-yellow-400 shadow-2xl transition-transform ease-out ${
                    isSpinning ? 'duration-[5000ms]' : 'duration-300'
                  }`}
                  style={{ 
                    transform: `rotate(${rotation}deg)`,
                    background: `conic-gradient(${rouletteNumbers.map((num, index) => {
                      const color = num.color === 'red' ? '#dc2626' : num.color === 'black' ? '#1f2937' : '#059669';
                      const startAngle = (index / rouletteNumbers.length) * 360;
                      const endAngle = ((index + 1) / rouletteNumbers.length) * 360;
                      return `${color} ${startAngle}deg ${endAngle}deg`;
                    }).join(', ')})`
                  }}
                >
                  {/* Number Labels */}
                  {rouletteNumbers.map((num, index) => (
                    <div
                      key={num.number}
                      className="absolute text-white text-xs lg:text-sm font-bold w-6 h-6 lg:w-8 lg:h-8 flex items-center justify-center drop-shadow-lg"
                      style={{
                        transform: `rotate(${(index / rouletteNumbers.length) * 360}deg) translateY(-120px) lg:translateY(-140px) rotate(-${(index / rouletteNumbers.length) * 360}deg)`,
                        transformOrigin: '50% 120px lg:50% 140px'
                      }}
                    >
                      {num.number}
                    </div>
                  ))}
                </div>
                
                {/* Spinning Ball */}
                <div 
                  className={`absolute inset-8 rounded-full transition-transform ease-out ${
                    isSpinning ? 'duration-[5000ms]' : 'duration-300'
                  }`}
                  style={{ transform: `rotate(${ballRotation}deg)` }}
                >
                  <div className="absolute top-2 left-1/2 w-3 h-3 bg-white rounded-full shadow-lg transform -translate-x-1/2 animate-bounce-subtle"></div>
                </div>
                
                {/* Center Hub */}
                <div className="absolute top-1/2 left-1/2 w-8 h-8 lg:w-12 lg:h-12 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full transform -translate-x-1/2 -translate-y-1/2 shadow-lg border-2 border-yellow-300"></div>
                
                {/* Pointer */}
                <div className="absolute top-1 left-1/2 w-0 h-0 border-l-4 border-r-4 border-b-8 border-l-transparent border-r-transparent border-b-yellow-400 transform -translate-x-1/2 drop-shadow-lg"></div>
              </div>

              {/* Enhanced Result Display */}
              {showResult && winningNumber !== null && (
                <div className="text-center mb-6 animate-bounce-in">
                  <div className="relative">
                    <Badge 
                      className={`text-xl lg:text-2xl px-6 py-3 font-bold shadow-2xl animate-glow ${
                        getNumberColor(winningNumber) === 'red' ? 'bg-red-500 border-red-400' :
                        getNumberColor(winningNumber) === 'black' ? 'bg-gray-800 border-gray-600' :
                        'bg-green-500 border-green-400'
                      }`}
                    >
                      🎉 Winner: {winningNumber} 🎉
                    </Badge>
                    <div className="absolute inset-0 bg-gradient-to-r from-yellow-400/20 to-orange-400/20 rounded-full animate-pulse"></div>
                  </div>
                  
                  {selectedNumbers.includes(winningNumber) && (
                    <div className="mt-4 animate-slide-up">
                      <div className="text-2xl lg:text-3xl font-bold text-green-400 mb-2">🎊 CONGRATULATIONS! 🎊</div>
                      <div className="text-lg text-green-300">You won {betAmount * 35} XRP!</div>
                    </div>
                  )}
                </div>
              )}

              <div className="flex gap-4 flex-wrap justify-center">
                <Button 
                  onClick={spinWheel} 
                  disabled={isSpinning || selectedNumbers.length === 0}
                  className={`bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-bold px-6 py-3 text-lg shadow-lg transform transition-all duration-200 ${
                    !isSpinning && selectedNumbers.length > 0 ? 'hover:scale-105 animate-pulse-subtle' : ''
                  }`}
                >
                  {isSpinning ? (
                    <span className="flex items-center gap-2">
                      <RotateCcw className="h-4 w-4 animate-spin" />
                      Spinning...
                    </span>
                  ) : 'Spin Wheel'}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setSelectedNumbers([])}
                  disabled={isSpinning}
                  className="border-gray-400 text-gray-300 hover:bg-gray-700 px-6 py-3"
                >
                  Clear Bets
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Enhanced Betting Board */}
          <Card className="bg-gray-800/50 border-gray-700 animate-slide-up">
            <CardHeader>
              <CardTitle>Place Your Bets</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-3">
                  Bet Amount: {betAmount} XRP
                </label>
                <input
                  type="range"
                  min="1"
                  max="100"
                  value={betAmount}
                  onChange={(e) => setBetAmount(Number(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                  disabled={isSpinning}
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>1 XRP</span>
                  <span>100 XRP</span>
                </div>
              </div>

              {/* Enhanced Number Grid */}
              <div className="grid grid-cols-3 gap-2 mb-6">
                {Array.from({ length: 36 }, (_, i) => i + 1).map(number => {
                  const isRed = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36].includes(number);
                  const isSelected = selectedNumbers.includes(number);
                  
                  return (
                    <button
                      key={number}
                      onClick={() => toggleNumber(number)}
                      disabled={isSpinning}
                      className={`
                        aspect-square text-white font-bold text-sm lg:text-base rounded-lg transition-all duration-300 transform
                        ${isRed ? 'bg-gradient-to-br from-red-600 to-red-700 hover:from-red-700 hover:to-red-800' : 'bg-gradient-to-br from-gray-800 to-gray-900 hover:from-gray-700 hover:to-gray-800'}
                        ${isSelected ? 'ring-4 ring-yellow-400 scale-110 shadow-lg animate-glow' : 'hover:scale-105'}
                        disabled:opacity-50 disabled:cursor-not-allowed shadow-md
                      `}
                    >
                      {number}
                    </button>
                  );
                })}
              </div>

              {/* Enhanced Zero Button */}
              <button
                onClick={() => toggleNumber(0)}
                disabled={isSpinning}
                className={`
                  w-full py-4 text-white font-bold text-lg rounded-lg mb-6 transition-all duration-300 transform
                  bg-gradient-to-br from-green-600 to-green-700 hover:from-green-700 hover:to-green-800
                  ${selectedNumbers.includes(0) ? 'ring-4 ring-yellow-400 scale-105 shadow-lg animate-glow' : 'hover:scale-105'}
                  disabled:opacity-50 disabled:cursor-not-allowed shadow-md
                `}
              >
                0 - GREEN
              </button>

              {/* Enhanced Betting Options */}
              <div className="grid grid-cols-2 gap-3 mb-6">
                <Button variant="outline" disabled={isSpinning} className="text-red-400 border-red-400 hover:bg-red-400/10 py-3 font-semibold">
                  🔴 Red (1:1)
                </Button>
                <Button variant="outline" disabled={isSpinning} className="text-gray-300 border-gray-400 hover:bg-gray-400/10 py-3 font-semibold">
                  ⚫ Black (1:1)
                </Button>
                <Button variant="outline" disabled={isSpinning} className="border-blue-400 text-blue-400 hover:bg-blue-400/10 py-3 font-semibold">
                  Even (1:1)
                </Button>
                <Button variant="outline" disabled={isSpinning} className="border-purple-400 text-purple-400 hover:bg-purple-400/10 py-3 font-semibold">
                  Odd (1:1)
                </Button>
              </div>

              {/* Enhanced Bet Summary */}
              {selectedNumbers.length > 0 && (
                <div className="mt-6 p-4 bg-gradient-to-r from-gray-700/50 to-gray-600/50 rounded-lg border border-gray-600 animate-slide-up">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-300">Selected Numbers:</span>
                    <span className="text-sm font-mono text-white">{selectedNumbers.join(', ')}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-300">Total Bet:</span>
                    <span className="text-lg font-bold text-green-400">{selectedNumbers.length * betAmount} XRP</span>
                  </div>
                  <div className="text-xs text-gray-400 mt-2">
                    Potential win: {selectedNumbers.length * betAmount * 35} XRP (35:1 payout)
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

export default Roulette;
