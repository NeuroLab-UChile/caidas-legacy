import React from "react";
import { StyleSheet, View } from "react-native";
import { theme } from "@/src/theme";

interface ScrollLayoutProps {
  children: React.ReactNode;
}

export function ScrollLayout({ children }: ScrollLayoutProps) {
  return <View style={styles.container}>{children}</View>;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
});
