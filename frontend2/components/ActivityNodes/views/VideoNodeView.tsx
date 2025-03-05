import React, { useState, useRef, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Dimensions,
  TouchableOpacity,
} from "react-native";
import { Video } from "expo-av";
import * as FileSystem from "expo-file-system";
import { theme } from "@/src/theme";
import { getMediaUrl } from '@/utils/mediaUrl';

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
  onNext?: () => void;
}

export const VideoNodeView: React.FC<VideoNodeViewProps> = ({
  data,
  onNext,
}) => {
  const videoRef = useRef<Video>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [localVideoUri, setLocalVideoUri] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isVideoComplete, setIsVideoComplete] = useState(false);

  const getVideoUrl = () => {
    return getMediaUrl(data?.media_url || '');
  };

  const downloadVideo = async (url: string) => {
    try {
      setIsLoading(true);
      setError(null);
      console.log("Downloading video from:", url);
      console.log("Downloading video from:", data);

      const fileName = url.split("/").pop() || "video.mp4";
      const fileUri = `${FileSystem.cacheDirectory}${fileName}`;

      const fileInfo = await FileSystem.getInfoAsync(fileUri);
      if (fileInfo.exists) {
        console.log("Video found in cache");

        setLocalVideoUri(fileUri);
        setIsLoading(false);
        return;
      }

      const downloadResult = await FileSystem.downloadAsync(url, fileUri);
      console.log("Download completed:", downloadResult);

      if (downloadResult.status === 200) {
        setLocalVideoUri(downloadResult.uri);
      } else {
        throw new Error(`Download failed with status ${downloadResult.status}`);
      }
    } catch (err) {
      console.error("Error downloading video:", err);
      setError(err instanceof Error ? err.message : "Error downloading video");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const videoUrl = getVideoUrl();
    if (videoUrl) {
      downloadVideo(videoUrl);
    }

    // Limpiar caché al desmontar
    return () => {
      if (localVideoUri) {
        FileSystem.deleteAsync(localVideoUri, { idempotent: true }).catch(
          console.error
        );
      }
    };
  }, [data]);

  const finalVideoUri = localVideoUri || getVideoUrl();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{data.description}</Text>

      <View style={styles.videoContainer}>
        {finalVideoUri && !error && (
          <Video
            ref={videoRef}
            style={styles.video}
            source={{ uri: finalVideoUri }}
            useNativeControls
            shouldPlay={false}
            isMuted={true}
            resizeMode={undefined}
            isLooping={false}
            onPlaybackStatusUpdate={(status) => {
              if (status.isLoaded && status.didJustFinish) {
                setIsVideoComplete(true);
              }
            }}
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
                Original URL: {getVideoUrl() || "No URL"}
                {"\n"}
                Local URI: {localVideoUri || "No local file"}
              </Text>
            )}
          </View>
        )}
      </View>

      {(isVideoComplete || __DEV__) && onNext && (
        <TouchableOpacity
          style={styles.nextButton}
          onPress={() => {
            console.log("Navegando al siguiente desde VideoNodeView");
            onNext();
          }}
        >
          <Text style={styles.nextButtonText}>Continuar</Text>
        </TouchableOpacity>
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
  nextButton: {
    backgroundColor: theme.colors.primary,
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 20,
    marginHorizontal: 16,
  },
  nextButtonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
  },
});
