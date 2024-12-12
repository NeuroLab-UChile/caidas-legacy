import React from "react";
import { Tabs } from "expo-router";
import {
  View,
  TouchableOpacity,
  Text,
  Platform,
  StyleSheet,
} from "react-native";
import { IconSymbol } from "@/components/ui/IconSymbol";
import { router } from "expo-router";
import { HapticTab } from "@/components/HapticTab";
import { theme } from "@/src/theme";

export default function TabLayout() {
  const handleMiddleButtonPress = () => {
    router.push("/(tabs)/action");
  };

  return (
    <View
      style={[styles.container, { backgroundColor: theme.colors.background }]}
    >
      <Tabs
        screenOptions={{
          tabBarActiveTintColor: theme.colors.primary,
          tabBarInactiveTintColor: theme.colors.text,
          headerShown: true,
          tabBarButton: HapticTab,
          headerStyle: {
            backgroundColor: theme.colors.primary,
            elevation: 0,
            shadowOpacity: 0,
          },
          headerTitleStyle: {
            color: theme.colors.text,
            fontSize: theme.typography.sizes.titleLarge,
            fontFamily: theme.typography.primary.fontFamily,
            fontWeight: theme.typography.primary.bold,
          },
          headerLeft: () => (
            <TouchableOpacity
              onPress={() => router.back()}
              style={styles.backButton}
            >
              <Text
                style={[styles.backButtonText, { color: theme.colors.text }]}
              >
                {"< Volver"}
              </Text>
            </TouchableOpacity>
          ),
          tabBarStyle: {
            ...styles.tabBar,
            backgroundColor: theme.colors.background,
            borderTopColor: theme.colors.border,
          },
          tabBarLabelStyle: {
            fontSize: theme.typography.sizes.bodySmall,
            fontFamily: theme.typography.primary.fontFamily,
            fontWeight: theme.typography.primary.bold,
          },
        }}
      >
        {menuItems.map((item, index) => (
          <Tabs.Screen
            key={item.name}
            name={item.name}
            options={{
              title: item.title,
              tabBarIcon: ({ color }) => (
                <IconSymbol
                  size={theme.components.icon.size}
                  name={item.icon as any}
                  color={color}
                />
              ),
              tabBarButton: index === 2 ? () => null : undefined,
            }}
          />
        ))}
      </Tabs>

      <TouchableOpacity
        onPress={handleMiddleButtonPress}
        style={[styles.middleButton, { backgroundColor: theme.colors.primary }]}
      >
        <Text style={[styles.logoText, { color: theme.colors.text }]}>UP</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  backButton: {
    marginLeft: 16,
    flexDirection: "row",
    alignItems: "center",
  },
  backButtonText: {
    fontSize: 18,
    fontWeight: "600",
  },
  tabBar: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: 60,
    elevation: 0,
    borderTopWidth: 1,
    shadowColor: "transparent",
  },
  middleButton: {
    position: "absolute",
    bottom: 30,
    alignSelf: "center",
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: "center",
    alignItems: "center",
    elevation: 5,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  logoText: {
    fontSize: 20,
    fontWeight: "bold",
  },
});

const menuItems = [
  {
    name: "remember",
    title: "RECORDAR",
    icon: "calendar",
  },
  {
    name: "evaluate",
    title: "EVALUAR",
    icon: "checkmark.square",
  },
  {
    name: "action",
    title: "PREIDAS",
    icon: "plus.circle",
  },
  {
    name: "train",
    title: "ENTRENAR",
    icon: "figure.walk",
  },
  {
    name: "profile",
    title: "MIS DATOS",
    icon: "person",
  },
];
