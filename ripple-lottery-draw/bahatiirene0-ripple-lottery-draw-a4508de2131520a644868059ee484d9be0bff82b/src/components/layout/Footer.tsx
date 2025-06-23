
import { Link } from 'react-router-dom';
import { Gamepad2, Twitter, Github, MessageCircle, Mail, Shield, FileText, HelpCircle } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="bg-gray-900 border-t border-gray-700 mt-20">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              <Gamepad2 className="h-6 w-6 text-blue-400" />
              XRP Lotto
            </div>
            <p className="text-gray-400 text-sm">
              The first fully decentralized, provably fair lottery on the XRP Ledger. 
              Every draw is transparent and verifiable.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-blue-400 transition-colors">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-purple-400 transition-colors">
                <Github className="h-5 w-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-green-400 transition-colors">
                <MessageCircle className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-gray-400 hover:text-white transition-colors text-sm">
                  Play Now
                </Link>
              </li>
              <li>
                <Link to="/about" className="text-gray-400 hover:text-white transition-colors text-sm">
                  About Us
                </Link>
              </li>
              <li>
                <Link to="/roadmap" className="text-gray-400 hover:text-white transition-colors text-sm">
                  Roadmap
                </Link>
              </li>
              <li>
                <Link to="/integrations" className="text-gray-400 hover:text-white transition-colors text-sm">
                  Integrations
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-white font-semibold mb-4">Support</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/help" className="text-gray-400 hover:text-white transition-colors text-sm flex items-center gap-2">
                  <HelpCircle className="h-4 w-4" />
                  Help Center
                </Link>
              </li>
              <li>
                <Link to="/faq" className="text-gray-400 hover:text-white transition-colors text-sm">
                  FAQ
                </Link>
              </li>
              <li>
                <a href="mailto:support@xrplotto.com" className="text-gray-400 hover:text-white transition-colors text-sm flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Contact Us
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-white font-semibold mb-4">Legal</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/terms" className="text-gray-400 hover:text-white transition-colors text-sm flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link to="/privacy" className="text-gray-400 hover:text-white transition-colors text-sm flex items-center gap-2">
                  <Shield className="h-4 w-4" />
                  Privacy Policy
                </Link>
              </li>
              <li>
                <span className="text-gray-400 text-sm">
                  Responsible Gaming
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-700 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm">
            © 2024 XRP Lotto. All rights reserved. Built on XRP Ledger.
          </p>
          <p className="text-gray-500 text-xs mt-2 md:mt-0">
            Provably fair • Decentralized • Open Source
          </p>
        </div>
      </div>
    </footer>
  );
};
