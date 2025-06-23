
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Wallet, History, Trophy, Clock, ChevronRight, Eye, ExternalLink } from "lucide-react";

interface Transaction {
  id: string;
  type: 'ticket_purchase' | 'win' | 'refund';
  amount: number;
  draw_id: string;
  timestamp: number;
  status: 'confirmed' | 'pending';
  hash: string;
}

interface WalletStats {
  balance: number;
  totalSpent: number;
  totalWon: number;
  totalTickets: number;
  activeTickets: number;
}

export const WalletDashboard = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState('');
  
  // Mock data
  const stats: WalletStats = {
    balance: 1250.5,
    totalSpent: 450,
    totalWon: 850,
    totalTickets: 45,
    activeTickets: 8
  };

  const transactions: Transaction[] = [
    {
      id: '1',
      type: 'win',
      amount: 850,
      draw_id: 'draw_123',
      timestamp: Date.now() - 3600000,
      status: 'confirmed',
      hash: 'ABC123...DEF789'
    },
    {
      id: '2',
      type: 'ticket_purchase',
      amount: -50,
      draw_id: 'draw_124',
      timestamp: Date.now() - 7200000,
      status: 'confirmed',
      hash: 'XYZ456...UVW012'
    },
    {
      id: '3',
      type: 'ticket_purchase',
      amount: -30,
      draw_id: 'draw_122',
      timestamp: Date.now() - 86400000,
      status: 'confirmed',
      hash: 'GHI789...JKL345'
    }
  ];

  const connectWallet = () => {
    // Simulate wallet connection
    setIsConnected(true);
    setWalletAddress('rNcFh9zzZgb...3k4pQ5');
  };

  if (!isConnected) {
    return (
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-400/20 to-purple-500/20 rounded-full flex items-center justify-center mb-4">
            <Wallet className="h-8 w-8 text-blue-400" />
          </div>
          <CardTitle className="text-white">Connect Your Wallet</CardTitle>
          <CardDescription className="text-gray-400">
            Connect your XRP wallet to view your account, purchase tickets, and track your history.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          <Button onClick={connectWallet} className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
            Connect Wallet
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Wallet Header */}
      <Card className="bg-gradient-to-r from-blue-600/10 to-purple-600/10 border-blue-500/30">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
                <Wallet className="h-6 w-6 text-white" />
              </div>
              <div>
                <CardTitle className="text-white">Wallet Connected</CardTitle>
                <CardDescription className="text-gray-300 font-mono text-sm">
                  {walletAddress}
                </CardDescription>
              </div>
            </div>
            <Badge variant="outline" className="text-green-400 border-green-400">
              Connected
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-gray-400">Balance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-400">{stats.balance} XRP</div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-gray-400">Total Won</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-400">+{stats.totalWon} XRP</div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-gray-400">Total Spent</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-400">-{stats.totalSpent} XRP</div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-gray-400">Active Tickets</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-400">{stats.activeTickets}</div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="history" className="w-full">
        <TabsList className="grid w-full grid-cols-2 bg-gray-800/50">
          <TabsTrigger value="history" className="flex items-center gap-2">
            <History className="h-4 w-4" />
            Transaction History
          </TabsTrigger>
          <TabsTrigger value="tickets" className="flex items-center gap-2">
            <Trophy className="h-4 w-4" />
            Active Tickets
          </TabsTrigger>
        </TabsList>

        <TabsContent value="history" className="mt-6">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Recent Transactions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {transactions.map((tx) => (
                  <div key={tx.id} className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        tx.type === 'win' ? 'bg-green-500/20' : 
                        tx.type === 'ticket_purchase' ? 'bg-blue-500/20' : 'bg-yellow-500/20'
                      }`}>
                        {tx.type === 'win' ? <Trophy className="h-5 w-5 text-green-400" /> :
                         tx.type === 'ticket_purchase' ? <Wallet className="h-5 w-5 text-blue-400" /> :
                         <Clock className="h-5 w-5 text-yellow-400" />}
                      </div>
                      <div>
                        <p className="text-white font-medium">
                          {tx.type === 'win' ? 'Prize Won' :
                           tx.type === 'ticket_purchase' ? 'Ticket Purchase' : 'Refund'}
                        </p>
                        <p className="text-gray-400 text-sm">
                          {new Date(tx.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-semibold ${
                        tx.amount > 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {tx.amount > 0 ? '+' : ''}{tx.amount} XRP
                      </p>
                      <div className="flex items-center gap-2">
                        <Badge variant={tx.status === 'confirmed' ? 'default' : 'secondary'} className="text-xs">
                          {tx.status}
                        </Badge>
                        <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                          <ExternalLink className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tickets" className="mt-6">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Active Tickets</CardTitle>
              <CardDescription className="text-gray-400">
                Your tickets for upcoming draws
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
                  <div>
                    <p className="text-white font-medium">Quick Draw #127</p>
                    <p className="text-gray-400 text-sm">5 tickets • Next draw in 2:34</p>
                  </div>
                  <div className="text-right">
                    <p className="text-blue-400 font-semibold">50 XRP</p>
                    <p className="text-gray-400 text-xs">Prize pool: 1,250 XRP</p>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
                  <div>
                    <p className="text-white font-medium">Hourly Draw #24</p>
                    <p className="text-gray-400 text-sm">3 tickets • Next draw in 45:12</p>
                  </div>
                  <div className="text-right">
                    <p className="text-blue-400 font-semibold">150 XRP</p>
                    <p className="text-gray-400 text-xs">Prize pool: 2,500 XRP</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
