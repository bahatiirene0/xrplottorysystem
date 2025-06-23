
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Dice6, Hash, Calculator, RefreshCw } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export const RNGModule = () => {
  const [ledgerHash, setLedgerHash] = useState('');
  const [participants, setParticipants] = useState(50);
  const [result, setResult] = useState<any>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const { toast } = useToast();

  // Simulate XRP Ledger hash to number conversion
  const generateRandomNumber = async (hash: string, totalParticipants: number) => {
    setIsCalculating(true);
    
    // Simulate calculation delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Convert hash to number (simplified for demo)
    const hashBuffer = new TextEncoder().encode(hash);
    let numericValue = 0;
    for (let i = 0; i < hashBuffer.length; i++) {
      numericValue += hashBuffer[i] * (i + 1);
    }
    
    const winnerIndex = numericValue % totalParticipants;
    
    const rngResult = {
      ledger_hash: hash,
      seed_value: numericValue.toString(),
      total_participants: totalParticipants,
      winner_index: winnerIndex,
      winner_wallet_id: `wallet_${winnerIndex + 1}`,
      timestamp: Date.now(),
      verification_steps: [
        `1. Hash input: ${hash}`,
        `2. Converted to numeric: ${numericValue}`,
        `3. Modulo operation: ${numericValue} % ${totalParticipants}`,
        `4. Winner index: ${winnerIndex}`,
        `5. Winner wallet: wallet_${winnerIndex + 1}`
      ]
    };
    
    setResult(rngResult);
    setIsCalculating(false);
    
    toast({
      title: "RNG Generated",
      description: `Winner determined: Wallet #${winnerIndex + 1}`,
    });
  };

  const generateSampleHash = () => {
    const sampleHash = `F4D2B${Math.random().toString(16).substr(2, 59).toUpperCase()}`;
    setLedgerHash(sampleHash);
  };

  return (
    <div className="space-y-6">
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Dice6 className="h-5 w-5 text-purple-400" />
            Verifiable RNG Module
          </CardTitle>
          <CardDescription className="text-gray-400">
            Generate provably fair random numbers using XRP Ledger close hash. Completely verifiable and deterministic.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="ledgerHash" className="text-gray-300">XRP Ledger Close Hash</Label>
            <div className="flex gap-2">
              <Input
                id="ledgerHash"
                placeholder="Enter ledger close hash..."
                value={ledgerHash}
                onChange={(e) => setLedgerHash(e.target.value)}
                className="bg-gray-700 border-gray-600 text-white font-mono text-sm"
              />
              <Button onClick={generateSampleHash} variant="outline" size="sm">
                <Hash className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="participants" className="text-gray-300">Total Participants</Label>
            <Input
              id="participants"
              type="number"
              value={participants}
              onChange={(e) => setParticipants(parseInt(e.target.value) || 0)}
              className="bg-gray-700 border-gray-600 text-white"
            />
          </div>

          <Button 
            onClick={() => generateRandomNumber(ledgerHash, participants)}
            disabled={!ledgerHash || participants <= 0 || isCalculating}
            className="w-full"
          >
            {isCalculating ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Calculator className="h-4 w-4 mr-2" />
            )}
            {isCalculating ? 'Calculating...' : 'Generate Winner'}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">RNG Result</CardTitle>
            <CardDescription className="text-gray-400">
              Deterministic result - same hash always produces same winner
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-gray-300">Winner</Label>
                <Badge variant="outline" className="text-green-400 border-green-400 text-lg">
                  Wallet #{result.winner_index + 1}
                </Badge>
              </div>
              <div className="space-y-2">
                <Label className="text-gray-300">Seed Value</Label>
                <p className="text-white font-mono text-sm bg-gray-700 p-2 rounded">
                  {result.seed_value}
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-gray-300">Verification Steps</Label>
              <div className="bg-gray-700 p-4 rounded space-y-1">
                {result.verification_steps.map((step: string, index: number) => (
                  <p key={index} className="text-gray-300 text-sm font-mono">
                    {step}
                  </p>
                ))}
              </div>
            </div>

            <Badge variant="secondary" className="text-blue-400">
              Generated at: {new Date(result.timestamp).toLocaleString()}
            </Badge>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
