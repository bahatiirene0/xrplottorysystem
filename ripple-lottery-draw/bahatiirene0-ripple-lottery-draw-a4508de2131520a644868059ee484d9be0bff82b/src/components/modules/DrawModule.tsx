import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Timer, Play, Trophy, History, Clock, Users, CheckCircle, ExternalLink } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface DrawModuleProps {
  nextDrawTime: number;
}

interface Participant {
  wallet_id: string;
  tickets: number;
  address: string;
}

interface DrawResult {
  id: string;
  ledger_hash: string;
  winner_wallet_id: string;
  winner_address: string;
  total_participants: number;
  total_tickets: number;
  prize_amount: number;
  timestamp: number;
  transaction_hash: string;
  payment_proof_hash: string;
}

export const DrawModule = ({ nextDrawTime }: DrawModuleProps) => {
  const [drawHistory, setDrawHistory] = useState<DrawResult[]>([]);
  const [isDrawing, setIsDrawing] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [animationSpeed, setAnimationSpeed] = useState(50);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [showCongratulations, setShowCongratulations] = useState(false);
  const [latestWinner, setLatestWinner] = useState<DrawResult | null>(null);
  const animationRef = useRef<number>();
  const startTimeRef = useRef<number>();
  const { toast } = useToast();

  // Mock participants with multiple tickets
  useEffect(() => {
    const mockParticipants: Participant[] = Array.from({ length: 25 }, (_, i) => ({
      wallet_id: `wallet_${i + 1}`,
      tickets: Math.floor(Math.random() * 5) + 1, // 1-5 tickets per participant
      address: `r${Math.random().toString(36).substr(2, 33)}...`
    }));
    setParticipants(mockParticipants);
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const generateMockHashes = () => {
    const chars = '0123456789ABCDEF';
    const generateHash = (length: number) => {
      return Array.from({ length }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
    };
    
    return {
      transaction_hash: generateHash(64),
      payment_proof_hash: generateHash(64),
      ledger_hash: `F4D2B${generateHash(59)}`
    };
  };

  const animateSelection = (targetIndex: number, duration: number = 3000) => {
    const startTime = Date.now();
    startTimeRef.current = startTime;
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function for realistic deceleration (cubic-out)
      const easeOut = 1 - Math.pow(1 - progress, 3);
      
      // Calculate current speed based on easing
      const maxSpeed = 150; // Initial fast speed
      const minSpeed = 500; // Final slow speed
      const currentSpeed = maxSpeed + (minSpeed - maxSpeed) * easeOut;
      
      // Calculate how many items we should have passed
      const totalItems = participants.length;
      const currentPosition = (targetIndex + (easeOut * totalItems * 3)) % totalItems;
      
      setCurrentIndex(Math.floor(currentPosition));
      setAnimationSpeed(currentSpeed);
      
      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        setCurrentIndex(targetIndex);
        setAnimationSpeed(0);
        
        // Finish the draw after animation
        setTimeout(() => {
          finishDraw(targetIndex);
        }, 500);
      }
    };
    
    animationRef.current = requestAnimationFrame(animate);
  };

  const finishDraw = (winnerIndex: number) => {
    const winner = participants[winnerIndex];
    const totalTickets = participants.reduce((sum, p) => sum + p.tickets, 0);
    const hashes = generateMockHashes();
    
    const newDraw: DrawResult = {
      id: `draw_${Date.now()}`,
      ledger_hash: hashes.ledger_hash,
      winner_wallet_id: winner.wallet_id,
      winner_address: winner.address,
      total_participants: participants.length,
      total_tickets: totalTickets,
      prize_amount: totalTickets * 10, // 10 XRP per ticket
      timestamp: Date.now(),
      transaction_hash: hashes.transaction_hash,
      payment_proof_hash: hashes.payment_proof_hash
    };
    
    setDrawHistory(prev => [newDraw, ...prev.slice(0, 9)]);
    setLatestWinner(newDraw);
    setIsDrawing(false);
    setShowCongratulations(true);

    // Show toast notification
    toast({
      title: "🎉 Draw Complete!",
      description: `${winner.wallet_id} won ${newDraw.prize_amount} XRP!`,
    });

    // Auto-hide congratulations after 8 seconds
    setTimeout(() => {
      setShowCongratulations(false);
      setLatestWinner(null);
    }, 8000);
  };

  const simulateDraw = async () => {
    if (participants.length === 0) return;
    
    setIsDrawing(true);
    
    // Create weighted array based on tickets
    const weightedParticipants: number[] = [];
    participants.forEach((participant, index) => {
      for (let i = 0; i < participant.tickets; i++) {
        weightedParticipants.push(index);
      }
    });
    
    // Simulate ledger hash based selection
    const randomValue = Math.floor(Math.random() * weightedParticipants.length);
    const winnerIndex = weightedParticipants[randomValue];
    
    // Start animation
    animateSelection(winnerIndex, 4000);
  };

  // Cleanup animation on unmount
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  const totalTickets = participants.reduce((sum, p) => sum + p.tickets, 0);
  const currentPrizePool = totalTickets * 10;

  return (
    <div className="space-y-6">
      {/* Congratulations Overlay */}
      {showCongratulations && latestWinner && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 animate-fade-in">
          <div className="bg-gradient-to-br from-yellow-400/20 to-purple-600/20 border border-yellow-400/50 rounded-2xl p-8 max-w-2xl mx-4 text-center animate-scale-in">
            <div className="mb-6">
              <div className="text-6xl mb-4 animate-bounce">🎉</div>
              <h2 className="text-4xl font-bold text-yellow-400 mb-2">Congratulations!</h2>
              <p className="text-2xl text-white mb-4">{latestWinner.winner_wallet_id}</p>
              <div className="text-3xl font-bold text-green-400 mb-6">
                Won {latestWinner.prize_amount} XRP!
              </div>
            </div>

            <div className="bg-gray-800/50 rounded-lg p-6 space-y-4 text-left">
              <h3 className="text-lg font-semibold text-white mb-4 text-center">Transaction Details</h3>
              
              <div className="space-y-3">
                <div>
                  <p className="text-gray-400 text-sm">Winner Address</p>
                  <p className="text-green-400 font-mono text-sm break-all">{latestWinner.winner_address}</p>
                </div>
                
                <div>
                  <p className="text-gray-400 text-sm">Transaction Hash</p>
                  <div className="flex items-center gap-2">
                    <p className="text-blue-400 font-mono text-sm break-all flex-1">{latestWinner.transaction_hash}</p>
                    <ExternalLink className="h-4 w-4 text-blue-400 cursor-pointer hover:text-blue-300" />
                  </div>
                </div>
                
                <div>
                  <p className="text-gray-400 text-sm">Payment Proof Hash</p>
                  <div className="flex items-center gap-2">
                    <p className="text-purple-400 font-mono text-sm break-all flex-1">{latestWinner.payment_proof_hash}</p>
                    <ExternalLink className="h-4 w-4 text-purple-400 cursor-pointer hover:text-purple-300" />
                  </div>
                </div>
                
                <div>
                  <p className="text-gray-400 text-sm">Ledger Hash Used</p>
                  <p className="text-orange-400 font-mono text-sm break-all">{latestWinner.ledger_hash}</p>
                </div>

                <div className="flex items-center justify-center gap-2 pt-4">
                  <CheckCircle className="h-5 w-5 text-green-400" />
                  <span className="text-green-400 font-medium">Payment Verified on XRP Ledger</span>
                </div>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-600/20 border border-blue-400/50 rounded-lg">
              <p className="text-blue-300 font-medium text-lg">🎟️ Next Draw Open for Participation!</p>
              <p className="text-gray-300 text-sm mt-1">Purchase tickets now for the next draw in {formatTime(nextDrawTime)}</p>
            </div>
          </div>
        </div>
      )}

      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Timer className="h-5 w-5 text-orange-400" />
            Automated Draw Module
          </CardTitle>
          <CardDescription className="text-gray-400">
            Draws execute automatically every 3 minutes using the latest XRP Ledger close hash.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center">
            <div className="text-6xl font-bold text-orange-400 mb-2">
              {formatTime(nextDrawTime)}
            </div>
            <p className="text-gray-400">Until next draw</p>
          </div>

          {/* Animation Display */}
          {participants.length > 0 && (
            <div className="bg-gray-700/30 rounded-lg p-4">
              <h3 className="text-white font-medium mb-3 text-center">
                {isDrawing ? 'Drawing in progress...' : 'Current Participants'}
              </h3>
              <div className="relative">
                <div className="flex overflow-hidden rounded-lg bg-gray-800/50 p-2">
                  <div 
                    className="flex transition-transform duration-100 ease-linear"
                    style={{
                      transform: `translateX(-${currentIndex * 120}px)`,
                      transitionDuration: isDrawing ? `${animationSpeed}ms` : '300ms'
                    }}
                  >
                    {participants.map((participant, index) => (
                      <div
                        key={participant.wallet_id}
                        className={`flex-shrink-0 w-28 mx-1 p-2 rounded text-center transition-all duration-200 ${
                          currentIndex === index && isDrawing
                            ? 'bg-yellow-500/30 border-2 border-yellow-400 scale-110'
                            : currentIndex === index && !isDrawing && drawHistory.length > 0 && drawHistory[0].winner_wallet_id === participant.wallet_id
                            ? 'bg-green-500/30 border-2 border-green-400'
                            : 'bg-gray-600/50 border border-gray-500'
                        }`}
                      >
                        <div className="text-white text-xs font-medium truncate">
                          {participant.wallet_id}
                        </div>
                        <div className="text-gray-300 text-xs mt-1">
                          {participant.tickets} ticket{participant.tickets > 1 ? 's' : ''}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Selection indicator */}
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 pointer-events-none">
                  <div className="w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-yellow-400"></div>
                </div>
              </div>
            </div>
          )}

          <Button 
            onClick={simulateDraw} 
            disabled={isDrawing || participants.length === 0}
            className="w-full"
            variant="outline"
          >
            <Play className="h-4 w-4 mr-2" />
            {isDrawing ? 'Drawing...' : 'Simulate Draw (Demo)'}
          </Button>
        </CardContent>
      </Card>

      {drawHistory.length > 0 && (
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Recent Draws</CardTitle>
            <CardDescription className="text-gray-400">
              Latest draw results with full verification data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {drawHistory.map((draw, index) => (
                <div key={draw.id} className="p-4 bg-gray-700/50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant={index === 0 ? "default" : "secondary"}>
                      Draw #{draw.id.split('_')[1]}
                    </Badge>
                    <span className="text-gray-400 text-sm">
                      {new Date(draw.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-400">Winner</p>
                      <p className="text-green-400 font-medium">{draw.winner_wallet_id}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Participants</p>
                      <p className="text-white">{draw.total_participants}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Total Tickets</p>
                      <p className="text-blue-400">{draw.total_tickets}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Prize</p>
                      <p className="text-purple-400 font-medium">{draw.prize_amount} XRP</p>
                    </div>
                  </div>
                  <div className="mt-2">
                    <p className="text-gray-400 text-xs">Ledger Hash:</p>
                    <p className="text-gray-300 font-mono text-xs break-all">{draw.ledger_hash}</p>
                  </div>
                  {draw.transaction_hash && (
                    <div className="mt-2">
                      <p className="text-gray-400 text-xs">Transaction Hash:</p>
                      <p className="text-blue-400 font-mono text-xs break-all">{draw.transaction_hash}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
