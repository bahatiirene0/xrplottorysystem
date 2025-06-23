
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Wallet, Import, Key, Copy, CheckCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface WalletModuleProps {
  onWalletChange: (count: number) => void;
}

export const WalletModule = ({ onWalletChange }: WalletModuleProps) => {
  const [wallets, setWallets] = useState<any[]>([]);
  const [seedPhrase, setSeedPhrase] = useState('');
  const [privateKey, setPrivateKey] = useState('');
  const [importMethod, setImportMethod] = useState<'seed' | 'key'>('seed');
  const { toast } = useToast();

  const generateWalletId = () => {
    return `wallet_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  const importWallet = () => {
    if (!seedPhrase && !privateKey) {
      toast({
        title: "Error",
        description: "Please provide seed phrase or private key",
        variant: "destructive"
      });
      return;
    }

    const newWallet = {
      id: generateWalletId(),
      address: `r${Math.random().toString(36).substr(2, 33)}`, // Mock XRP address
      balance: Math.floor(Math.random() * 1000) + 100,
      imported_at: Date.now(),
      method: importMethod
    };

    setWallets(prev => [...prev, newWallet]);
    onWalletChange(wallets.length + 1);
    setSeedPhrase('');
    setPrivateKey('');

    toast({
      title: "Wallet Imported",
      description: `Wallet ${newWallet.id} successfully imported`,
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied",
      description: "Address copied to clipboard",
    });
  };

  return (
    <div className="space-y-6">
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Wallet className="h-5 w-5 text-blue-400" />
            Wallet Management Module
          </CardTitle>
          <CardDescription className="text-gray-400">
            Import and manage your XRP wallets securely. Each wallet gets a unique ID for the lottery system.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2 mb-4">
            <Button
              variant={importMethod === 'seed' ? 'default' : 'outline'}
              onClick={() => setImportMethod('seed')}
              className="flex items-center gap-2"
            >
              <Key className="h-4 w-4" />
              Seed Phrase
            </Button>
            <Button
              variant={importMethod === 'key' ? 'default' : 'outline'}
              onClick={() => setImportMethod('key')}
              className="flex items-center gap-2"
            >
              <Import className="h-4 w-4" />
              Private Key
            </Button>
          </div>

          {importMethod === 'seed' ? (
            <div className="space-y-2">
              <Label htmlFor="seedPhrase" className="text-gray-300">12/24 Word Seed Phrase</Label>
              <Input
                id="seedPhrase"
                placeholder="Enter your seed phrase..."
                value={seedPhrase}
                onChange={(e) => setSeedPhrase(e.target.value)}
                className="bg-gray-700 border-gray-600 text-white"
              />
            </div>
          ) : (
            <div className="space-y-2">
              <Label htmlFor="privateKey" className="text-gray-300">Private Key</Label>
              <Input
                id="privateKey"
                placeholder="Enter your private key..."
                type="password"
                value={privateKey}
                onChange={(e) => setPrivateKey(e.target.value)}
                className="bg-gray-700 border-gray-600 text-white"
              />
            </div>
          )}

          <Button onClick={importWallet} className="w-full">
            <Import className="h-4 w-4 mr-2" />
            Import Wallet
          </Button>
        </CardContent>
      </Card>

      {wallets.length > 0 && (
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Imported Wallets</CardTitle>
            <CardDescription className="text-gray-400">
              {wallets.length} wallet(s) ready for lottery participation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {wallets.map((wallet, index) => (
                <div key={wallet.id} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Badge variant="outline" className="text-blue-400 border-blue-400">
                      #{index + 1}
                    </Badge>
                    <div>
                      <p className="text-white font-medium">ID: {wallet.id}</p>
                      <p className="text-gray-400 text-sm">{wallet.address}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className="text-green-400">
                      {wallet.balance} XRP
                    </Badge>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(wallet.address)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
