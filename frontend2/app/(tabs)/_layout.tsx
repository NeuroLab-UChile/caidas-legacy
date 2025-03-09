
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
import { Ionicons } from '@expo/vector-icons';

const BOTTOM_TAB_HEIGHT = 83;
const MIDDLE_BUTTON_SIZE = 76;
const { width } = Dimensions.get("window");
const SCREEN_WIDTH = width * 0.95;

// Definimos los tipos de iconos que estamos usando
type IconNames = 
  | "calendar"
  | "checkbox"
  | "walk"
  | "person"
  | "power"
  | "chevron-back"
  | "folder";

interface MenuItem {
  name: string;
  title: string;
  icon: IconNames | undefined;
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
    icon: "checkbox",
  },
];

const rightMenuItems: MenuItem[] = [
  {
    name: "training",
    title: "ENTRENAR",
    icon: "walk",
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
    icon: undefined
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
    <View style={styles.container}>
      <ScrollLayout>
        <Tabs
          screenOptions={({ route }: { route: any }) => ({
            tabBarActiveTintColor: theme.colors.background,
            tabBarInactiveTintColor: theme.colors.background + '80',
            headerShown: true,
            tabBarButton: HapticTab,
            headerTitle: () => {
              const item = [...leftMenuItems, ...rightMenuItems, ...hiddenItems]
                .find((item) => item.name === route.name);
              return (
                <Text style={[styles.headerTitle, { color: theme.colors.background }]}>
                  {item?.title || route.name}
                </Text>
              );
            },
            headerStyle: {
              backgroundColor: theme.colors.text,
              elevation: 0,
              shadowOpacity: 0,
              height: route.name === "category-detail" ? 100 : 60,
            },
            headerTitleAlign: "center",
            header: ({ route }: { route: any }) => {
              const item = [...leftMenuItems, ...rightMenuItems, ...hiddenItems]
                .find((item) => item.name === route.name);
              
              return (
                <View style={[styles.headerContainer, { backgroundColor: theme.colors.text }]}>
                  <View style={styles.headerTopRow}>
                    {(route.name === "events" || route.name === "category-detail") && (
                      <TouchableOpacity
                        onPress={() => router.push("/(tabs)/action")}
                        style={styles.backArrowButton}
                      >
                        <Ionicons
                          name="chevron-back"
                          size={24}
                          color={theme.colors.background}
                        />
                      </TouchableOpacity>
                    )}

                    <Text style={[styles.headerTitle, { color: theme.colors.background }]}>
                      {item?.title || route.name}
                    </Text>

                    <TouchableOpacity
                      onPress={() => {
                        Alert.alert(
                          "Cerrar Sesión",
                          "¿Estás seguro que deseas salir?",
                          [
                            { text: "Cancelar", style: "cancel" },
                            {
                              text: "Salir",
                              style: "destructive",
                              onPress: async () => {
                                try {
                                  await authService.logout();
                                  router.replace("/sign-in");
                                } catch (error) {
                                  console.error("Error al cerrar sesión:", error);
                                  Alert.alert("Error", "No se pudo cerrar la sesión");
                                }
                              },
                            },
                          ]
                        );
                      }}
                      style={[styles.logoutButton, { backgroundColor: theme.colors.text }]}
                    >
                      <View style={styles.logoutContent}>
                        <IconSymbol
                          name="power"
                          size={18}
                          color={theme.colors.background}
                        />
                        <Text style={[styles.logoutText, { color: theme.colors.background }]}>
                          Salir
                        </Text>
                      </View>
                    </TouchableOpacity>
                  </View>
                </View>
              );
            },
            tabBarStyle: {
              backgroundColor: theme.colors.text,
              borderTopWidth: 2,
              borderLeftWidth: 2,
              borderRightWidth: 2,
              borderColor: theme.colors.text,
              borderBottomWidth: 0,
              height: BOTTOM_TAB_HEIGHT,
            },
            tabBarLabelStyle: {
              fontSize: 9,
              fontWeight: "600",
              marginTop: 4,
              color: theme.colors.background,
            },
            tabBarIcon: ({ focused }: { focused: any }) => {
              const item = [...leftMenuItems, ...rightMenuItems]
                .find((item) => item.name === route.name);
              if (!item) return null;

              return (
                <View style={[
                  styles.iconContainer,
                  focused && styles.activeIconContainer
                ]}>
                  {item.icon && (
                    <Ionicons
                      name={item.icon}
                      size={24}
                      color={focused ? theme.colors.background : theme.colors.background + '80'}
                    />
                  )}
                </View>
              );
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
              }}
            />
          ))}
        </Tabs>
      </ScrollLayout>

      <TouchableOpacity
        onPress={handleMiddleButtonPress}
        activeOpacity={0.8}
        style={[styles.middleButton, { backgroundColor: theme.colors.text }]}
      >
        <View style={[styles.middleButtonTop, { borderColor: theme.colors.text }]} />
        <View style={styles.middleButtonContent}>
          <Image
            source={require("@/assets/images/logo_color.png")}
            style={styles.middleButtonLogo}
            resizeMode="contain"
          />
          <Text style={[styles.middleButtonText, { color: theme.colors.background }]}>
            WE-TRAIN
          </Text>
        </View>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  headerContainer: {
    paddingTop: 40,
    paddingHorizontal: 16,
    paddingBottom: 8,
  },
  headerTopRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 4,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: "600",
    flex: 1,
    textAlign: "center",
  },
  backArrowButton: {
    padding: 8,
    marginRight: 8,
    borderRadius: 8,
  },
  logoutButton: {
    marginRight: 0,
    padding: 6,
    paddingHorizontal: 10,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: theme.colors.background,
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
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 20,
  },
  activeIconContainer: {
    backgroundColor: `${theme.colors.primary}20`,
  },
  icon: {
    width: 24,
    height: 24,
  },
  middleButton: {
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
  middleButtonTop: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    height: MIDDLE_BUTTON_SIZE / 2,
    borderTopLeftRadius: MIDDLE_BUTTON_SIZE / 2,
    borderTopRightRadius: MIDDLE_BUTTON_SIZE / 2,
    borderWidth: 2,
    borderBottomWidth: 0,
  },
  middleButtonContent: {
    marginTop: 10,
    alignItems: "center",
  },
  middleButtonLogo: {
    width: 40,
    height: 40,
  },
  middleButtonText: {
    fontSize: 9,
    fontWeight: "bold",
    letterSpacing: 0.5,
    marginTop: 10,
  },
  tabBarLabel: {
    fontSize: 9,
    fontWeight: "600",
    color: theme.colors.background,
    marginTop: 4,
  },
});
