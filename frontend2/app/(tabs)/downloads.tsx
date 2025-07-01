import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
  StatusBar,
  ScrollView,
  RefreshControl,
  Linking,
} from "react-native";
import { router } from "expo-router";
import { theme } from "@/src/theme";
import { IconSymbol } from "@/components/ui/IconSymbol";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { apiService } from "../services/apiService";
import { useFocusEffect } from "@react-navigation/native";
import { useCallback } from "react";

interface Download {
  id: number;
  title: string;
  description: string;
  url: string;
  status: "PENDING" | "DOWNLOADED";
}

const { width } = Dimensions.get("window");
const SPACING = 16;

export default function DownloadsScreen() {
  const [downloads, setDownloads] = useState<Download[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>("all");

  // useEffect(() => {
  //   //
  // }, []);

  useFocusEffect(
    useCallback(() => {
      fetchDownloads(); // Refetch downloads when screen is focused
      apiService.activityLog.trackAction("screen downloads"); // Record action
    }, [])
  );

  const fetchDownloads = async () => {
    try {
      setLoading(true);
      // const response = await apiService.downloads.getAll();
      // Use mock response for testing
      const response = {
        data: [
          {
            id: 1,
            title: "Ejercicios para Tobillos",
            description: "Guía de ejercicios de fortalecimiento de tobillos",
            url: "https://www.google.com/search?q=ejercicios+de+tobillos",
            status: "PENDING" as "PENDING",
          },
          {
            id: 2,
            title: "Guía de Prevención para el Hogar",
            description: "Instrucciones para habilitar el hogar seguro",
            url: "https://www.sanidad.gob.es/areas/promocionPrevencion/lesiones/ocioHogar/documentosTecnicos/docs/Prevenir_caidas_en_el_hogar.pdf",
            status: "PENDING" as "PENDING",
          },
        ],
      };
      setDownloads(response.data);
    } catch (error) {
      console.error("Error fetching downloads:", error);
      setError("Error al cargar los descargables");
    } finally {
      setLoading(false);
    }
  };

  const reloadDownloads = () => {
    apiService.activityLog.trackAction("reload downloads"); // Record action
    fetchDownloads();
  };

  const renderDownloadItem = ({ item }: { item: Download }) => (
    <View style={styles.row}>
      <View style={[styles.cell, { flex: 0.2 }]}>
        <View style={styles.statusContainer}>
          <IconSymbol
            name={
              item.status === "PENDING"
                ? "radio-button-off"
                : "checkmark-circle-outline"
            }
            size={20}
            color={
              item.status === "PENDING"
                ? theme.colors.warning
                : theme.colors.success
            }
          />
        </View>
      </View>
      <Text style={[styles.cell, { flex: 0.8 }]}>{item.title}</Text>
      <Text style={[styles.cell, { flex: 1 }]}>{item.description}</Text>
      {/* Downloads button download-outline*/}
      <TouchableOpacity
        style={[
          styles.cell,
          { flex: 0.8, justifyContent: "center", alignItems: "center" },
        ]}
        onPress={() => {
          apiService.activityLog.trackAction(`download ${item.id}`); // Record action
          // Set status to DOWNLOADED if it was PENDING
          if (item.status === "PENDING") {
            item.status = "DOWNLOADED";
            setDownloads((prev) =>
              prev.map((d) => (d.id === item.id ? item : d))
            );
            // Send to API
            ///TODO
          }
          // For now just open the URL in a browser
          console.log(`Downloading: ${item.url}`);
          Linking.openURL(item.url);
        }}
      >
        <IconSymbol name="download-outline" size={30} color={"black"} />
      </TouchableOpacity>
    </View>
  );

  const filters = [
    { id: "all", label: "Todos" },
    { id: "PENDING", label: "Pendientes" },
    { id: "DOWNLOADED", label: "Descargados" },
  ];

  const filteredDownloads = downloads.filter((download) =>
    selectedFilter === "all" ? true : download.status === selectedFilter
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={reloadDownloads}>
          <Text style={styles.retryText}>Reintentar</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" />
      {/* <ScrollView
        // Padding and margin 0
        contentContainerStyle={{ padding: 0, margin: 0 }}
        // style={{ flex: 1 }}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={reloadDownloads} />
        }
      > */}
      <View style={styles.filtersContainer}>
        <FlatList
          horizontal
          data={filters}
          showsHorizontalScrollIndicator={false}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[
                styles.filterButton,
                selectedFilter === item.id && styles.filterButtonActive,
              ]}
              onPress={() => setSelectedFilter(item.id)}
            >
              <Text
                style={[
                  styles.filterText,
                  selectedFilter === item.id && styles.filterTextActive,
                ]}
              >
                {item.label}
              </Text>
            </TouchableOpacity>
          )}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.filtersContent}
        />
      </View>

      {/* Table header */}
      <View style={styles.table}>
        <View
          style={[
            styles.table_header,
            { paddingLeft: SPACING, paddingRight: SPACING },
          ]}
        >
          <View
            style={[styles.cell_header, { flex: 0.2 }, styles.statusContainer]}
          >
            <IconSymbol
              name={"checkmark-circle-outline"}
              size={20}
              color={"black"}
            />
          </View>
          <Text style={[styles.cell_header, { flex: 0.8 }]}>Título</Text>
          <Text style={[styles.cell_header, { flex: 1 }]}>Descripción</Text>
          <Text style={[styles.cell_header, { flex: 0.8 }]}>Descarga</Text>
          {/* </View> */}
        </View>

        <FlatList
          style={styles.listContainer}
          refreshControl={
            <RefreshControl refreshing={loading} onRefresh={reloadDownloads} />
          }
          data={filteredDownloads || []}
          renderItem={renderDownloadItem}
          keyExtractor={(item) => item.id.toString()}
          // contentContainerStyle={styles.listContainer}
          contentContainerStyle={styles.table}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <IconSymbol
                name="cloud-offline"
                size={64}
                color={theme.colors.text}
              />
              <Text style={styles.emptyText}>No hay descargas disponibles</Text>
            </View>
          }
        />
      </View>
      {/* </ScrollView> */}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: SPACING,
    backgroundColor: theme.colors.primary,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: "bold",
    color: theme.colors.text,
  },
  addButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: theme.colors.primary,
    justifyContent: "center",
    alignItems: "center",
  },
  filtersContainer: {
    marginTop: SPACING,
    marginBottom: SPACING / 2,
  },
  filtersContent: {
    paddingHorizontal: SPACING,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    backgroundColor: theme.colors.background,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  filterButtonActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  filterText: {
    color: theme.colors.text,
    fontWeight: "500",
  },
  filterTextActive: {
    color: theme.colors.text,
    fontWeight: "600",
  },
  listContainer: {
    // padding: SPACING,
    paddingLeft: SPACING,
    paddingRight: SPACING,
    paddingBottom: SPACING * 4,
  },
  priorityBadge: {
    flexDirection: "row",
    alignItems: "center",
  },
  priorityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  priorityText: {
    fontSize: 12,
    color: theme.colors.text,
    opacity: 0.7,
  },
  dateContainer: {
    flexDirection: "row",
    alignItems: "center",
  },
  dateText: {
    fontSize: 12,
    color: theme.colors.text,
    marginLeft: 4,
  },
  categoryBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    backgroundColor: theme.colors.primary,
    borderRadius: 12,
  },
  categoryText: {
    fontSize: 12,
    color: theme.colors.text,
    fontWeight: "500",
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  errorContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: SPACING * 2,
  },
  errorText: {
    fontSize: 16,
    color: theme.colors.error,
    textAlign: "center",
    marginBottom: 16,
  },
  retryButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: theme.colors.primary,
    borderRadius: 8,
  },
  retryText: {
    color: theme.colors.text,
    fontWeight: "600",
  },
  emptyContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: SPACING * 4,
  },
  emptyText: {
    fontSize: 16,
    color: theme.colors.text,
    opacity: 0.7,
    marginTop: SPACING,
  },
  statusContainer: {
    justifyContent: "center",
    alignItems: "center",
  },
  statusText: {
    fontSize: 14,
    color: theme.colors.text,
    marginLeft: 4,
  },
  table: {
    // borderWidth: 1,
    // borderColor: "lightgray",
  },
  table_header: {
    flexDirection: "row",
    // backgroundColor: "#f0f0f0",
    // padding: 10,
    marginBottom: 2,
  },
  cell_header: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderWidth: 1,
    borderColor: "black",
    justifyContent: "center",
    textAlign: "center",
    fontWeight: "bold",
  },
  row: {
    flexDirection: "row",
  },
  cell: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderWidth: 1,
    borderColor: "lightgray",
    justifyContent: "center",
    textAlign: "center",
  },
});
