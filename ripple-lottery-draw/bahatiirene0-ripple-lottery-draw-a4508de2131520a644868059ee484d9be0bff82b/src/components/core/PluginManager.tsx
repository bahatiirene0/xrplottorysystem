
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Cpu, Download, Settings, Trash2, Plus } from "lucide-react";

export const PluginManager = () => {
  const [plugins, setPlugins] = useState([
    {
      id: 'wallet-manager',
      name: 'Wallet Manager',
      version: '1.0.0',
      description: 'Core wallet import and management functionality',
      author: 'XRP Lotto Team',
      active: true,
      core: true
    },
    {
      id: 'rng-engine',
      name: 'RNG Engine',
      version: '1.0.0',
      description: 'Verifiable random number generation using XRP Ledger',
      author: 'XRP Lotto Team',
      active: true,
      core: true
    },
    {
      id: 'ticket-system',
      name: 'Ticket System',
      version: '1.0.0',
      description: 'Ticket purchasing and management',
      author: 'XRP Lotto Team',
      active: true,
      core: true
    },
    {
      id: 'auto-draw',
      name: 'Auto Draw',
      version: '1.0.0',
      description: 'Automated drawing every 3 minutes',
      author: 'XRP Lotto Team',
      active: true,
      core: true
    },
    {
      id: 'telegram-notifications',
      name: 'Telegram Notifications',
      version: '0.9.0',
      description: 'Send draw results via Telegram bot',
      author: 'Community',
      active: false,
      core: false
    },
    {
      id: 'analytics-dashboard',
      name: 'Analytics Dashboard',
      version: '1.2.0',
      description: 'Advanced statistics and charts',
      author: 'Data Team',
      active: true,
      core: false
    },
    {
      id: 'multi-token-support',
      name: 'Multi-Token Support',
      version: '0.8.0',
      description: 'Support for other XRP Ledger tokens',
      author: 'Community',
      active: false,
      core: false
    }
  ]);

  const togglePlugin = (pluginId: string) => {
    setPlugins(prev => prev.map(plugin => 
      plugin.id === pluginId && !plugin.core
        ? { ...plugin, active: !plugin.active }
        : plugin
    ));
  };

  const removePlugin = (pluginId: string) => {
    setPlugins(prev => prev.filter(plugin => plugin.id !== pluginId || plugin.core));
  };

  return (
    <div className="space-y-6">
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Cpu className="h-5 w-5 text-blue-400" />
            Plugin Management System
          </CardTitle>
          <CardDescription className="text-gray-400">
            Manage, install, and configure plugins for your XRP Lotto system. Add or remove features without breaking core functionality.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-6">
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Install Plugin
            </Button>
            <Button variant="outline" className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Plugin Marketplace
            </Button>
          </div>

          <div className="space-y-4">
            {plugins.map((plugin) => (
              <div key={plugin.id} className="p-4 bg-gray-700/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div>
                      <h3 className="text-white font-medium">{plugin.name}</h3>
                      <p className="text-gray-400 text-sm">{plugin.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {plugin.core && (
                      <Badge variant="outline" className="text-blue-400 border-blue-400">
                        Core
                      </Badge>
                    )}
                    <Badge variant="secondary" className="text-gray-300">
                      v{plugin.version}
                    </Badge>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <span className="text-gray-400 text-sm">by {plugin.author}</span>
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={plugin.active}
                        onCheckedChange={() => togglePlugin(plugin.id)}
                        disabled={plugin.core}
                      />
                      <span className="text-sm text-gray-300">
                        {plugin.active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button size="sm" variant="ghost">
                      <Settings className="h-4 w-4" />
                    </Button>
                    {!plugin.core && (
                      <Button 
                        size="sm" 
                        variant="ghost"
                        onClick={() => removePlugin(plugin.id)}
                        className="text-red-400 hover:text-red-300"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white">Plugin Development</CardTitle>
          <CardDescription className="text-gray-400">
            Create custom plugins using our standardized API
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-700 p-4 rounded-lg">
            <h4 className="text-white font-medium mb-2">Plugin API Interface</h4>
            <pre className="text-green-400 text-sm overflow-x-auto">
{`interface Plugin {
  metadata: PluginMetadata;
  api: PluginAPI;
  initialize: () => Promise<void>;
  destroy: () => Promise<void>;
  isActive: boolean;
}

// Event hooks available:
- onWalletImport
- onTicketPurchase
- onDrawComplete
- onRNGGenerated`}
            </pre>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
