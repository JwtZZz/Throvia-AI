/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#faf9f5",
        ink: "#141413",
        hairline: "#e6dfd8",
        avocado: {
          100: "#f4efbe",
          200: "#e7de8d",
          300: "#c8d157",
          400: "#99b037",
          500: "#6f8528",
          600: "#56691f"
        },
        pit: {
          400: "#bf7640",
          500: "#a65f31",
          600: "#82461f"
        }
      },
      boxShadow: {
        soft: "0 20px 60px rgba(61, 61, 58, 0.08)",
        glow: "0 18px 34px rgba(166, 95, 49, 0.2)"
      },
      fontFamily: {
        display: ['"Iowan Old Style"', '"Palatino Linotype"', '"Book Antiqua"', "serif"],
        body: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"]
      }
    }
  },
  plugins: []
};
