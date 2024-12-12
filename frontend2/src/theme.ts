import { DefaultTheme } from '@react-navigation/native';

// Colores base
const palette = {
  primary: '#F2FF2A',     // Amarillo brillante
  background: '#FFFFFF',   // Blanco
  card: '#FFFFFF',        // Blanco
  accent: '#000000',      // Negro
  button: '#000000',      // Negro
} as const;

// Tipografía
const typography = {
  primary: {
    fontFamily: 'Roboto',    // Asegúrate de tener estas fuentes cargadas
    regular: '400',
    bold: '700',
    italic: 'italic',
  },
  secondary: {
    fontFamily: 'RobotoMono',
    regular: '400',
    bold: '700',
  },
  sizes: {
    displayLarge: 28,
    titleLarge: 22,
    bodyMedium: 16,
    displaySmall: 20,
    labelLarge: 16,
    bodySmall: 12
  },
} as const;

// Tema principal
export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: palette.primary,
    background: palette.background,
    card: palette.card,
    text: palette.accent,
    border: palette.accent,
  },
  typography,
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
  roundness: {
    small: 4,
    medium: 8,
    large: 12,
  },
  components: {
    button: {
      borderRadius: 12,
      borderWidth: 1,
      borderColor: palette.accent,
      backgroundColor: palette.background,
      textColor: palette.button,
    },
    card: {
      backgroundColor: palette.card,
      borderRadius: 12,
      shadowColor: 'rgba(0, 0, 0, 0.38)',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.25,
      shadowRadius: 3.84,
      elevation: 6,
    },
    appBar: {
      backgroundColor: palette.primary,
      titleColor: palette.accent,
      titleSize: 24,
      iconSize: 30,
      iconColor: palette.accent,
    },
    bottomTab: {
      backgroundColor: palette.background,
      activeColor: palette.primary,
      inactiveColor: palette.accent,
      labelSize: typography.sizes.labelLarge,
    },
    icon: {
      size: 30,
      color: palette.accent,
    },
  },
} as const;

// Type safety
export type Theme = typeof theme;

