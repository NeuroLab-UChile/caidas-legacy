import { DefaultTheme } from '@react-navigation/native';

// Paleta de colores base
const palette = {
  primary: '#F2FF2A',      // Amarillo brillante
  secondary: '#FFD700',    // Dorado
  background: '#FFFFFF',   // Blanco
  surface: '#FFFFFF',      // Blanco para superficies
  accent: '#000000',      // Negro
  error: '#FF3B30',       // Rojo para errores
  warning: '#FF9500',     // Naranja para advertencias
  success: '#34C759',     // Verde para éxito
  info: '#007AFF',        // Azul para información

  // Variaciones de grises
  grey: {
    100: '#F5F5F5',
    200: '#EEEEEE',
    300: '#E0E0E0',
    400: '#BDBDBD',
    500: '#9E9E9E',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
  },

  // Variaciones de transparencia
  alpha: {
    light: 'rgba(255, 255, 255, 0.7)',
    dark: 'rgba(0, 0, 0, 0.7)',
  },
} as const;

// Sistema tipográfico extendido
const typography = {
  fonts: {
    primary: {
      light: 'Roboto-Light',
      regular: 'Roboto-Regular',
      medium: 'Roboto-Medium',
      bold: 'Roboto-Bold',
      black: 'Roboto-Black',
    },
    secondary: {
      regular: 'RobotoMono-Regular',
      medium: 'RobotoMono-Medium',
      bold: 'RobotoMono-Bold',
    },
  },
  sizes: {
    display1: 36,
    display2: 32,
    display3: 28,
    headline1: 24,
    headline2: 22,
    title: 20,
    subtitle: 18,
    body1: 16,
    body2: 14,
    caption: 12,
    small: 10,
  },
  lineHeights: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
  },
  // Estilos de texto predefinidos
  styles: {
    display1: {
      fontFamily: 'Roboto-Bold',
      fontSize: 36,
      lineHeight: 1.2,
      letterSpacing: -0.5,
    },
    display2: {
      fontFamily: 'Roboto-Bold',
      fontSize: 32,
      lineHeight: 1.2,
      letterSpacing: -0.5,
    },
    display3: {
      fontFamily: 'Roboto-Bold',
      fontSize: 28,
      lineHeight: 1.2,
    },
    headline1: {
      fontFamily: 'Roboto-Bold',
      fontSize: 24,
      lineHeight: 1.3,
    },
    headline2: {
      fontFamily: 'Roboto-Medium',
      fontSize: 22,
      lineHeight: 1.35,
    },
    title1: {
      fontFamily: 'Roboto-Medium',
      fontSize: 20,
      lineHeight: 1.4,
    },
    title2: {
      fontFamily: 'Roboto-Medium',
      fontSize: 18,
      lineHeight: 1.4,
    },
    subtitle1: {
      fontFamily: 'Roboto-Medium',
      fontSize: 16,
      lineHeight: 1.5,
      letterSpacing: 0.15,
    },
    subtitle2: {
      fontFamily: 'Roboto-Medium',
      fontSize: 14,
      lineHeight: 1.5,
      letterSpacing: 0.1,
    },
    body1: {
      fontFamily: 'Roboto-Regular',
      fontSize: 16,
      lineHeight: 1.5,
      letterSpacing: 0.5,
    },
    body2: {
      fontFamily: 'Roboto-Regular',
      fontSize: 14,
      lineHeight: 1.5,
      letterSpacing: 0.25,
    },
    button: {
      fontFamily: 'Roboto-Medium',
      fontSize: 14,
      lineHeight: 1.75,
      letterSpacing: 0.4,
      textTransform: 'uppercase',
    },
    caption: {
      fontFamily: 'Roboto-Regular',
      fontSize: 12,
      lineHeight: 1.66,
      letterSpacing: 0.4,
    },
    overline: {
      fontFamily: 'Roboto-Medium',
      fontSize: 10,
      lineHeight: 1.6,
      letterSpacing: 1.5,
      textTransform: 'uppercase',
    },
    // Variantes adicionales
    mono: {
      fontFamily: 'RobotoMono-Regular',
      fontSize: 14,
      lineHeight: 1.5,
    },
    monoBold: {
      fontFamily: 'RobotoMono-Bold',
      fontSize: 14,
      lineHeight: 1.5,
    },
    link: {
      fontFamily: 'Roboto-Medium',
      fontSize: 16,
      lineHeight: 1.5,
      textDecorationLine: 'underline',
    },
    error: {
      fontFamily: 'Roboto-Regular',
      fontSize: 12,
      lineHeight: 1.66,
      color: palette.error,
    },
    success: {
      fontFamily: 'Roboto-Regular',
      fontSize: 12,
      lineHeight: 1.66,
      color: palette.success,
    },
  },
} as const;

// Sistema de espaciado
const spacing = {
  xxs: 2,
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64,
} as const;

// Tema principal
export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#F2FF2A',      // Amarillo brillante
    background: '#FFFFFF',   // Blanco
    surface: '#FFFFFF',      // Blanco para superficies
    text: '#000000',        // Negro para texto general
    textSecondary: '#000000', // Negro para texto secundario
    textTertiary: '#000000',  // Negro para texto terciario
    border: '#E0E0E0',      // Gris claro
    error: '#FF3B30',       // Rojo para errores
    success: '#34C759',     // Verde para éxito
    warning: '#FF9500',     // Naranja para advertencias
    disabled: '#000000',    // Negro para texto deshabilitado
    placeholder: '#000000',  // Negro para placeholder
  },
  typography: {
    ...typography,
    styles: {
      ...typography.styles,
      button: {
        ...typography.styles.button,
        color: '#000000',  // Negro para texto de botones
      },
      body1: {
        ...typography.styles.body1,
        color: '#000000',  // Negro para texto principal
      },
      body2: {
        ...typography.styles.body2,
        color: '#000000',  // Negro para texto secundario
      },
      caption: {
        ...typography.styles.caption,
        color: '#000000',  // Negro para texto pequeño
      },
    },
  },
  spacing,

  // Sistema de bordes y sombras
  shape: {
    borderRadius: {
      none: 0,
      xs: 2,
      sm: 4,
      md: 8,
      lg: 12,
      xl: 16,
      full: 9999,
    },
    borderWidth: {
      none: 0,
      thin: 1,
      medium: 2,
      thick: 4,
    },
  },

  // Efectos y animaciones
  animation: {
    duration: {
      shortest: 150,
      shorter: 200,
      short: 250,
      standard: 300,
      complex: 375,
      enteringScreen: 225,
      leavingScreen: 195,
    },
    easing: {
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
    },
  },

  // Componentes predefinidos
  components: {
    button: {
      variants: {
        primary: {
          backgroundColor: palette.primary,
          textColor: palette.accent,
          borderRadius: 12,
          borderWidth: 1,
          borderColor: palette.accent,
          paddingVertical: spacing.md,
          paddingHorizontal: spacing.lg,
        },
        secondary: {
          backgroundColor: palette.background,
          textColor: palette.accent,
          borderRadius: 12,
          borderWidth: 1,
          borderColor: palette.accent,
        },
        text: {
          backgroundColor: 'transparent',
          textColor: palette.accent,
        },
      },
      sizes: {
        small: {
          height: 32,
          paddingHorizontal: spacing.sm,
          fontSize: typography.sizes.body2,
        },
        medium: {
          height: 40,
          paddingHorizontal: spacing.md,
          fontSize: typography.sizes.body1,
        },
        large: {
          height: 48,
          paddingHorizontal: spacing.lg,
          fontSize: typography.sizes.subtitle,
        },
      },
    },

    card: {
      variants: {
        elevated: {
          backgroundColor: palette.surface,
          borderRadius: 12,
          shadowColor: palette.accent,
          shadowOffset: { width: 0, height: 2 },
          shadowOpacity: 0.25,
          shadowRadius: 3.84,
          elevation: 6,
          padding: spacing.md,
        },
        outlined: {
          backgroundColor: palette.surface,
          borderRadius: 12,
          borderWidth: 1,
          borderColor: palette.grey[300],
          padding: spacing.md,
        },
      },
    },

    input: {
      default: {
        backgroundColor: palette.surface,
        borderColor: palette.grey[300],
        borderWidth: 1,
        borderRadius: 8,
        padding: spacing.md,
        fontSize: typography.sizes.body1,
        color: palette.accent,
      },
      focused: {
        borderColor: palette.primary,
        shadowColor: palette.primary,
        shadowOpacity: 0.2,
        shadowRadius: 4,
      },
      error: {
        borderColor: palette.error,
        shadowColor: palette.error,
      },
    },

    navigation: {
      header: {
        backgroundColor: palette.primary,
        titleColor: palette.accent,
        titleSize: typography.sizes.headline2,
        height: 56,
        elevation: 4,
      },
      bottomTab: {
        backgroundColor: palette.background,
        activeColor: palette.primary,
        inactiveColor: palette.grey[600],
        height: 56,
        labelSize: typography.sizes.caption,
        iconSize: 24,
      },
    },

    activityNode: {
      container: {
        flex: 1,
        backgroundColor: '#FFFFFF',
        padding: 16,
      },
      question: {
        fontSize: 18,
        color: '#000000',
        marginBottom: 16,
      },
      option: {
        backgroundColor: '#FFFFFF',
        padding: 16,
        borderRadius: 8,
        borderWidth: 1,
        borderColor: '#E0E0E0',
        marginBottom: 12,
        flexDirection: 'row',
        alignItems: 'center',
      },
      optionText: {
        fontSize: 16,
        color: '#000000',
        flex: 1,
        marginLeft: 12,
      },
      selectedOption: {
        backgroundColor: '#F2FF2A20',
        borderColor: '#F2FF2A',
        borderWidth: 2,
      },
      button: {
        backgroundColor: '#F2FF2A',
        padding: 16,
        borderRadius: 8,
        alignItems: 'center',
        marginTop: 16,
      },
      buttonText: {
        fontSize: 16,
        color: '#000000',
        fontWeight: '600',
      },
      input: {
        borderWidth: 1,
        borderColor: '#E0E0E0',
        borderRadius: 8,
        padding: 12,
        color: '#000000',
        backgroundColor: '#FFFFFF',
      },
    },
  },
} as const;

// Type safety
export type Theme = typeof theme;

// Utilidades de tema
export const getSpacing = (value: keyof typeof spacing) => spacing[value];
export const getColor = (value: keyof typeof palette) => palette[value];
export const getFontSize = (value: keyof typeof typography.sizes) => typography.sizes[value];

// Componente de texto predefinido
export const TextPresets = {
  default: typography.styles.body1,
  title: typography.styles.title1,
  subtitle: typography.styles.subtitle1,
  body: typography.styles.body1,
  caption: typography.styles.caption,
  button: typography.styles.button,
  link: typography.styles.link,
  error: typography.styles.error,
  success: typography.styles.success,
} as const;