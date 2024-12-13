import { useTheme as useNavigationTheme } from "@react-navigation/native";
import { theme, Theme } from "../theme";

export function useCustomTheme(): Theme {
  const navigationTheme = useNavigationTheme();
  return theme;
} 