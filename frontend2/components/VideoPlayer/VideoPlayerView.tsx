import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { VideoView, useVideoPlayer } from "expo-video";
import { theme } from "@/src/theme";

interface VideoPlayerViewProps {
  url: string;
  description?: string;
}

export const VideoPlayerView: React.FC<VideoPlayerViewProps> = ({ 
  url, 
  description,
}) => {
  const player = useVideoPlayer(url, (player) => {
    player.loop = false;
    player.volume = 1.0;
    player.muted = false;
  });

  return (
    <View style={styles.container}>
      {description && <Text style={styles.title}>{description}</Text>}

      <View style={styles.videoContainer}>
        <VideoView
          style={styles.video}
          player={player}
          contentFit="contain"
          nativeControls={true}
        />
      </View>
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
});