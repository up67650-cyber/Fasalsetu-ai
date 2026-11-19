/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        forest: '#123c2d',
        leaf: '#39885a',
        lime: '#d9ee7a',
        cream: '#f6f7f1',
        ink: '#17251f',
        muted: '#718078'
      },
      fontFamily: {
        sans: ['DM Sans', 'sans-serif'],
        display: ['Manrope', 'sans-serif']
      },
      boxShadow: {
        card: '0 12px 40px rgba(20, 52, 39, 0.06)'
      }
    }
  },
  plugins: []
}
