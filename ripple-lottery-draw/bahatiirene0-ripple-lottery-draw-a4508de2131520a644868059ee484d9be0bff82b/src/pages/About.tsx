
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Shield, Zap, Users, Globe, CheckCircle, Award } from "lucide-react";

const About = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      <Navbar />
      
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-6">
            About XRP Lotto
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            The first fully decentralized lottery platform built on the XRP Ledger, 
            providing transparent, fair, and instant gaming experiences.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <Shield className="h-8 w-8 text-blue-400 mb-2" />
              <CardTitle className="text-white">Provably Fair</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-400">
                Every draw uses XRP Ledger close hashes, making results verifiable and impossible to manipulate.
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <Zap className="h-8 w-8 text-green-400 mb-2" />
              <CardTitle className="text-white">Instant Payouts</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-400">
                Winners receive their prizes automatically through smart contracts, no delays or manual processing.
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <Users className="h-8 w-8 text-purple-400 mb-2" />
              <CardTitle className="text-white">Community Driven</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-400">
                Built by the community, for the community. Open source and governed by XRP Lotto token holders.
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="text-center">
          <h2 className="text-3xl font-bold text-white mb-8">Our Mission</h2>
          <p className="text-lg text-gray-300 max-w-4xl mx-auto leading-relaxed">
            To revolutionize online gaming through blockchain technology, creating a transparent, 
            fair, and accessible lottery platform that empowers players with true ownership and control. 
            We believe in the power of decentralization to create better experiences for everyone.
          </p>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default About;
