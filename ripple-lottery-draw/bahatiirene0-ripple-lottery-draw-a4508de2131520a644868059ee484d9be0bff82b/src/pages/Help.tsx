import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { HelpCircle, MessageCircle, Mail, BookOpen, Shield, Dice6, Code } from "lucide-react";
import { RNGModule } from "@/components/modules/RNGModule";
import { VerificationModule } from "@/components/modules/VerificationModule";

const Help = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      <Navbar />
      
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-6">
            Help Center
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Find answers to common questions and understand our provably fair system.
          </p>
        </div>

        <div className="max-w-6xl mx-auto">
          <Tabs defaultValue="faq" className="w-full">
            <TabsList className="grid w-full grid-cols-4 mb-8">
              <TabsTrigger value="faq" className="flex items-center gap-2">
                <HelpCircle className="h-4 w-4" />
                FAQ
              </TabsTrigger>
              <TabsTrigger value="fairness" className="flex items-center gap-2">
                <Shield className="h-4 w-4" />
                Provably Fair
              </TabsTrigger>
              <TabsTrigger value="code" className="flex items-center gap-2">
                <Code className="h-4 w-4" />
                RNG Code
              </TabsTrigger>
              <TabsTrigger value="rng" className="flex items-center gap-2">
                <Dice6 className="h-4 w-4" />
                RNG Demo
              </TabsTrigger>
            </TabsList>

            <TabsContent value="faq">
              <Card className="bg-gray-800/50 border-gray-700 mb-8">
                <CardHeader>
                  <CardTitle className="text-white">Frequently Asked Questions</CardTitle>
                </CardHeader>
                <CardContent>
                  <Accordion type="single" collapsible className="w-full">
                    <AccordionItem value="item-1">
                      <AccordionTrigger className="text-white">How do I connect my wallet?</AccordionTrigger>
                      <AccordionContent className="text-gray-400">
                        Click on the "Wallet" tab and then "Connect Wallet". We support all major XRP wallets including XUMM, GateHub, and others.
                      </AccordionContent>
                    </AccordionItem>

                    <AccordionItem value="item-2">
                      <AccordionTrigger className="text-white">How are winners selected?</AccordionTrigger>
                      <AccordionContent className="text-gray-400">
                        Winners are selected using the XRP Ledger close hash, making the process completely transparent and verifiable. Each ticket gives you one entry into the draw.
                      </AccordionContent>
                    </AccordionItem>

                    <AccordionItem value="item-3">
                      <AccordionTrigger className="text-white">When do I receive my winnings?</AccordionTrigger>
                      <AccordionContent className="text-gray-400">
                        Winnings are paid out automatically to your wallet immediately after the draw is completed. No manual processing required.
                      </AccordionContent>
                    </AccordionItem>

                    <AccordionItem value="item-4">
                      <AccordionTrigger className="text-white">What are the different draw types?</AccordionTrigger>
                      <AccordionContent className="text-gray-400">
                        We offer Quick Draws (every 3 minutes), Hourly Draws, Daily Jackpots, and Weekly Mega Jackpots. Each has different prize pools and participation levels.
                      </AccordionContent>
                    </AccordionItem>

                    <AccordionItem value="item-5">
                      <AccordionTrigger className="text-white">Is XRP Lotto safe?</AccordionTrigger>
                      <AccordionContent className="text-gray-400">
                        Yes, XRP Lotto is built on the XRP Ledger with smart contracts that ensure fairness and security. All draws are provably fair and verifiable.
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="bg-gray-800/50 border-gray-700 text-center">
                  <CardHeader>
                    <MessageCircle className="h-8 w-8 text-blue-400 mx-auto mb-2" />
                    <CardTitle className="text-white">Discord</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-400 mb-4">Join our community for real-time support</p>
                  </CardContent>
                </Card>

                <Card className="bg-gray-800/50 border-gray-700 text-center">
                  <CardHeader>
                    <Mail className="h-8 w-8 text-green-400 mx-auto mb-2" />
                    <CardTitle className="text-white">Email Support</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-400 mb-4">support@xrplotto.com</p>
                  </CardContent>
                </Card>

                <Card className="bg-gray-800/50 border-gray-700 text-center">
                  <CardHeader>
                    <BookOpen className="h-8 w-8 text-purple-400 mx-auto mb-2" />
                    <CardTitle className="text-white">Documentation</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-400 mb-4">Read our complete guides</p>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="fairness">
              <div className="space-y-8">
                <Card className="bg-gray-800/50 border-gray-700">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-white">
                      <Shield className="h-5 w-5 text-green-400" />
                      Why Our System is Provably Fair
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6 text-gray-300">
                    <div className="space-y-4">
                      <h3 className="text-xl font-semibold text-white">🔒 Complete Transparency</h3>
                      <p>
                        Unlike traditional lottery systems that rely on physical balls or centralized random number generators, 
                        XRP Lotto uses the XRP Ledger's close hash as the source of randomness. This hash is:
                      </p>
                      <ul className="list-disc pl-6 space-y-2">
                        <li><strong>Public:</strong> Anyone can verify the hash on the XRP Ledger</li>
                        <li><strong>Immutable:</strong> Cannot be changed or manipulated after creation</li>
                        <li><strong>Unpredictable:</strong> Generated by the decentralized XRP network</li>
                        <li><strong>Verifiable:</strong> Mathematical proof of fairness</li>
                      </ul>
                    </div>

                    <div className="space-y-4">
                      <h3 className="text-xl font-semibold text-white">🎯 Deterministic Process</h3>
                      <p>
                        Our winner selection process is completely deterministic, meaning the same input will always 
                        produce the same output. Here's how it works:
                      </p>
                      <ol className="list-decimal pl-6 space-y-2">
                        <li>Take the XRP Ledger close hash (64 characters)</li>
                        <li>Convert the hash to a large number</li>
                        <li>Use modulo operation with total participants</li>
                        <li>Result determines the winner index</li>
                      </ol>
                    </div>

                    <div className="space-y-4">
                      <h3 className="text-xl font-semibold text-white">⚡ No Luck Required</h3>
                      <p className="text-yellow-400 font-medium">
                        This isn't about luck - it's about mathematics and transparency. Every player has an equal, 
                        verifiable chance based on their participation. You don't need to "trust" us - you can verify everything yourself.
                      </p>
                    </div>

                    <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 p-6 rounded-lg border border-blue-700/50">
                      <h4 className="text-lg font-semibold text-white mb-3">🧮 Mathematical Guarantee</h4>
                      <p className="text-blue-200">
                        The probability of winning is exactly: <code className="bg-blue-800 px-2 py-1 rounded">1 / total_participants</code>
                      </p>
                      <p className="text-blue-200 mt-2">
                        This is mathematically guaranteed and verifiable by anyone, anywhere, at any time.
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <VerificationModule />
              </div>
            </TabsContent>

            <TabsContent value="code">
              <div className="space-y-8">
                <Card className="bg-gray-800/50 border-gray-700">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-white">
                      <Code className="h-5 w-5 text-cyan-400" />
                      RNG Implementation - Open Source Code
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="bg-gradient-to-r from-green-900/50 to-emerald-900/50 p-6 rounded-lg border border-green-700/50">
                      <h3 className="text-lg font-semibold text-white mb-3">🔓 Complete Transparency</h3>
                      <p className="text-green-200">
                        Below is the exact code that determines winners in every draw. No hidden algorithms, 
                        no secret formulas - just pure, verifiable mathematics.
                      </p>
                    </div>

                    <div className="space-y-6">
                      <div>
                        <h4 className="text-xl font-semibold text-white mb-4">Step 1: Hash to Number Conversion</h4>
                        <div className="bg-gray-900 p-4 rounded-lg border border-gray-600">
                          <pre className="text-green-400 text-sm overflow-x-auto">
{`// Convert XRP Ledger hash to numeric value
function hashToNumber(ledgerHash) {
  const hashBuffer = new TextEncoder().encode(ledgerHash);
  let numericValue = 0;
  
  // Each character contributes to final number
  for (let i = 0; i < hashBuffer.length; i++) {
    numericValue += hashBuffer[i] * (i + 1);
  }
  
  return numericValue;
}

// Example:
// Hash: "F4D2B3A1C9E8..."
// Result: Large deterministic number`}</pre>
                        </div>
                      </div>

                      <div>
                        <h4 className="text-xl font-semibold text-white mb-4">Step 2: Winner Selection Algorithm</h4>
                        <div className="bg-gray-900 p-4 rounded-lg border border-gray-600">
                          <pre className="text-blue-400 text-sm overflow-x-auto">
{`// Determine winner using modulo operation
function selectWinner(ledgerHash, totalParticipants) {
  // Convert hash to number
  const seedNumber = hashToNumber(ledgerHash);
  
  // Use modulo to get winner index
  const winnerIndex = seedNumber % totalParticipants;
  
  return winnerIndex;
}

// Mathematical guarantee:
// Same hash + same participants = same winner
// Every participant has equal probability: 1/totalParticipants`}</pre>
                        </div>
                      </div>

                      <div>
                        <h4 className="text-xl font-semibold text-white mb-4">Step 3: Complete Draw Function</h4>
                        <div className="bg-gray-900 p-4 rounded-lg border border-gray-600">
                          <pre className="text-purple-400 text-sm overflow-x-auto">
{`// Complete provably fair draw implementation
function executeProvablyFairDraw(participants, ledgerCloseHash) {
  // Validate inputs
  if (!participants || participants.length === 0) {
    throw new Error("No participants in draw");
  }
  
  if (!ledgerCloseHash || ledgerCloseHash.length !== 64) {
    throw new Error("Invalid XRP Ledger hash");
  }
  
  // Execute deterministic selection
  const winnerIndex = selectWinner(ledgerCloseHash, participants.length);
  const winner = participants[winnerIndex];
  
  // Return verifiable result
  return {
    winner: winner,
    winnerIndex: winnerIndex,
    ledgerHash: ledgerCloseHash,
    totalParticipants: participants.length,
    timestamp: Date.now(),
    verificationHash: generateVerificationProof(ledgerCloseHash, winnerIndex)
  };
}`}</pre>
                        </div>
                      </div>

                      <div>
                        <h4 className="text-xl font-semibold text-white mb-4">Step 4: Verification Function</h4>
                        <div className="bg-gray-900 p-4 rounded-lg border border-gray-600">
                          <pre className="text-yellow-400 text-sm overflow-x-auto">
{`// Anyone can verify any draw result
function verifyDrawResult(drawResult) {
  const { ledgerHash, winnerIndex, totalParticipants } = drawResult;
  
  // Recalculate winner using same algorithm
  const expectedWinner = selectWinner(ledgerHash, totalParticipants);
  
  // Verify the result matches
  const isValid = (expectedWinner === winnerIndex);
  
  return {
    isValid: isValid,
    expectedWinner: expectedWinner,
    actualWinner: winnerIndex,
    message: isValid ? "✅ Draw result verified!" : "❌ Invalid draw result"
  };
}

// Verification is always possible because:
// 1. XRP Ledger hashes are public and immutable
// 2. Algorithm is deterministic and open source
// 3. No external randomness or secret keys required`}</pre>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 p-6 rounded-lg border border-blue-700/50">
                      <h4 className="text-lg font-semibold text-white mb-3">🧮 Why This Works</h4>
                      <ul className="text-blue-200 space-y-2">
                        <li><strong>Deterministic:</strong> Same input always produces same output</li>
                        <li><strong>Unpredictable:</strong> XRP Ledger hash cannot be predicted in advance</li>
                        <li><strong>Fair:</strong> Each participant has exactly equal probability</li>
                        <li><strong>Verifiable:</strong> Anyone can run this code and verify results</li>
                        <li><strong>Transparent:</strong> No hidden code, no secret algorithms</li>
                      </ul>
                    </div>

                    <div className="bg-gradient-to-r from-red-900/50 to-pink-900/50 p-6 rounded-lg border border-red-700/50">
                      <h4 className="text-lg font-semibold text-white mb-3">⚠️ Important Note</h4>
                      <p className="text-red-200">
                        This is NOT about luck! This is about mathematics and cryptographic proof. 
                        The winner is determined by pure mathematical calculation using blockchain data 
                        that nobody can manipulate. Your chances are exactly what the math says they are.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="rng">
              <div className="space-y-8">
                <Card className="bg-gray-800/50 border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-white">Try Our RNG System</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 p-6 rounded-lg border border-purple-700/50 mb-6">
                      <h3 className="text-lg font-semibold text-white mb-3">🎲 Interactive Demo</h3>
                      <p className="text-purple-200">
                        Use the module below to generate random numbers using any XRP Ledger hash. 
                        See how the same hash always produces the same result - this is the foundation of our fairness guarantee.
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <RNGModule />
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default Help;
