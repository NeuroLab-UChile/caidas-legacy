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
import React, { useEffect, useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useAuth } from "../contexts/auth";
import { apiService } from "@/app/services/apiService";

import { WelcomeAlert } from "@/components/WelcomeAlert";
import { IconSymbol } from "@/components/ui/IconSymbol";
import { router } from "expo-router";
import { HapticTab } from "@/components/HapticTab";
import { theme } from "@/src/theme";
import authService from "../services/authService";
import { ScrollLayout } from "@/components/ScrollLayout";
import { Ionicons } from "@expo/vector-icons";

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
  | "folder"
  | "cloud-download";

interface Event {
  id: number;
  title: string;
  description: string;
  date: string;
  status: "pending" | "completed" | "cancelled" | null | string;
}

interface TextRecommendation {
  id: number;
  data: string;
  category: string;
}

interface MenuItem {
  name: string;
  title: string;
  icon: IconNames | undefined;
  customIcon?: any;
}

const leftHiddenItems: MenuItem[] = [
  {
    name: "action",
    title: "WE-TRAIN",
    customIcon: require("@/assets/images/logo_color.png"),
    icon: undefined,
  },
];

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
  // {
  //   name: "action",
  //   title: "WE-TRAIN",
  //   customIcon: require("@/assets/images/logo_color.png"),
  //   icon: undefined,
  // },
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
  {
    name: "downloads",
    title: "Contenido Descargable",
    icon: "cloud-download",
  },
];

export default function TabLayout() {
  const { userProfile } = useAuth();

  // Estados para controlar nuestro modal de alerta
  const [alertInfo, setAlertInfo] = useState({
    title: "",
    message: "",
    showOnPostpone: false,
    eventId: 0, // ID del evento para posponer
  });
  const [isAlertVisible, setIsAlertVisible] = useState(false);
  const [initialAlertShown, setInitialAlertShown] = useState(false); // Para que se muestre solo una vez

  useEffect(() => {
    // La lógica se ejecuta solo si hay un usuario y la alerta inicial no se ha mostrado
    if (userProfile && !initialAlertShown) {
      const fetchAndPrepareAlert = async () => {
        setInitialAlertShown(true); // Marcamos como mostrada inmediatamente
        try {
          // 1. OBTENEMOS LAS CITAS/EVENTOS
          const appointmentsResponse = await apiService.events.getAll();
          const allEvents = (appointmentsResponse?.data as Event[]) || [];

          // 2. BUSCAMOS LA PRÓXIMA CITA FUTURA PENDIENTE
          const now = new Date();
          now.setHours(0, 0, 0, 0);

          // Get postponed events from AsyncStorage
          // Format: "postponedEvents": { [eventId]: timestamp }
          const postponedEventsString = await AsyncStorage.getItem(
            "postponedEvents"
          );
          const postponedEvents = postponedEventsString
            ? JSON.parse(postponedEventsString)
            : {};
          // Check if we need to remove any postponed events that are older than 1 week
          const oneWeekAgo = new Date();
          // TEST -1 minute
          // oneWeekAgo.setMinutes(oneWeekAgo.getMinutes() - 1); // Test with 1 minute ago
          // REAL -1 week
          oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
          console.log("Comparing with oneWeekAgo:", oneWeekAgo);
          let postponedEventsChanged = false;
          Object.keys(postponedEvents).forEach((eventId) => {
            if (new Date(postponedEvents[eventId]) < oneWeekAgo) {
              // Re-enable the event if it's been more than a week
              delete postponedEvents[eventId];
              postponedEventsChanged = true;
              console.log(`Postponed event ${eventId} removed after 1 week`);
            }
          });
          // If we changed the postponed events, save them back to AsyncStorage
          if (postponedEventsChanged) {
            console.log("Postponed events:", postponedEvents);
            await AsyncStorage.setItem(
              "postponedEvents",
              JSON.stringify(postponedEvents)
            );
          }

          const upcomingEvents = allEvents
            .map((event) => ({ ...event, parsedDate: new Date(event.date) }))
            .filter(
              (event) =>
                event.status !== "completed" &&
                event.status !== "cancelled" &&
                !postponedEvents[event.id] && // Exclude postponed events
                event.parsedDate >= now
            )
            .sort((a, b) => a.parsedDate.getTime() - b.parsedDate.getTime());

          const nextEvent =
            upcomingEvents.length > 0 ? upcomingEvents[0] : null;

          const userName =
            userProfile.first_name || userProfile.username || "usuario";
          let finalTitle = `¡Hola, ${userName}!`;
          let finalMessage = "";
          let showOnPostpone = false;
          let eventId = 0; // ID del evento para posponer

          // 3. LÓGICA PRINCIPAL: Si hay un próximo evento, lo mostramos.
          if (nextEvent) {
            finalTitle = "¡Recordatorio de Próximo Evento!";
            showOnPostpone = true; // Hacemos visible el botón de posponer
            eventId = nextEvent.id;
            const dateOptions: Intl.DateTimeFormatOptions = {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            };
            const formattedDate = nextEvent.parsedDate.toLocaleDateString(
              "es-ES",
              dateOptions
            );
            finalMessage = `Recuerda tu próximo evento: "${nextEvent.title}" el día ${formattedDate}.\n\nDescripción: ${nextEvent.description}`;
          }
          // 4. LÓGICA DE RESPALDO: Si no hay eventos, buscamos una recomendación aleatoria.
          else {
            showOnPostpone = false; // No hacemos visible el botón de posponer si no hay eventos
            const recommendationsResponse =
              await apiService.recommendations.getAll();
            const allRecommendations =
              (recommendationsResponse?.data
                ?.recommendations as TextRecommendation[]) || [];

            if (allRecommendations.length > 0) {
              const randomIndex = Math.floor(
                Math.random() * allRecommendations.length
              );
              const randomRecommendation = allRecommendations[randomIndex];
              finalTitle = "Recomendación del día";
              finalMessage = randomRecommendation.data;
            } else {
              finalMessage =
                "No tienes eventos ni recomendaciones nuevas por ahora. ¡Que tengas un excelente día!";
            }
          }

          // 5. Guardamos la información y hacemos visible el Modal
          setAlertInfo({
            title: finalTitle,
            message: finalMessage,
            showOnPostpone: showOnPostpone,
            eventId: eventId,
          });
          setIsAlertVisible(true);
        } catch (error) {
          console.error("Error al preparar la alerta:", error);
          setAlertInfo({
            title: `¡Bienvenido/a, ${userProfile.first_name || "usuario"}!`,
            message:
              "No se pudo conectar al servidor para obtener tus novedades.",
            showOnPostpone: false,
            eventId: 0,
          });
          setIsAlertVisible(true);
        }
      };

      fetchAndPrepareAlert();
    }
  }, [userProfile, initialAlertShown]);

  const handleMiddleButtonPress = () => {
    router.push("/(tabs)/action");
  };

  return (
    <View style={styles.container}>
      <ScrollLayout>
        <Tabs
          screenOptions={({ route }: { route: any }) => ({
            tabBarActiveTintColor: theme.colors.background,
            tabBarInactiveTintColor: theme.colors.background + "80",
            headerShown: true,
            tabBarButton: HapticTab,
            headerTitle: () => {
              const item = [
                ...leftHiddenItems,
                ...leftMenuItems,
                ...rightMenuItems,
                ...hiddenItems,
              ].find((item) => item.name === route.name);
              return (
                <Text
                  style={[
                    styles.headerTitle,
                    { color: theme.colors.background },
                  ]}
                >
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
              const item = [
                ...leftHiddenItems,
                ...leftMenuItems,
                ...rightMenuItems,
                ...hiddenItems,
              ].find((item) => item.name === route.name);

              return (
                <View
                  style={[
                    styles.headerContainer,
                    { backgroundColor: theme.colors.text },
                  ]}
                >
                  <View style={styles.headerTopRow}>
                    {(route.name === "events" ||
                      route.name === "downloads" ||
                      route.name === "category-detail") && (
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

                    <Text
                      style={[
                        styles.headerTitle,
                        { color: theme.colors.background },
                      ]}
                    >
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
                                  await apiService.activityLog.trackAction(
                                    "logout"
                                  ); // Record action - ensure it occurs before logout
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
                        { backgroundColor: theme.colors.text },
                      ]}
                    >
                      <View style={styles.logoutContent}>
                        <IconSymbol
                          name="power"
                          size={18}
                          color={theme.colors.background}
                          style={styles.logoutIcon}
                        />
                        <Text
                          style={[
                            styles.logoutText,
                            { color: theme.colors.background },
                          ]}
                        >
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
                  {item.icon && (
                    <Ionicons
                      name={item.icon}
                      size={24}
                      color={
                        focused
                          ? theme.colors.background
                          : theme.colors.background + "80"
                      }
                    />
                  )}
                </View>
              );
            },
          })}
        >
          {leftHiddenItems.map((item) => (
            <Tabs.Screen
              key={item.name}
              name={item.name}
              options={{
                title: item.title,
                headerTitle: item.title,
                href: null, // Hide from tab bar
              }}
            />
          ))}

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

          {hiddenItems.map((item, idx) => (
            <Tabs.Screen
              key={item.name}
              name={item.name}
              options={{
                title: item.title,
                headerTitle: item.title,
                // "Hack" to generate spacing and maintain the navigation items
                ...(idx < 2 && {
                  // tabBarButton: () => null,
                  href: null, // Hide from tab bar
                }),
                ...(idx >= 2 && {
                  tabBarButton: () => null,
                  // href: null, // Hide from tab bar
                }),
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
        <View
          style={[styles.middleButtonTop, { borderColor: theme.colors.text }]}
        />
        <View style={styles.middleButtonContent}>
          <Image
            source={require("@/assets/images/logo_color.png")}
            style={styles.middleButtonLogo}
            resizeMode="contain"
          />
          <Text
            style={[
              styles.middleButtonText,
              { color: theme.colors.background },
            ]}
          >
            WE-TRAIN
          </Text>
        </View>
      </TouchableOpacity>
      <WelcomeAlert
        visible={isAlertVisible}
        title={alertInfo.title}
        message={alertInfo.message}
        showOnPostpone={!!alertInfo.showOnPostpone}
        onPostpone={async () => {
          setIsAlertVisible(false);
          console.log("Alerta pospuesta por 1 semana");
          // Store id and timestamp in AsyncStorage
          const postponedEventsString = await AsyncStorage.getItem(
            "postponedEvents"
          );
          const postponedEvents = postponedEventsString
            ? JSON.parse(postponedEventsString)
            : {};
          const now = new Date();
          postponedEvents[alertInfo.eventId] = now.toISOString(); // Store as ISO string
          await AsyncStorage.setItem(
            "postponedEvents",
            JSON.stringify(postponedEvents)
          );
          console.log("Postponed events:", postponedEvents);
          // Show confirmation alert
          Alert.alert(
            "Recordatorio pospuesto",
            "El recordatorio ha sido pospuesto por 1 semana. Puedes volver a revisarlo en la sección de Eventos."
          );
        }}
        onClose={() => setIsAlertVisible(false)}
      />
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
    alignItems: "center",
    justifyContent: "center",
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
