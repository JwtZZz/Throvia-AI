import { RippleButton } from "@/components/ui/ripple-button";

const variantPositions = {
  0: "0% 0%",
  1: "100% 0%",
  2: "0% 100%",
  3: "100% 100%",
};

const flowerPlacements = [
  { variant: 0, size: 150, top: "-2%", left: "2%", rotate: -12, opacity: 0.9, motion: "floating-flower", duration: "14s", delay: "-5s", floatDistance: "12px" },
  { variant: 1, size: 130, top: "3%", right: "8%", rotate: 10, opacity: 0.75, motion: "floating-flower", duration: "16s", delay: "-9s", floatDistance: "10px" },
  { variant: 2, size: 160, bottom: "2%", left: "3%", rotate: 8, opacity: 0.85, motion: "floating-flower", duration: "15s", delay: "-11s", floatDistance: "14px" },
  { variant: 3, size: 150, bottom: "3%", right: "5%", rotate: -8, opacity: 0.85, motion: "floating-flower", duration: "13s", delay: "-7s", floatDistance: "11px" },
  { variant: 0, size: 90, top: "28%", left: "-2%", rotate: 18, opacity: 0.45, hideOnMobile: true, motion: "breathing-flower", duration: "10s", delay: "-6s", floatDistance: "6px" },
  { variant: 1, size: 90, top: "30%", right: "-2%", rotate: -18, opacity: 0.45, hideOnMobile: true, motion: "breathing-flower", duration: "11s", delay: "-8s", floatDistance: "6px" },
  { variant: 2, size: 80, bottom: "18%", left: "14%", rotate: -6, opacity: 0.35, hideOnMobile: true, motion: "breathing-flower", duration: "9s", delay: "-4s", floatDistance: "6px" },
  { variant: 3, size: 80, bottom: "18%", right: "14%", rotate: 6, opacity: 0.35, hideOnMobile: true, motion: "breathing-flower", duration: "12s", delay: "-10s", floatDistance: "7px" },
  { variant: 0, size: 70, top: "8%", left: "42%", rotate: 4, opacity: 0.35, hideOnMobile: true, motion: "breathing-flower", duration: "8.5s", delay: "-3s", floatDistance: "6px" },
  { variant: 1, size: 70, bottom: "6%", left: "48%", rotate: -4, opacity: 0.35, hideOnMobile: true, motion: "breathing-flower", duration: "10.5s", delay: "-7s", floatDistance: "6px" },
];

const dotPlacements = [
  { top: "3%", left: "4%", size: 14, color: "#c8d157", duration: "14s", delay: "-2s", floatDistance: "7px" },
  { top: "14%", left: "23%", size: 12, color: "#d8d349", hideOnMobile: true, duration: "18s", delay: "-11s", floatDistance: "8px" },
  { top: "4%", left: "40%", size: 14, color: "#b6c745", hideOnMobile: true, duration: "16s", delay: "-6s", floatDistance: "7px" },
  { top: "6%", left: "53%", size: 10, color: "#e0d84d", hideOnMobile: true, duration: "21s", delay: "-15s", floatDistance: "8px" },
  { top: "5%", right: "28%", size: 14, color: "#b6c745", hideOnMobile: true, duration: "17s", delay: "-10s", floatDistance: "8px" },
  { top: "13%", right: "16%", size: 16, color: "#e0d84d", duration: "12s", delay: "-4s", floatDistance: "7px" },
  { top: "2%", right: "4%", size: 14, color: "#c8d157", duration: "20s", delay: "-12s", floatDistance: "8px" },
  { top: "31%", left: "2%", size: 16, color: "#c8d157", duration: "13s", delay: "-5s", floatDistance: "7px" },
  { top: "43%", left: "11%", size: 14, color: "#e0d84d", hideOnMobile: true, duration: "19s", delay: "-8s", floatDistance: "8px" },
  { top: "38%", right: "6%", size: 16, color: "#b6c745", duration: "15s", delay: "-9s", floatDistance: "7px" },
  { top: "46%", right: "2.5%", size: 12, color: "#d8d349", hideOnMobile: true, duration: "22s", delay: "-16s", floatDistance: "8px" },
  { bottom: "27%", left: "2.5%", size: 18, color: "#d8d349", duration: "14s", delay: "-7s", floatDistance: "7px" },
  { bottom: "18%", left: "18%", size: 16, color: "#b6c745", hideOnMobile: true, duration: "16s", delay: "-13s", floatDistance: "8px" },
  { bottom: "8%", left: "22%", size: 16, color: "#e0d84d", hideOnMobile: true, duration: "20s", delay: "-14s", floatDistance: "8px" },
  { bottom: "1.5%", left: "27%", size: 14, color: "#c8d157", hideOnMobile: true, duration: "18s", delay: "-9s", floatDistance: "7px" },
  { bottom: "8%", left: "46%", size: 12, color: "#b6c745", hideOnMobile: true, duration: "11s", delay: "-6s", floatDistance: "6px" },
  { bottom: "5%", right: "28%", size: 18, color: "#e0d84d", hideOnMobile: true, duration: "17s", delay: "-12s", floatDistance: "8px" },
  { bottom: "8%", right: "17%", size: 14, color: "#c8d157", duration: "13s", delay: "-4s", floatDistance: "7px" },
  { bottom: "21%", right: "6%", size: 16, color: "#b6c745", hideOnMobile: true, duration: "19s", delay: "-10s", floatDistance: "8px" },
  { bottom: "14%", right: "1.5%", size: 18, color: "#e0d84d", duration: "15s", delay: "-11s", floatDistance: "7px" },
];

function AvocadoFlowerSprite({ variant, size, className = "", style = {} }) {
  return (
    <div
      aria-hidden="true"
      className={`pointer-events-none ${className}`}
      style={{
        width: size,
        height: size,
        backgroundImage: "url('/附件.png')",
        backgroundSize: "200% 200%",
        backgroundPosition: variantPositions[variant],
        backgroundRepeat: "no-repeat",
        mixBlendMode: "multiply",
        filter: "drop-shadow(0 4px 10px rgba(111, 133, 40, 0.08))",
        ...style,
      }}
    />
  );
}

function FloatingFlowerBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 z-0 overflow-hidden [contain:layout_paint_style]">
      {flowerPlacements.map((flower, index) => (
        <AvocadoFlowerSprite
          key={`flower-${index}`}
          variant={flower.variant}
          size={flower.size}
          className={`absolute will-change-transform ${flower.motion} ${flower.hideOnMobile ? "hidden md:block" : "block"}`}
          style={{
            top: flower.top,
            right: flower.right,
            bottom: flower.bottom,
            left: flower.left,
            opacity: flower.opacity,
            "--rotate": `${flower.rotate}deg`,
            "--duration": flower.duration,
            "--delay": flower.delay,
            "--float-distance": flower.floatDistance,
          }}
        />
      ))}

      {dotPlacements.map((dot, index) => (
        <span
          key={`dot-${index}`}
          aria-hidden="true"
          className={`absolute rounded-full will-change-transform floating-dot ${dot.hideOnMobile ? "hidden md:block" : "block"}`}
          style={{
            top: dot.top,
            right: dot.right,
            bottom: dot.bottom,
            left: dot.left,
            width: dot.size,
            height: dot.size,
            backgroundColor: dot.color,
            opacity: 0.78,
            "--duration": dot.duration,
            "--delay": dot.delay,
            "--float-distance": dot.floatDistance,
          }}
        />
      ))}
    </div>
  );
}

function ProductStartButton() {
  return (
    <div className="group relative z-20">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-10 -bottom-3 h-10 rounded-full bg-[#b76e3e]/20 blur-2xl transition-all duration-500 ease-[cubic-bezier(0.22,1,0.36,1)] group-hover:opacity-100"
      />
      <RippleButton
        rippleColor="rgba(255,255,255,0.4)"
        duration="900ms"
        className="group relative inline-flex h-16 min-w-[13.5rem] items-center justify-center overflow-hidden rounded-[1.45rem] border border-[#d6a082]/25 px-12 text-[1.05rem] font-semibold tracking-[0.01em] text-white outline-none transition-all duration-500 ease-[cubic-bezier(0.22,1,0.36,1)] hover:-translate-y-1 hover:scale-[1.02] hover:shadow-[0_24px_48px_rgba(168,95,43,0.24),inset_0_1px_0_rgba(255,255,255,0.25)] active:translate-y-0 active:scale-[0.985] focus-visible:ring-4 focus-visible:ring-[#d6b195]/30 before:pointer-events-none before:absolute before:inset-0 before:rounded-[inherit] before:bg-[radial-gradient(circle_at_50%_0%,rgba(255,250,245,0.2),transparent_56%)] after:pointer-events-none after:absolute after:-left-[35%] after:top-0 after:h-full after:w-[24%] after:-skew-x-[22deg] after:bg-gradient-to-r after:from-transparent after:via-white/30 after:to-transparent after:transition-transform after:duration-700 after:ease-[cubic-bezier(0.22,1,0.36,1)] hover:after:translate-x-[560%]"
        style={{
          background:
            "linear-gradient(135deg, #C8793E 0%, #B96E3A 48%, #A85F2B 100%)",
          boxShadow:
            "0 18px 40px rgba(168, 95, 43, 0.22), inset 0 1px 0 rgba(255,255,255,0.25)",
        }}
      >
        <span className="relative flex items-center gap-3">
          <span>Start</span>
          <span className="text-[1.05rem] transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)] group-hover:translate-x-1">
            →
          </span>
        </span>
      </RippleButton>
    </div>
  );
}

function StartScreen() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#F8F5ED] font-body">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 z-0 bg-[radial-gradient(circle_at_center,rgba(234,227,213,0.45),transparent_52%)]"
      />
      <FloatingFlowerBackground />

      <section className="relative z-10 flex min-h-screen items-center justify-center px-6 py-10">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute h-44 w-44 rounded-full bg-[radial-gradient(circle,rgba(232,224,210,0.78),transparent_70%)] blur-3xl"
        />

        <div className="relative z-10 flex min-h-screen w-full -translate-y-[3vh] flex-col items-center justify-center px-6 text-center">
          <h1
            className="intro-reveal max-w-[900px] font-[Georgia,'Times_New_Roman',serif] text-[2.5rem] font-normal leading-[1.05] tracking-[-0.04em] text-[#1F1F1D] sm:text-[3.25rem] lg:text-[4rem]"
            style={{ animationDelay: "0ms" }}
          >
            A calmer way to understand the market.
          </h1>

          <p
            className="intro-reveal mt-6 max-w-[680px] text-base font-normal leading-[1.7] text-[#6F6A60] sm:text-[1.25rem]"
            style={{ animationDelay: "120ms" }}
          >
            Seven specialized agents turn scattered signals into thoughtful equity research.
          </p>

          <div
            className="intro-reveal mt-[42px]"
            style={{ animationDelay: "240ms" }}
          >
            <ProductStartButton />
          </div>
        </div>
      </section>
    </main>
  );
}

export default function App() {
  return <StartScreen />;
}
