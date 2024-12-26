import React, { useState, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";
import { Video, ResizeMode, AVPlaybackStatus } from "expo-av";
import { MaterialIcons } from "@expo/vector-icons";

interface VideoNodeViewProps {
  data: {
    title: string;
    description: string;
    video: string;
    thumbnail: string;
    duration?: number;
  };
}

interface VideoStatus {
  isPlaying?: boolean;
  // Otros campos que puedas necesitar del estado del video
}

export const VideoNodeView: React.FC<VideoNodeViewProps> = ({ data }) => {
  const videoRef = useRef<Video | null>(null);
  const [status, setStatus] = useState<VideoStatus>({});
  const [isLoading, setIsLoading] = useState(true);

  const onPlaybackStatusUpdate = (status: AVPlaybackStatus) => {
    if (status.isLoaded) {
      setStatus({
        isPlaying: status.isPlaying,
      });
      setIsLoading(false);
    }
  };

  const handlePlayPause = async () => {
    if (!videoRef.current) return;

    if (status.isPlaying) {
      await videoRef.current.pauseAsync();
    } else {
      await videoRef.current.playAsync();
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{data.title}</Text>

      <View style={styles.videoContainer}>
        {isLoading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#FFCC00" />
          </View>
        )}

        <Video
          ref={videoRef}
          style={styles.video}
          source={{ uri: data.video }}
          useNativeControls
          resizeMode={ResizeMode.CONTAIN}
          onPlaybackStatusUpdate={onPlaybackStatusUpdate}
        />

        <View style={styles.controls}>
          <TouchableOpacity onPress={handlePlayPause}>
            <MaterialIcons
              name={status.isPlaying ? "pause" : "play-arrow"}
              size={32}
              color="#FFCC00"
            />
          </TouchableOpacity>
        </View>
      </View>

      <Text style={styles.description}>{data.description}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 16,
  },
  videoContainer: {
    width: "100%",
    aspectRatio: 16 / 9,
    backgroundColor: "#000",
    borderRadius: 8,
    overflow: "hidden",
    marginBottom: 16,
  },
  video: {
    flex: 1,
    width: "100%",
  },
  poster: {
    resizeMode: "cover",
  },
  loadingContainer: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(0,0,0,0.3)",
  },
  controls: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    padding: 16,
    backgroundColor: "rgba(0,0,0,0.5)",
  },
  description: {
    fontSize: 16,
    lineHeight: 24,
    color: "#666",
  },
});
