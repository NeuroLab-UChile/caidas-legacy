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
  Platform,
  PermissionsAndroid,
} from "react-native";
import { router } from "expo-router";
import { theme } from "@/src/theme";
import { IconSymbol } from "@/components/ui/IconSymbol";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { apiService } from "../services/apiService";
import { useFocusEffect } from "@react-navigation/native";
import { useCallback } from "react";
import * as IntentLauncher from "expo-intent-launcher";
import RNFetchBlob from "react-native-blob-util";

interface Download {
  id: number;
  downloaded: boolean;
  download_date: string;
  content: {
    id: number;
    title: string;
    description: string;
    file: string;
  };
}

const { width } = Dimensions.get("window");
const SPACING = 16;

export default function DownloadsScreen() {
  const [downloads, setDownloads] = useState<Download[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>("all");

  useFocusEffect(
    useCallback(() => {
      fetchDownloads(); // Refetch downloads when screen is focused
      apiService.activityLog.trackAction("screen downloads"); // Record action
    }, [])
  );

  const fetchDownloads = async () => {
    try {
      setLoading(true);
      // Actual API call
      const response = await apiService.downloads.downloadableContentList();
      setDownloads(response.data);
      console.log("Downloads fetched:", JSON.stringify(response.data, null, 2));
      setError(null); // Clear any previous errors
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
              item.downloaded ? "checkmark-circle-outline" : "warning-outline"
            }
            size={20}
            color={
              item.downloaded ? theme.colors.success : theme.colors.warning
            }
          />
        </View>
      </View>
      <Text style={[styles.cell, styles.cellText, { flex: 1.2 }]}>
        {item.content.title}
      </Text>

      {/* Downloads button */}
      <TouchableOpacity
        style={[
          styles.cell,
          { flex: 0.8, justifyContent: "center", alignItems: "center" },
        ]}
        onPress={async () => {
          apiService.activityLog.trackAction(`download ${item.id}`); // Record action
          // Send to API

          const response = await apiService.downloads.registerDownload(
            item.content.id
          );
          // Set downloaded to true if response was successful

          if (response.status === 201) {
            // && !item.downloaded) {
            item.downloaded = true;
            setDownloads((prev) =>
              prev.map((d) => (d.id === item.id ? item : d))
            );
          } else {
            console.error("Error registering download:", response);
            return;
          }

          console.log(`Downloading: ${item.content.file}`);
          // // For now just open the URL in a browser to be downloaded
          // Linking.openURL(item.content.file);
          await downloadFile(
            item.content.file,
            item.content.title.replace(/\s+/g, "_"),
            item.content.file.split(".").pop() || "png"
          );
        }}
      >
        <IconSymbol
          name="download-outline"
          size={30}
          color={theme.colors.text}
        />
      </TouchableOpacity>
    </View>
  );

  const filters = [
    { id: "all", label: "Todos" },
    { id: "PENDING", label: "Pendientes" },
    { id: "DOWNLOADED", label: "Descargados" },
  ];

  const filteredDownloads = downloads.filter((download) =>
    selectedFilter === "all"
      ? true
      : selectedFilter === "DOWNLOADED"
      ? download.downloaded
      : !download.downloaded
  );

  const openDownloadsFolder = () => {
    if (Platform.OS === "android") {
      IntentLauncher.startActivityAsync("android.intent.action.VIEW_DOWNLOADS");
    } else {
      alert("Esta función solo está disponible en Android por ahora");
    }
  };

  // Example usage:
  // downloadFile('https://example.com/document.pdf', 'MyDocument', 'pdf');
  const downloadFile = async (
    fileUrl: string,
    fileName: string,
    fileExtension: string
  ) => {
    try {
      // Request permission for Android < 11
      if (Platform.OS === "android" && Platform.Version < 30) {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE,
          {
            title: "Permiso de Almacenamiento",
            message:
              "La aplicación necesita acceso a su almacenamiento para descargar archivos.",
            buttonNeutral: "Preguntar más tarde",
            buttonNegative: "Cancelar",
            buttonPositive: "OK",
          }
        );
        if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
          console.log("Storage permission denied", granted);
          return;
        }
      }

      const { config, fs } = RNFetchBlob;
      const downloadsDir = fs.dirs.DownloadDir; // Path to the Android Downloads folder

      const options = {
        // fileCache: true,
        addAndroidDownloads: {
          useDownloadManager: true,
          notification: true,
          path: `${downloadsDir}/${fileName}.${fileExtension}`,
          description: "Descargando archivo...",
          mediaScannable: true,
        },
      };

      config(options)
        .fetch("GET", fileUrl)
        .then((res) => {
          console.log("File downloaded to:", res.path());
        })
        .catch((err) => {
          console.log("Download error:", err);
        });
    } catch (error) {
      console.error("Error requesting permission or downloading:", error);
    }
  };

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

      <View style={styles.filtersContainer}>
        <TouchableOpacity
          style={[styles.filterButton, styles.filterButtonActive]}
          onPress={openDownloadsFolder}
        >
          <Text style={styles.filterTextActive}>Ver descargas</Text>
        </TouchableOpacity>

        {/* <FlatList
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
        /> */}
      </View>

      {/* Table header */}
      <View
        style={[styles.table, { paddingLeft: SPACING, paddingRight: SPACING }]}
      >
        <View style={styles.table_header}>
          <View
            style={[styles.cell_header, { flex: 0.2 }, styles.statusContainer]}
          >
            <IconSymbol
              name={"checkmark-circle-outline"}
              size={20}
              color={theme.colors.text}
            />
          </View>
          <Text style={[styles.cell_header, styles.headerText, { flex: 1.2 }]}>
            Título
          </Text>
          <Text style={[styles.cell_header, styles.headerText, { flex: 0.8 }]}>
            Descarga
          </Text>
        </View>
      </View>

      <FlatList
        style={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={reloadDownloads} />
        }
        data={filteredDownloads || []}
        renderItem={renderDownloadItem}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={{ paddingBottom: SPACING * 2 }}
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
  );
}

// ---------- STYLES ----------
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
    fontSize: theme.typography.sizes.headline1,
    fontWeight: "bold",
    color: theme.colors.text,
  },

  filtersContainer: {
    marginTop: SPACING,
    marginBottom: SPACING / 2,
    paddingHorizontal: SPACING,
    flexDirection: "row",
  },
  filterButton: {
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    backgroundColor: theme.colors.background,
    borderWidth: 1,
    borderColor: theme.colors.border,
    justifyContent: "center",
    alignItems: "center",
  },
  filterButtonActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  filterText: {
    fontSize: theme.typography.sizes.body2,
    color: theme.colors.text,
    fontWeight: "500",
  },
  filterTextActive: {
    fontSize: theme.typography.sizes.body2,
    color: theme.colors.text,
    fontWeight: "600",
  },

  listContainer: {
    paddingLeft: SPACING,
    paddingRight: SPACING,
    paddingBottom: SPACING * 2,
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
    fontSize: theme.typography.sizes.body1,
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
    fontSize: theme.typography.sizes.body2,
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
    fontSize: theme.typography.sizes.body1,
    color: theme.colors.text,
    opacity: 0.7,
    marginTop: SPACING,
  },

  statusContainer: {
    justifyContent: "center",
    alignItems: "center",
  },
  statusText: {
    fontSize: theme.typography.sizes.body2,
    color: theme.colors.text,
    marginLeft: 4,
  },

  table: {},
  table_header: {
    flexDirection: "row",
    marginBottom: 2,
  },
  headerText: {
    fontSize: theme.typography.sizes.subtitle,
    fontWeight: "600",
    color: theme.colors.text,
  },
  cell_header: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderWidth: 1,
    borderColor: theme.colors.border,
    justifyContent: "center",
    textAlign: "center",
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
  cellText: {
    fontSize: theme.typography.sizes.body2,
    color: theme.colors.text,
    opacity: 0.9,
  },
});
