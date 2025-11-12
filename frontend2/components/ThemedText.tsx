import { Text, type TextProps, StyleSheet } from 'react-native';
import { theme } from "@/src/theme";
import { useThemeColor } from '@/hooks/useThemeColor';

export type ThemedTextProps = TextProps & {
  lightColor?: string;
  darkColor?: string;
  type?: 'default' | 'title' | 'defaultSemiBold' | 'subtitle' | 'link';
};

export function ThemedText({
  style,
  lightColor,
  darkColor,
  type = 'default',
  ...rest
}: ThemedTextProps) {
  const color = useThemeColor({ light: lightColor, dark: darkColor }, 'text');

  return (
    <Text
      style={[
        { color },
        type === 'default' ? styles.default : undefined,
        type === 'title' ? styles.title : undefined,
        type === 'defaultSemiBold' ? styles.defaultSemiBold : undefined,
        type === 'subtitle' ? styles.subtitle : undefined,
        type === 'link' ? styles.link : undefined,
        style,
      ]}
      {...rest}
    />
  );
}

const styles = StyleSheet.create({
  default: {
    fontSize: theme.typography.sizes.body1,
    lineHeight: theme.typography.sizes.subtitle,
  },
  defaultSemiBold: {
    fontSize: theme.typography.sizes.body1,
    lineHeight: theme.typography.sizes.subtitle,
    fontWeight: '600',
  },
  title: {
    fontSize: theme.typography.sizes.display2,
    fontWeight: 'bold',
    lineHeight: 32,
  },
  subtitle: {
    fontSize: theme.typography.sizes.title,
    fontWeight: 'bold',
  },
  link: {
    lineHeight: 30,
    fontSize: theme.typography.sizes.body1,
    color: '#0a7ea4',
  },
});
