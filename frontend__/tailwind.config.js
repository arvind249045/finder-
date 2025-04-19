module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        poppins: ['Poppins', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
        spacemono: ['Space Mono', 'monospace'],
      },
      colors: {
        coral: '#FF6B6B',
        navy: '#1A1A40',
        cyan: '#00F5FF',
        lightgray: '#F8FAFC',
        graybg: '#E2E8F0',
      },
      backgroundImage: {
        'gradient-soft': 'linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)',
        'hero-gradient': 'linear-gradient(120deg, rgba(255,107,107,0.2) 0%, rgba(26,26,64,0.8) 100%)',
        'footer-gradient': 'linear-gradient(90deg, #FF6B6B 0%, #1A1A40 100%)',
      },
      boxShadow: {
        glass: '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
        neon: '0 0 12px #00F5FF',
      },
    },
  },
  plugins: [],
}
