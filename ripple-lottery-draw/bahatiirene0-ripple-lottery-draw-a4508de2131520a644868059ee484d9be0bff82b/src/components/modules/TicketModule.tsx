
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Ticket, ShoppingCart, Coins, Receipt } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface TicketModuleProps {
  onPotChange: (amount: number) => void;
}

export const TicketModule = ({ onPotChange }: TicketModuleProps) => {
  const [ticketPrice, setTicketPrice] = useState(10);
  const [selectedWallet, setSelectedWallet] = useState('');
  const [purchasedTickets, setPurchasedTickets] = useState<any[]>([]);
  const [totalPot, setTotalPot] = useState(0);
  const { toast } = useToast();

  const mockWallets = [
    { id: 'wallet_1', address: 'rAbC123...', balance: 500 },
    { id: 'wallet_2', address: 'rDef456...', balance: 750 },
    { id: 'wallet_3', address: 'rGhi789...', balance: 300 }
  ];

  const purchaseTicket = () => {
    if (!selectedWallet) {
      toast({
        title: "Error",
        description: "Please select a wallet",
        variant: "destructive"
      });
      return;
    }

    const selectedWalletData = mockWallets.find(w => w.id === selectedWallet);
    if (!selectedWalletData || selectedWalletData.balance < ticketPrice) {
      toast({
        title: "Insufficient Balance",
        description: "Not enough XRP in selected wallet",
        variant: "destructive"
      });
      return;
    }

    const ticket = {
      id: `ticket_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
      wallet_id: selectedWallet,
      amount: ticketPrice,
      transaction_hash: `TX${Math.random().toString(36).substr(2, 32).toUpperCase()}`,
      timestamp: Date.now(),
      lottery_wallet: 'rLottery123456789...'
    };

    setPurchasedTickets(prev => [...prev, ticket]);
    const newTotal = totalPot + ticketPrice;
    setTotalPot(newTotal);
    onPotChange(newTotal);

    toast({
      title: "Ticket Purchased",
      description: `Ticket purchased for ${ticketPrice} XRP`,
    });
  };

  return (
    <div className="space-y-6">
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Ticket className="h-5 w-5 text-green-400" />
            Ticket Purchase Module
          </CardTitle>
          <CardDescription className="text-gray-400">
            Purchase lottery tickets with XRP. Funds are automatically sent to the lottery escrow wallet.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="ticketPrice" className="text-gray-300">Ticket Price (XRP)</Label>
              <Input
                id="ticketPrice"
                type="number"
                value={ticketPrice}
                onChange={(e) => setTicketPrice(parseInt(e.target.value) || 0)}
                className="bg-gray-700 border-gray-600 text-white"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="wallet" className="text-gray-300">Select Wallet</Label>
              <select
                id="wallet"
                value={selectedWallet}
                onChange={(e) => setSelectedWallet(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 text-white rounded-md px-3 py-2"
              >
                <option value="">Choose wallet...</option>
                {mockWallets.map(wallet => (
                  <option key={wallet.id} value={wallet.id}>
                    {wallet.id} ({wallet.balance} XRP)
                  </option>
                ))}
              </select>
            </div>
          </div>

          <Button onClick={purchaseTicket} className="w-full">
            <ShoppingCart className="h-4 w-4 mr-2" />
            Purchase Ticket for {ticketPrice} XRP
          </Button>

          <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
            <span className="text-gray-300">Current Prize Pool:</span>
            <Badge variant="outline" className="text-purple-400 border-purple-400 text-lg">
              <Coins className="h-4 w-4 mr-1" />
              {totalPot} XRP
            </Badge>
          </div>
        </CardContent>
      </Card>

      {purchasedTickets.length > 0 && (
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Your Tickets</CardTitle>
            <CardDescription className="text-gray-400">
              {purchasedTickets.length} ticket(s) purchased
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {purchasedTickets.map((ticket) => (
                <div key={ticket.id} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Receipt className="h-4 w-4 text-green-400" />
                    <div>
                      <p className="text-white font-medium">{ticket.id}</p>
                      <p className="text-gray-400 text-sm">Wallet: {ticket.wallet_id}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant="secondary" className="text-green-400">
                      {ticket.amount} XRP
                    </Badge>
                    <p className="text-gray-400 text-xs mt-1">
                      {new Date(ticket.timestamp).toLocaleTimeString()}
                    </p>
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
