
export interface PluginMetadata {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  dependencies?: string[];
  permissions?: string[];
}

export interface PluginAPI {
  // Core system events
  onWalletImport?: (walletData: WalletData) => void;
  onTicketPurchase?: (ticketData: TicketData) => void;
  onDrawComplete?: (drawResult: DrawResult) => void;
  onRNGGenerated?: (rngData: RNGData) => void;
}

export interface WalletData {
  id: string;
  address: string;
  balance: number;
  imported_at: number;
}

export interface TicketData {
  id: string;
  wallet_id: string;
  amount: number;
  transaction_hash: string;
  timestamp: number;
}

export interface DrawResult {
  draw_id: string;
  ledger_hash: string;
  winner_wallet_id: string;
  total_participants: number;
  prize_amount: number;
  timestamp: number;
}

export interface RNGData {
  ledger_hash: string;
  seed_value: string;
  generated_number: number;
  total_participants: number;
  winner_index: number;
}

export interface Plugin {
  metadata: PluginMetadata;
  api: PluginAPI;
  initialize: () => Promise<void>;
  destroy: () => Promise<void>;
  isActive: boolean;
}

export interface PluginRegistry {
  [key: string]: Plugin;
}
