/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
    './apps/**/forms.py',
    './**/templatetags/**/*.py',
    './static/js/**/*.js',
    './apps/**/*.js',
  ],
  safelist: [
    'pb-12','pb-8','pb-16','md:pb-16',
    'mt-3','mt-2','mb-3','py-3',
    'h-8','h-12'
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#667eea',
          50: '#f5f7ff',
          100: '#ebefff',
          200: '#d6deff',
          300: '#b8c5ff',
          400: '#94a5ff',
          500: '#667eea',
          600: '#5566d3',
          700: '#4451b0',
          800: '#353e8d',
          900: '#2a3174',
        },
        secondary: {
          DEFAULT: '#764ba2',
          50: '#f9f5fc',
          100: '#f3ebf9',
          200: '#e7d7f3',
          300: '#d4b7e8',
          400: '#bb8ed9',
          500: '#764ba2',
          600: '#66418c',
          700: '#553675',
          800: '#452c5f',
          900: '#38244e',
        },
      },
      fontFamily: {
        sans: ['Segoe UI', 'Tahoma', 'Geneva', 'Verdana', 'sans-serif'],
      },
      spacing: {
        'sidebar': '280px',
        'topbar': '60px',
      },
      zIndex: {
        'sidebar': '1000',
        'topbar': '999',
        'mobile-toggle': '1001',
        'toast': '9999',
      },
    },
  },
  plugins: [],
}
