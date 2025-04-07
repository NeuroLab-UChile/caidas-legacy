import { VideoPlayerView } from "@/components/VideoPlayer/VideoPlayerView";
import { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, Platform } from "react-native";
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

  const handleVideoComplete = () => {
    setIsComplete(true);
  };

  return (
    <View style={styles.container}>
      <View style={styles.videoCard}>
    
        
        <View style={styles.videoWrapper}>
          <VideoPlayerView 
            url={data.media_url}
            showDebug={__DEV__}
            onComplete={handleVideoComplete}
            description={data.description}
          />
        </View>

        <TouchableOpacity 
          style={[styles.nextButton, isComplete && styles.nextButtonComplete]} 
          onPress={onNext}
        >
          <Text style={styles.nextButtonText}>
            {isComplete ? "Continuar" : "Omitir"}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  videoCard: {
    backgroundColor: theme.colors.card,
    borderRadius: 24,
    padding: 20,
    ...Platform.select({
      ios: {
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.1,
        shadowRadius: 12,
      },
      android: {
        elevation: 4,
      },
    }),
  },
  description: {
    fontSize: 16,
    color: theme.colors.text,
    marginBottom: 16,
    lineHeight: 24,
  },
  videoWrapper: {
    borderRadius: 16,
    overflow: 'hidden',
    backgroundColor: theme.colors.background,
    marginBottom: 16,
  },
  nextButton: {
    backgroundColor: `${theme.colors.primary}10`,
    padding: 12,
    borderRadius: 12,
    alignItems: "center",
  },
  nextButtonComplete: {
    backgroundColor: theme.colors.primary,
  },
  nextButtonText: {
    color: theme.colors.primary,
    fontSize: 14,
    fontWeight: "600",
  },
  nextButtonTextComplete: {
    color: theme.colors.background,
  },
});
