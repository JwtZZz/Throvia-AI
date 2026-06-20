import { useEffect, useState } from "react";

import ChatPanel from "@/components/chat/ChatPanel";
import { FlickeringGrid } from "@/components/ui/flickering-grid";

function usePrefersReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) {
      return undefined;
    }

    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const handleChange = () => {
      setPrefersReducedMotion(mediaQuery.matches);
    };

    handleChange();
    mediaQuery.addEventListener("change", handleChange);

    return () => {
      mediaQuery.removeEventListener("change", handleChange);
    };
  }, []);

  return prefersReducedMotion;
}

export default function ResearchDashboard({ className = "" }) {
  const prefersReducedMotion = usePrefersReducedMotion();

  return (
    <main className={`relative min-h-screen overflow-hidden bg-[#F8F5ED] text-[#1F1F1D] ${className}`}>
      <div className="absolute inset-0 z-0 bg-[#F8F5ED]" />

      <section className="relative z-10 min-h-screen pb-3 pl-[10px] pr-0 pt-6 sm:pb-4 sm:pl-[10px] sm:pt-8 lg:pb-4 lg:pl-[10px] lg:pt-10">
        <div className="flex min-h-[calc(100vh-32px)] w-full justify-start">
          <div className="w-full max-w-[500px]">
            <ChatPanel />
          </div>
        </div>
      </section>

      {!prefersReducedMotion && (
        <div className="pointer-events-none absolute inset-0 z-20 opacity-[0.12] md:opacity-[0.16]">
          <FlickeringGrid
            className="h-full w-full"
            squareSize={12}
            gridGap={16}
            flickerChance={0.14}
            color="#5D6B2F"
            maxOpacity={0.42}
          />
        </div>
      )}
    </main>
  );
}
