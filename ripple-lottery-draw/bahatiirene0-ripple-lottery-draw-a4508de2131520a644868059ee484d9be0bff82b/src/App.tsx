
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import About from "./pages/About";
import Help from "./pages/Help";
import NotFound from "./pages/NotFound";
import Roulette from "./pages/Roulette";
import DreamCatcher from "./pages/DreamCatcher";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/about" element={<About />} />
          <Route path="/help" element={<Help />} />
          <Route path="/roulette" element={<Roulette />} />
          <Route path="/dreamcatcher" element={<DreamCatcher />} />
          <Route path="/roadmap" element={<div className="min-h-screen bg-gray-900 text-white flex items-center justify-center"><h1>Roadmap - Coming Soon</h1></div>} />
          <Route path="/integrations" element={<div className="min-h-screen bg-gray-900 text-white flex items-center justify-center"><h1>Integrations - Coming Soon</h1></div>} />
          <Route path="/faq" element={<div className="min-h-screen bg-gray-900 text-white flex items-center justify-center"><h1>FAQ - Coming Soon</h1></div>} />
          <Route path="/terms" element={<div className="min-h-screen bg-gray-900 text-white flex items-center justify-center"><h1>Terms - Coming Soon</h1></div>} />
          <Route path="/privacy" element={<div className="min-h-screen bg-gray-900 text-white flex items-center justify-center"><h1>Privacy Policy - Coming Soon</h1></div>} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
