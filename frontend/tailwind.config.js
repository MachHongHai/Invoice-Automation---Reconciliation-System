/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        navy: {
          50: '#f0f7fa',
          100: '#dbeff5',
          200: '#bce0eb',
          300: '#8ccbdc',
          400: '#56adcb',
          500: '#3a91b0',
          600: '#2f7593',
          700: '#2a607a',
          800: '#275167',
          900: '#244558',
          950: '#152936',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
