import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '@/src/theme';

interface StepIndicatorProps {
  current: number;
  total: number;
}

export const StepIndicator: React.FC<StepIndicatorProps> = ({ current, total }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>
        Paso <Text style={styles.current}>{current}</Text> de {total}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.primaryDark,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignSelf: 'center',
  },
  text: {
    color: theme.colors.background,
    fontSize: 14,
    fontWeight: '600',
  },
  current: {
    fontWeight: '700',
  },
}); 