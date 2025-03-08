import  { useState, useEffect } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Image, ActivityIndicator } from "react-native";
import { VideoView, useVideoPlayer, type StatusChangeEventPayload } from "expo-video";
import { useEventListener } from "expo";
import { theme } from "@/src/theme";

interface VideoNodeViewProps {
  data: {
    description: string;
    media_url: string;
  };
  onNext?: () => void;
}

export const VideoNodeView: React.FC<VideoNodeViewProps> = ({ data, onNext }) => {
  const [showVideo, setShowVideo] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // **Optimización del buffer y calidad**
  const player = useVideoPlayer(data.media_url, (player) => {
    player.loop = false;
    player.volume = 1.0;
    player.muted = true; // 🔥 Activar mute puede mejorar la reproducción automática en iOS
    player.timeUpdateEventInterval = 0.5; // 🔥 Reduce el tiempo de actualización para mejor respuesta
    player.bufferOptions = {
      minBufferForPlayback: 1, // 🔥 Se inicia con menos buffer
      preferredForwardBufferDuration: 10, // 🔥 Reduce la espera por buffer
    };
  });

  // **📌 Detectar cuando el video está listo**
  useEventListener(player, "statusChange", async ({ status }: StatusChangeEventPayload) => {
    if (status === "readyToPlay") {
      console.log("✅ Video listo para reproducir");
      setIsLoading(false);
      try {
        await player.play();
      } catch (err) {
        console.warn("🚨 No se pudo iniciar automáticamente. Esperando interacción.");
      }
    }
  });

  // **📌 Detectar cuando el video comienza a reproducirse**
  useEventListener(player, "playingChange", ({ isPlaying }) => {
    if (isPlaying) {
      console.log("▶️ Video en reproducción");
      setIsLoading(false);
    }
  });

  const handleVideoPress = async () => {
    try {
      setShowVideo(true);
      setIsLoading(true);
      setError(null);
      await player.play();
    } catch (err) {
      console.error("❌ Error al iniciar el video:", err);
      setError("No se pudo cargar el video.");
      setShowVideo(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{data.description}</Text>

      <View style={styles.videoContainer}>
        {!showVideo ? (
          <TouchableOpacity style={styles.thumbnailContainer} onPress={handleVideoPress}>
            <Image source={{ uri: `${data.media_url}?thumb=1` }} style={styles.video} resizeMode="contain" />
            <View style={styles.playButtonOverlay}>
              {error ? (
                <View style={styles.errorContainer}>
                  <Text style={styles.errorText}>{error}</Text>
                  <Text style={styles.retryText}>Toca para reintentar</Text>
                </View>
              ) : (
                <Text style={styles.playButtonText}>▶️</Text>
              )}
            </View>
          </TouchableOpacity>
        ) : (
          <View style={styles.videoWrapper}>
            <VideoView
              style={styles.video}
              player={player}
              contentFit="contain"
              nativeControls
              onFullscreenEnter={() => console.log("Entró a pantalla completa")}
              onFullscreenExit={() => console.log("Salió de pantalla completa")}
            />
            {isLoading && (
              <View style={styles.loadingOverlay}>
                <ActivityIndicator size="large" color={theme.colors.primary} />
                <Text style={styles.loadingText}>Cargando video...</Text>
              </View>
            )}
          </View>
        )}
      </View>

      <View style={styles.debugContainer}>
        <Text style={styles.debugText}>Estado: {player.status}</Text>
      </View>

      {(isComplete || __DEV__) && onNext && (
        <TouchableOpacity style={[styles.nextButton, isComplete && styles.nextButtonComplete]} onPress={onNext}>
          <Text style={styles.nextButtonText}>{isComplete ? "Continuar ✓" : "Continuar"}</Text>
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
    width: "100%",
    aspectRatio: 16 / 9,
    backgroundColor: "#000",
    borderRadius: 8,
    overflow: "hidden",
  },
  video: {
    width: "100%",
    height: "100%",
  },
  thumbnailContainer: {
    width: "100%",
    height: "100%",
    justifyContent: "center",
    alignItems: "center",
  },
  playButtonOverlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(0,0,0,0.3)",
  },
  playButtonText: {
    fontSize: 40,
  },
  nextButton: {
    backgroundColor: theme.colors.primary,
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 20,
  },
  nextButtonComplete: {
    backgroundColor: theme.colors.success,
  },
  nextButtonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
  },
  errorContainer: {
    justifyContent: "center",
    alignItems: "center",
  },
  errorText: {
    color: theme.colors.error,
    marginBottom: 8,
  },
  retryText: {
    color: theme.colors.text,
  },
  videoWrapper: {
    position: "relative",
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(0,0,0,0.5)",
  },
  loadingText: {
    color: "white",
    marginTop: 8,
  },
  debugContainer: {
    padding: 10,
    backgroundColor: "#f0f0f0",
    marginTop: 10,
  },
  debugText: {
    fontSize: 12,
    color: "#666",
  },
});
