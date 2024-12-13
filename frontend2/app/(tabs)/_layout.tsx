import React from "react";
import { Tabs } from "expo-router";
import {
  View,
  TouchableOpacity,
  Text,
  StyleSheet,
  Dimensions,
} from "react-native";
import { IconSymbol } from "@/components/ui/IconSymbol";
import { router } from "expo-router";
import { HapticTab } from "@/components/HapticTab";
import { theme } from "@/src/theme";

const BOTTOM_TAB_HEIGHT = 83;
const MIDDLE_BUTTON_SIZE = 65;
const { width } = Dimensions.get("window");
const SCREEN_WIDTH = width * 0.95;

const leftMenuItems = [
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
];

const rightMenuItems = [
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

const hiddenItems = [
  {
    name: "action",
    title: "PREIDAS",
    icon: "plus.circle",
    hidden: true,
  },
  {
    name: "category-detail",
    title: "Detalle",
    icon: "info.circle",
    hidden: true,
  },
];

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
          tabBarActiveTintColor: theme.colors.text,
          tabBarInactiveTintColor: "#000000",
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
              onPress={() => router.replace("/(tabs)/action")}
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
            backgroundColor: theme.colors.card,
          },
          tabBarItemStyle: {
            width: SCREEN_WIDTH / 4 - 10,
          },
          tabBarLabelStyle: {
            fontSize: 11,
            fontFamily: theme.typography.primary.fontFamily,
            fontWeight: theme.typography.primary.bold,
            paddingBottom: 15,
          },
          tabBarIconStyle: {
            marginTop: 15,
          },
        }}
      >
        {leftMenuItems.map((item) => (
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
            }}
          />
        ))}

        {hiddenItems.map((item) => (
          <Tabs.Screen
            key={item.name}
            name={item.name}
            options={{
              title: item.title,
              tabBarLabel: "",
              tabBarButton: () => null,
            }}
          />
        ))}

        {rightMenuItems.map((item) => (
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
            }}
          />
        ))}
      </Tabs>

      <TouchableOpacity
        onPress={handleMiddleButtonPress}
        style={[styles.middleButton, { backgroundColor: theme.colors.primary }]}
      >
        <IconSymbol
          name="figure.walk"
          size={24}
          color={theme.colors.text}
          style={styles.buttonIcon}
        />
        <Text style={[styles.logoText, { color: theme.colors.text }]}>
          PREIDAS
        </Text>
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
    height: BOTTOM_TAB_HEIGHT,
    elevation: 0,
    borderTopWidth: 0,
    shadowColor: "transparent",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    flexDirection: "row",
    justifyContent: "space-between",
    paddingHorizontal: 20,
  },
  middleButton: {
    position: "absolute",
    bottom: 40,
    left: (width - MIDDLE_BUTTON_SIZE) / 2,
    width: MIDDLE_BUTTON_SIZE,
    height: MIDDLE_BUTTON_SIZE,
    borderRadius: MIDDLE_BUTTON_SIZE / 2,
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1,
    elevation: 5,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  buttonIcon: {
    marginBottom: 2,
  },
  logoText: {
    fontSize: 12,
    fontWeight: "bold",
    marginTop: -2,
  },
  activeIconContainer: {
    backgroundColor: "#F2FF2A",
    padding: 8,
    borderRadius: 8,
  },
});
