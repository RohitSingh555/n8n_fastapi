/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0c0d0f',
        surface: 'rgba(255, 255, 255, 0.05)',
        primary: '#4a9eff',
        secondary: 'rgba(255, 255, 255, 0.1)',
        border: 'rgba(255, 255, 255, 0.2)',
        text: {
          primary: '#ffffff',
          secondary: '#e0e0e0',
          muted: 'rgba(255, 255, 255, 0.5)'
        }
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
} 