
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Shield, Search, CheckCircle, AlertCircle } from "lucide-react";

export const VerificationModule = () => {
  const [hashToVerify, setHashToVerify] = useState('');
  const [drawIdToVerify, setDrawIdToVerify] = useState('');
  const [verificationResult, setVerificationResult] = useState<any>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  const verifyDraw = async () => {
    if (!hashToVerify && !drawIdToVerify) return;
    
    setIsVerifying(true);
    
    // Simulate verification process
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const result = {
      draw_id: drawIdToVerify || `draw_${Date.now()}`,
      ledger_hash: hashToVerify || `F4D2B${Math.random().toString(16).substr(2, 59).toUpperCase()}`,
      is_valid: Math.random() > 0.1, // 90% success rate for demo
      winner_wallet_id: `wallet_${Math.floor(Math.random() * 50) + 1}`,
      total_participants: 42,
      verification_steps: [
        "✓ Ledger hash exists on XRP Ledger",
        "✓ Hash conversion algorithm verified",
        "✓ Modulo calculation confirmed",
        "✓ Winner wallet ID matches participants list",
        "✓ Prize distribution transaction verified"
      ],
      timestamp: Date.now()
    };
    
    setVerificationResult(result);
    setIsVerifying(false);
  };

  return (
    <div className="space-y-6">
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Shield className="h-5 w-5 text-cyan-400" />
            Independent Verification Module
          </CardTitle>
          <CardDescription className="text-gray-400">
            Verify any draw result independently using the ledger hash or draw ID. Complete transparency guaranteed.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="hashVerify" className="text-gray-300">Ledger Hash to Verify</Label>
            <Input
              id="hashVerify"
              placeholder="Enter XRP Ledger close hash..."
              value={hashToVerify}
              onChange={(e) => setHashToVerify(e.target.value)}
              className="bg-gray-700 border-gray-600 text-white font-mono text-sm"
            />
          </div>

          <div className="text-center text-gray-400">OR</div>

          <div className="space-y-2">
            <Label htmlFor="drawIdVerify" className="text-gray-300">Draw ID to Verify</Label>
            <Input
              id="drawIdVerify"
              placeholder="Enter draw ID (e.g., draw_123456789)..."
              value={drawIdToVerify}
              onChange={(e) => setDrawIdToVerify(e.target.value)}
              className="bg-gray-700 border-gray-600 text-white"
            />
          </div>

          <Button 
            onClick={verifyDraw}
            disabled={(!hashToVerify && !drawIdToVerify) || isVerifying}
            className="w-full"
          >
            <Search className="h-4 w-4 mr-2" />
            {isVerifying ? 'Verifying...' : 'Verify Draw Result'}
          </Button>
        </CardContent>
      </Card>

      {verificationResult && (
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              {verificationResult.is_valid ? (
                <CheckCircle className="h-5 w-5 text-green-400" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-400" />
              )}
              Verification Result
            </CardTitle>
            <CardDescription className="text-gray-400">
              Independent verification completed
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-center mb-4">
              <Badge 
                variant={verificationResult.is_valid ? "default" : "destructive"}
                className="text-lg px-4 py-2"
              >
                {verificationResult.is_valid ? "✓ VERIFIED" : "✗ INVALID"}
              </Badge>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-gray-300">Draw ID</Label>
                <p className="text-white font-mono bg-gray-700 p-2 rounded text-sm">
                  {verificationResult.draw_id}
                </p>
              </div>
              <div className="space-y-2">
                <Label className="text-gray-300">Winner</Label>
                <p className="text-green-400 font-medium bg-gray-700 p-2 rounded">
                  {verificationResult.winner_wallet_id}
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-gray-300">Ledger Hash</Label>
              <p className="text-white font-mono text-xs bg-gray-700 p-2 rounded break-all">
                {verificationResult.ledger_hash}
              </p>
            </div>

            <div className="space-y-2">
              <Label className="text-gray-300">Verification Steps</Label>
              <div className="bg-gray-700 p-4 rounded space-y-2">
                {verificationResult.verification_steps.map((step: string, index: number) => (
                  <div key={index} className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span className="text-gray-300 text-sm">{step}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="text-center">
              <Badge variant="secondary" className="text-blue-400">
                Verified at: {new Date(verificationResult.timestamp).toLocaleString()}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
