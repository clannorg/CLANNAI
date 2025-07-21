/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: '#016F33',
        secondary: '#1a1a1a',
        accent: '#333333',
        'gray': {
          800: '#1a1a1a',
          900: '#111111'
        }
      }
    }
  },
  plugins: []
}

