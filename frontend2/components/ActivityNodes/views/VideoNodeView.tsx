import { VideoPlayerView } from "@/components/VideoPlayer/VideoPlayerView";
import { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { theme } from "@/src/theme";

interface VideoNodeViewProps {
  data: {
    description: string;
    media_url: string;
  };
  onNext?: () => void;
}

export const VideoNodeView: React.FC<VideoNodeViewProps> = ({ data, onNext }) => {
  const [isComplete, setIsComplete] = useState(false);

  return (
    <View style={styles.container}>
      <VideoPlayerView 
        url={data.media_url}
        description={data.description}
        showDebug={__DEV__}
      />

      {(isComplete || __DEV__) && onNext && (
        <TouchableOpacity 
          style={[styles.nextButton, isComplete && styles.nextButtonComplete]} 
          onPress={onNext}
        >
          <Text style={styles.nextButtonText}>
            {isComplete ? "Continuar ✓" : "Continuar"}
          </Text>
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
