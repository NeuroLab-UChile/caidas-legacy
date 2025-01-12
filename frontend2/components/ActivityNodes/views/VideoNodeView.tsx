import React, { useState, useRef, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Dimensions,
} from "react-native";
import { Video } from "expo-av";
import * as FileSystem from "expo-file-system";
import { theme } from "@/src/theme";

interface VideoNodeViewProps {
  data: {
    id: number;
    description: string;
    type: string;
    media?: {
      id: number;
      name: string;
      type: string;
      file: {
        uri?: string;
        url?: string;
      };
    }[];
    media_url?: string;
  };
}

export const VideoNodeView: React.FC<VideoNodeViewProps> = ({ data }) => {
  const videoRef = useRef<Video>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [localVideoUri, setLocalVideoUri] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const downloadVideo = async (url: string) => {
    try {
      setIsLoading(true);
      setError(null);
      console.log("Starting video download from:", url);

      const fileName = url.split("/").pop() || "video.mp4";
      const fileUri = `${FileSystem.cacheDirectory}${fileName}`;
      console.log("Target file URI:", fileUri);

      const fileInfo = await FileSystem.getInfoAsync(fileUri);
      console.log("File info:", fileInfo);

      if (fileInfo.exists) {
        console.log("Video found in cache:", fileUri);
        setLocalVideoUri(fileUri);
        setIsLoading(false);
        return;
      }

      console.log("Downloading video to:", fileUri);
      const downloadResult = await FileSystem.downloadAsync(url, fileUri);
      console.log("Download result:", downloadResult);

      if (downloadResult.status === 200) {
        console.log("Download successful, setting URI:", downloadResult.uri);
        setLocalVideoUri(downloadResult.uri);
      } else {
        throw new Error(`Download failed with status ${downloadResult.status}`);
      }
    } catch (err) {
      console.error("Error in downloadVideo:", err);
      setError(err instanceof Error ? err.message : "Error downloading video");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    console.log("=== VIDEO NODE DATA ===");
    console.log(JSON.stringify(data, null, 2));
    console.log("=== MEDIA INFO ===");
    console.log({
      mediaUrl: data.media_url,
      mediaType: data.media_type,
      isPending: data.media_pending,
      originalFilename: data.original_filename,
      id: data.id,
      type: data.type,
      content: data.content,
    });
    console.log("=== MEDIA ARRAY (if exists) ===");
    if (data.media && Array.isArray(data.media)) {
      console.log(JSON.stringify(data.media, null, 2));
    }
    console.log("========================");

    const videoUrl = data.media_url;

    if (data.media_pending) {
      setError("El video está siendo procesado...");
      setIsLoading(false);
      return;
    }

    if (!videoUrl) {
      setError("URL del video no disponible");
      setIsLoading(false);
      return;
    }

    downloadVideo(videoUrl);

    return () => {
      if (localVideoUri) {
        FileSystem.deleteAsync(localVideoUri, { idempotent: true }).catch(
          console.error
        );
      }
    };
  }, [data]);

  const finalVideoUri = localVideoUri;

  useEffect(() => {
    console.log("Final video URI updated:", finalVideoUri);
  }, [finalVideoUri]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{data.description}</Text>

      {__DEV__ && (
        <View style={styles.debugInfo}>
          <Text style={styles.debugText}>Media URL: {data.media_url}</Text>
          <Text style={styles.debugText}>Local URI: {localVideoUri}</Text>
          <Text style={styles.debugText}>Final URI: {finalVideoUri}</Text>
        </View>
      )}

      <View style={styles.videoContainer}>
        {finalVideoUri && !error && (
          <Video
            ref={videoRef}
            style={styles.video}
            source={{ uri: finalVideoUri }}
            useNativeControls
            shouldPlay={false}
            isMuted={true}
            resizeMode="contain"
            isLooping={false}
            onLoadStart={() => {
              console.log("Video load started with URI:", finalVideoUri);
              setIsLoading(true);
            }}
            onLoad={() => {
              console.log("Video loaded successfully");
              setIsLoading(false);
            }}
            onError={(error) => {
              console.error("Video playback error:", error);
              setError("Error playing video");
              setIsLoading(false);
            }}
          />
        )}

        {isLoading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color={theme.colors.primary} />
            <Text style={styles.loadingText}>Cargando video...</Text>
          </View>
        )}

        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>Error: {error}</Text>
            {__DEV__ && (
              <Text style={styles.debugText}>
                Original URL: {data.media_url || "No URL"}
                {"\n"}
                Local URI: {localVideoUri || "No local file"}
              </Text>
            )}
          </View>
        )}
      </View>

      {__DEV__ && (
        <View style={styles.debugContainer}>
          <Text style={styles.debugTitle}>Debug Info:</Text>
          <Text style={styles.debugText}>{JSON.stringify(data, null, 2)}</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 16,
    fontWeight: "500",
    marginBottom: 16,
    color: theme.colors.text,
  },
  videoContainer: {
    width: Dimensions.get("window").width - 32,
    aspectRatio: 16 / 9,
    backgroundColor: "#000",
    borderRadius: 8,
    overflow: "hidden",
    position: "relative",
  },
  video: {
    width: "100%",
    height: "100%",
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0.3)",
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    color: "#fff",
    marginTop: 8,
  },
  errorContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 16,
  },
  errorText: {
    color: theme.colors.error,
    textAlign: "center",
    marginBottom: 8,
  },
  debugText: {
    color: theme.colors.text,
    fontSize: 12,
    textAlign: "center",
  },
  debugInfo: {
    padding: 8,
    backgroundColor: "#f0f0f0",
    borderRadius: 4,
    marginBottom: 8,
  },
  debugText: {
    fontSize: 12,
    color: "#666",
    fontFamily: "monospace",
  },
  debugContainer: {
    margin: 10,
    padding: 10,
    backgroundColor: "#f0f0f0",
    borderRadius: 5,
  },
  debugTitle: {
    fontSize: 14,
    fontWeight: "bold",
    marginBottom: 5,
    color: "#333",
  },
  debugText: {
    fontSize: 12,
    fontFamily: "monospace",
    color: "#666",
  },
});
