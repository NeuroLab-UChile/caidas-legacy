import React from "react";
import { Tabs } from "expo-router";
import {
  View,
  TouchableOpacity,
  Text,
  StyleSheet,
  Dimensions,
  Alert,
  Image,
} from "react-native";
import { IconSymbol } from "@/components/ui/IconSymbol";
import { router } from "expo-router";
import { HapticTab } from "@/components/HapticTab";
import { theme } from "@/src/theme";
import authService from "../services/authService";
import { ScrollLayout } from "@/components/ScrollLayout";

const BOTTOM_TAB_HEIGHT = 83;
const MIDDLE_BUTTON_SIZE = 76;
const { width } = Dimensions.get("window");
const SCREEN_WIDTH = width * 0.95;

interface MenuItem {
  name: string;
  title: string;
  icon?: string;
  customIcon?: any;
}

const leftMenuItems: MenuItem[] = [
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

const rightMenuItems: MenuItem[] = [
  {
    name: "training",
    title: "ENTRENAR",
    icon: "figure.walk",
  },
  {
    name: "profile",
    title: "MIS DATOS",
    icon: "person",
  },
];

const hiddenItems: MenuItem[] = [
  {
    name: "action",
    title: "WE-TRAIN",
    customIcon: require("@/assets/images/logo_color.png"),
  },
  {
    name: "category-detail",
    title: "Detalle de Categoría",
    icon: "folder",
  },
  {
    name: "events",
    title: "Eventos",
    icon: "calendar",
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
      <ScrollLayout>
        <Tabs
          screenOptions={({ route }) => ({
            tabBarActiveTintColor: "#FFFFFF",
            tabBarInactiveTintColor: "#FFFFFF80",
            headerShown: true,
            tabBarButton: HapticTab,
            headerTitle: () => {
              const item = [
                ...leftMenuItems,
                ...rightMenuItems,
                ...hiddenItems,
              ].find((item) => item.name === route.name);
              return (
                <Text style={[styles.headerTitle, { color: "#FFFFFF" }]}>
                  {item?.title || route.name}
                </Text>
              );
            },
            headerStyle: {
              backgroundColor: "#000000",
              elevation: 0,
              shadowOpacity: 0,
              height: route.name === "category-detail" ? 100 : 60,
            },
            headerTitleAlign: "center",
            header: ({ route, options }) => {
              const item = [
                ...leftMenuItems,
                ...rightMenuItems,
                ...hiddenItems,
              ].find((item) => item.name === route.name);
              return (
                <View style={styles.headerContainer}>
                  <View style={styles.headerTopRow}>
                    <Text
                      style={[styles.headerTitle, { color: theme.colors.text }]}
                    >
                      {item?.title || route.name}
                    </Text>
                    <TouchableOpacity
                      onPress={() => {
                        Alert.alert(
                          "Cerrar Sesión",
                          "¿Estás seguro que deseas salir?",
                          [
                            {
                              text: "Cancelar",
                              style: "cancel",
                            },
                            {
                              text: "Salir",
                              style: "destructive",
                              onPress: async () => {
                                try {
                                  await authService.logout();
                                  router.replace("/sign-in");
                                } catch (error) {
                                  console.error(
                                    "Error al cerrar sesión:",
                                    error
                                  );
                                  Alert.alert(
                                    "Error",
                                    "No se pudo cerrar la sesión"
                                  );
                                }
                              },
                            },
                          ]
                        );
                      }}
                      style={[
                        styles.logoutButton,
                        {
                          backgroundColor: theme.colors.background,
                          borderWidth: 2,
                          borderColor: theme.colors.border,
                        },
                      ]}
                    >
                      <View style={styles.logoutContent}>
                        <IconSymbol
                          name="power"
                          size={18}
                          color={theme.colors.text}
                          style={styles.logoutIcon}
                        />
                        <Text
                          style={[
                            styles.logoutText,
                            { color: theme.colors.text },
                          ]}
                        >
                          Salir
                        </Text>
                      </View>
                    </TouchableOpacity>
                  </View>
                  {route.name === "category-detail" && (
                    <TouchableOpacity
                      onPress={() => router.replace("/(tabs)/action")}
                      style={[styles.backButton, { marginTop: 8 }]}
                    >
                      <Text
                        style={[
                          styles.backButtonText,
                          { color: theme.colors.text },
                        ]}
                      >
                        {"< Volver"}
                      </Text>
                    </TouchableOpacity>
                  )}
                </View>
              );
            },
            headerLeft: undefined,
            tabBarStyle: {
              backgroundColor: "#000000",
              borderTopWidth: 2,
              borderLeftWidth: 2,
              borderRightWidth: 2,
              borderColor: "#000000",
              borderBottomWidth: 0,
            },

            tabBarItemStyle: {
              width: SCREEN_WIDTH / 5, // Reducir ancho proporcional de cada botón
              height: BOTTOM_TAB_HEIGHT - 20,
              paddingTop: 4,
            },
            tabBarLabelStyle: {
              fontSize: 9,
              fontWeight: "600",
              position: "relative",
              top: 0,
              display: "flex",
              marginTop: 4,
            },
            tabBarIcon: ({ color, focused }) => {
              const item = [...leftMenuItems, ...rightMenuItems].find(
                (item) => item.name === route.name
              );
              if (!item) return null;

              return (
                <View
                  style={[
                    styles.iconContainer,
                    focused && styles.activeIconContainer,
                  ]}
                >
                  {item.customIcon ? (
                    <Image
                      source={item.customIcon}
                      style={{
                        width: 24,
                        height: 24,
                      }}
                      resizeMode="contain"
                    />
                  ) : (
                    <IconSymbol
                      size={24}
                      name={item.icon as any}
                      color={focused ? theme.colors.text : color}
                    />
                  )}
                </View>
              );
            },
            headerRight: () => (
              <TouchableOpacity
                onPress={() => {
                  Alert.alert(
                    "Cerrar Sesión",
                    "¿Estás seguro que deseas salir?",
                    [
                      {
                        text: "Cancelar",
                        style: "cancel",
                      },
                      {
                        text: "Salir",
                        style: "destructive",
                        onPress: async () => {
                          try {
                            await authService.logout();
                            router.replace("/login");
                          } catch (error) {
                            console.error("Error al cerrar sesión:", error);
                            Alert.alert("Error", "No se pudo cerrar la sesión");
                          }
                        },
                      },
                    ]
                  );
                }}
                style={[
                  styles.logoutButton,
                  {
                    backgroundColor: theme.colors.background,
                    borderWidth: 2,
                    borderColor: theme.colors.border,
                  },
                ]}
              >
                <View style={styles.logoutContent}>
                  <IconSymbol
                    name="power"
                    size={20}
                    color={theme.colors.text}
                    style={styles.logoutIcon}
                  />
                  <Text
                    style={[styles.logoutText, { color: theme.colors.text }]}
                  >
                    Salir
                  </Text>
                </View>
              </TouchableOpacity>
            ),
            tabBarIconStyle: {
              marginBottom: 4,
            },
          })}
        >
          {leftMenuItems.map((item) => (
            <Tabs.Screen
              key={item.name}
              name={item.name}
              options={{
                title: item.title,
                headerTitle: item.title,
                tabBarLabel: item.title,
                tabBarIcon: ({ color }) => (
                  <IconSymbol size={24} name={item.icon as any} color={color} />
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
                headerTitle: item.title,
                tabBarButton: () => null,
                tabBarIcon: ({ color, focused }) => {
                  if (item.customIcon) {
                    return (
                      <Image
                        source={item.customIcon}
                        style={{
                          width: 24,
                          height: 24,
                          tintColor: focused ? theme.colors.text : color,
                        }}
                        resizeMode="contain"
                      />
                    );
                  }
                  return (
                    <IconSymbol
                      size={24}
                      name={item.icon as any}
                      color={focused ? theme.colors.text : color}
                    />
                  );
                },
                headerLeft:
                  item.name === "category-detail"
                    ? () => (
                        <TouchableOpacity
                          onPress={() => router.replace("/(tabs)/action")}
                          style={styles.backButton}
                        >
                          <Text
                            style={[
                              styles.backButtonText,
                              { color: theme.colors.text },
                            ]}
                          >
                            {"< Volver"}
                          </Text>
                        </TouchableOpacity>
                      )
                    : undefined,
              }}
            />
          ))}

          {rightMenuItems.map((item) => (
            <Tabs.Screen
              key={item.name}
              name={item.name}
              options={{
                title: item.title,
                headerTitle: item.title,
                tabBarLabel: item.title,
                tabBarIcon: ({ color }) => (
                  <IconSymbol size={24} name={item.icon as any} color={color} />
                ),
              }}
            />
          ))}
        </Tabs>
      </ScrollLayout>

      <TouchableOpacity
        onPress={handleMiddleButtonPress}
        activeOpacity={0.8}
        style={[
          styles.middleButton,
          {
            backgroundColor: "#000000",
          },
        ]}
      >
        <View
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: MIDDLE_BUTTON_SIZE / 2,
            borderTopLeftRadius: MIDDLE_BUTTON_SIZE / 2,
            borderTopRightRadius: MIDDLE_BUTTON_SIZE / 2,
            borderWidth: 2,
            borderColor: "#000000",
            borderBottomWidth: 0,
          }}
        />
        <View
          style={{
            marginTop: 10,
            alignItems: "center",
          }}
        >
          <Image
            source={require("@/assets/images/logo_color.png")}
            style={{
              width: 40,
              height: 40,
            }}
            resizeMode="contain"
          />
          <Text style={[styles.logoText, { color: "#FFFFFF" }]}>WE-TRAIN</Text>
        </View>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  backButton: {
    alignSelf: "flex-start",
    padding: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.border,
    backgroundColor: theme.colors.background,
  },
  backButtonText: {
    fontSize: 16,
    fontWeight: "600",
  },
  tabBar: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: BOTTOM_TAB_HEIGHT - 15, // Altura ajustada si es necesario
    elevation: 0,
    shadowColor: "transparent",
    flexDirection: "row",
    justifyContent: "space-around", // Reducir espacio horizontal
    paddingHorizontal: 10, // Margen horizontal reducido
    paddingBottom: 12,
    overflow: "hidden",
  },
  middleButton: {
    backgroundColor: "#000000",
    position: "absolute",
    bottom: 40,
    left: (width - MIDDLE_BUTTON_SIZE) / 2,
    width: MIDDLE_BUTTON_SIZE,
    height: MIDDLE_BUTTON_SIZE,
    borderTopLeftRadius: MIDDLE_BUTTON_SIZE / 2,
    borderTopRightRadius: MIDDLE_BUTTON_SIZE / 2,
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
    elevation: 8,
  },
  buttonIcon: {
    marginBottom: 2,
  },
  logoText: {
    fontSize: 9,
    fontWeight: "bold",
    textAlign: "center",
    letterSpacing: 0.5,
    marginTop: 10,
  },
  activeIconContainer: {
    backgroundColor: theme.colors.text + "20",
    transform: [{ scale: 1.1 }],
  },
  logoutButton: {
    marginRight: 0,
    padding: 6,
    paddingHorizontal: 10,
    borderRadius: 8,
    elevation: 1,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.15,
    shadowRadius: 2,
    zIndex: 1,
  },
  logoutContent: {
    flexDirection: "row",
    alignItems: "center",
    height: 24,
  },
  logoutIcon: {
    marginRight: 4,
  },
  logoutText: {
    fontSize: 16,
    fontWeight: "600",
  },
  iconContainer: {
    padding: 4,
    borderRadius: 12,
    backgroundColor: "transparent",
  },
  headerContainer: {
    backgroundColor: theme.colors.primary,
    paddingTop: 40,
    paddingHorizontal: 16,
    paddingBottom: 8,
  },
  headerTopRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 4,
    paddingRight: 0,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: "600",
    flex: 1,
  },
});
