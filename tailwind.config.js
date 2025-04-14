/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        'brand-blue': '#1e3a8a',
      },
      boxShadow: {
        'soft': '0 4px 20px rgba(0, 0, 0, 0.2)',
      },
    },
  },
  darkMode: 'class', // or 'media'
  plugins: [],
};
