
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { NavigationMenu, NavigationMenuContent, NavigationMenuItem, NavigationMenuLink, NavigationMenuList, NavigationMenuTrigger } from "@/components/ui/navigation-menu";
import { Menu, X, Gamepad2, Info, MapPin, Zap, Dice1, RotateCcw, Crown } from "lucide-react";
import { cn } from "@/lib/utils";

export const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-gray-900/80 backdrop-blur-md border-b border-gray-700 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent hover:scale-105 transition-transform">
            <Gamepad2 className="h-6 w-6 text-blue-400" />
            XRP Lotto
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <NavigationMenu>
              <NavigationMenuList>
                <NavigationMenuItem>
                  <NavigationMenuTrigger className="bg-transparent text-gray-300 hover:text-white">
                    Games
                  </NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <div className="grid gap-3 p-6 w-[500px] lg:w-[600px]">
                      <div className="grid grid-cols-2 gap-4">
                        <NavigationMenuLink asChild>
                          <Link className="flex flex-col justify-between rounded-md bg-gradient-to-b from-blue-600/20 to-purple-600/20 p-4 no-underline outline-none focus:shadow-md hover:bg-gradient-to-b hover:from-blue-600/30 hover:to-purple-600/30 transition-all" to="/">
                            <Gamepad2 className="h-8 w-8 text-blue-400 mb-3" />
                            <div className="mb-2 text-lg font-medium text-white">
                              XRP Lotto
                            </div>
                            <p className="text-sm leading-tight text-gray-300">
                              Decentralized lottery with provably fair draws every few minutes.
                            </p>
                          </Link>
                        </NavigationMenuLink>
                        
                        <NavigationMenuLink asChild>
                          <Link className="flex flex-col justify-between rounded-md bg-gradient-to-b from-red-600/20 to-orange-600/20 p-4 no-underline outline-none focus:shadow-md hover:bg-gradient-to-b hover:from-red-600/30 hover:to-orange-600/30 transition-all" to="/roulette">
                            <RotateCcw className="h-8 w-8 text-red-400 mb-3" />
                            <div className="mb-2 text-lg font-medium text-white">
                              Live Roulette
                            </div>
                            <p className="text-sm leading-tight text-gray-300">
                              Classic roulette with realistic wheel physics and live betting.
                            </p>
                          </Link>
                        </NavigationMenuLink>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <NavigationMenuLink asChild>
                          <Link className="flex flex-col justify-between rounded-md bg-gradient-to-b from-yellow-600/20 to-amber-600/20 p-4 no-underline outline-none focus:shadow-md hover:bg-gradient-to-b hover:from-yellow-600/30 hover:to-amber-600/30 transition-all" to="/dreamcatcher">
                            <Crown className="h-8 w-8 text-yellow-400 mb-3" />
                            <div className="mb-2 text-lg font-medium text-white">
                              Dream Catcher
                            </div>
                            <p className="text-sm leading-tight text-gray-300">
                              Spin the wheel of fortune with multipliers and bonus rounds.
                            </p>
                          </Link>
                        </NavigationMenuLink>
                        
                        <div className="flex flex-col justify-between rounded-md bg-gradient-to-b from-gray-600/20 to-gray-700/20 p-4 opacity-50">
                          <Dice1 className="h-8 w-8 text-gray-400 mb-3" />
                          <div className="mb-2 text-lg font-medium text-gray-300">
                            XRP Dice
                          </div>
                          <p className="text-sm leading-tight text-gray-400">
                            Coming soon - Provably fair dice game with customizable odds.
                          </p>
                        </div>
                      </div>
                      
                      <div className="text-sm text-gray-400 border-t border-gray-600 pt-3">
                        <p>More games coming soon:</p>
                        <ul className="mt-2 space-y-1 text-gray-500">
                          <li>• XRP Poker</li>
                          <li>• XRP Sports Betting</li>
                          <li>• XRP Crash</li>
                        </ul>
                      </div>
                    </div>
                  </NavigationMenuContent>
                </NavigationMenuItem>
              </NavigationMenuList>
            </NavigationMenu>

            <Link to="/about" className="text-gray-300 hover:text-white transition-colors flex items-center gap-2">
              <Info className="h-4 w-4" />
              About
            </Link>
            <Link to="/roadmap" className="text-gray-300 hover:text-white transition-colors flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              Roadmap
            </Link>
            <Link to="/integrations" className="text-gray-300 hover:text-white transition-colors flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Integrations
            </Link>
          </div>

          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden text-gray-300"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-gray-800/95 border-t border-gray-700 animate-fade-in">
            <div className="px-2 pt-2 pb-3 space-y-1">
              <div className="px-3 py-2 text-gray-200 font-medium">Games</div>
              <Link to="/" className="block px-6 py-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-md transition-colors">
                XRP Lotto
              </Link>
              <Link to="/roulette" className="block px-6 py-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-md transition-colors">
                Live Roulette
              </Link>
              <Link to="/dreamcatcher" className="block px-6 py-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-md transition-colors">
                Dream Catcher
              </Link>
              <div className="px-6 py-2 text-gray-500">XRP Dice (Coming Soon)</div>
              
              <Link to="/about" className="block px-3 py-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-md transition-colors">
                About
              </Link>
              <Link to="/roadmap" className="block px-3 py-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-md transition-colors">
                Roadmap
              </Link>
              <Link to="/integrations" className="block px-3 py-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-md transition-colors">
                Integrations
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};
