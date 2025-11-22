/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './frontend/index.html',
    './frontend/js/**/*.js',
    './templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4285F4',
        danger: '#DB4437',
        warning: '#F4B400',
        success: '#0F9D58',
        gray: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  safelist: [
    'bg-primary', 'text-primary', 'border-primary',
    'bg-success', 'text-success',
    'bg-danger', 'text-danger',
    'bg-warning', 'text-warning',
    'animate-pulse', 'hidden', 'block', 'flex', 'grid',
    {
      pattern: /dark:(bg|text|border|divide|hover)-.*/,
    },
  ],
};
