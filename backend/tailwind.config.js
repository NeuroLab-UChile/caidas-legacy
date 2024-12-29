module.exports = {
  content: [
    "./prevcad/templates/**/*.html",
    "./prevcad/static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#FFCC00',
        'primary-light': '#FFE066',
        'primary-dark': '#E6B800',
        secondary: '#333333',
        light: {
          bg: {
            primary: '#FFFFFF',
            secondary: '#F3F4F6',
            tertiary: '#F9FAFB',
          },
          text: {
            primary: '#111827',
            secondary: '#374151',
            tertiary: '#6B7280',
          },
          border: {
            primary: '#E5E7EB',
            secondary: '#D1D5DB',
          }
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
      },
      boxShadow: {
        'soft': '0 2px 4px rgba(0,0,0,0.05)',
        'medium': '0 4px 6px rgba(0,0,0,0.07)',
      }
    },
  },
  plugins: [],
}
