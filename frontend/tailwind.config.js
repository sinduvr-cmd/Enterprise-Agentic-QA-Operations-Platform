/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          sidebar: '#08231c',
          sidebarLight: '#0d2e26',
          sidebarHover: '#123d32',
          sidebarActive: '#15473a',
          sidebarBorder: '#1c5446',
          mint: '#34d399',
          emeraldBtn: '#0b382d',
          emeraldBtnHover: '#0f4639',
          bgLight: '#f6f8f6',
          borderLight: '#e4eae4',
        }
      }
    },
  },
  plugins: [],
}
