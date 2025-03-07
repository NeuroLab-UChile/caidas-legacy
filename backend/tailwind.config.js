module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./templates/admin/**/*.{js,css}",
    "./prevcad/**/templates/**/*.html",
    "./templates/**/*.{js,css}",
    "./prevcad/**/templates/**/*.{js,css}",
    "./prevcad/**/templates/**/*.html",
    "./prevcad/**/templates/**/*.{js,css}",
    "./prevcad/**/templates/**/*.html",
    "./prevcad/**/templates/**/*.{js,css}",
  ],
  theme: {
    extend: {
      colors: {
        admin: {
          primary: {
            50: '#F0F9FF',
            100: '#E0F2FE',
            500: '#0EA5E9',
            600: '#0284C7',
            700: '#0369A1'
          },
          error: {
            50: '#FEF2F2',
            100: '#FEE2E2',
            500: '#EF4444',
            600: '#DC2626'
          },
          success: {
            50: '#F0FDF4',
            100: '#DCFCE7',
            500: '#22C55E',
            600: '#16A34A'
          },
          warning: {
            50: '#FFFBEB',
            100: '#FEF3C7',
            500: '#F59E0B',
            600: '#D97706'
          },
          gray: {
            50: '#F9FAFB',
            100: '#F3F4F6',
            200: '#E5E7EB',
            300: '#D1D5DB',
            400: '#9CA3AF',
            500: '#6B7280',
            600: '#4B5563',
            700: '#374151'
          }
        }
      },
      spacing: {
        'admin': {
          'form': '1.5rem',
          'section': '2rem',
          'header': '4rem'
        }
      },
      borderRadius: {
        'admin': '0.5rem'
      },
      fontSize: {
        'admin': {
          'xs': '0.75rem',
          'sm': '0.875rem',
          'base': '1rem',
          'lg': '1.125rem',
          'xl': '1.25rem'
        }
      },
      boxShadow: {
        'admin': '0 1px 3px rgba(0, 0, 0, 0.1)',
        'admin-md': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'admin-lg': '0 10px 15px rgba(0, 0, 0, 0.1)'
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms')({
      strategy: 'class'
    })
  ],
  prefix: 'tw-',
  important: true,
  corePlugins: {
    preflight: false
  }
}
