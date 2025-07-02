// Important note: this Video player doesn't support high resolution videos.
// If it's failing, reduce the video resolution with:
// ffmpeg -i input.mp4 -c:v libx264 -profile:v main -preset fast -crf 23 -vf scale=-2:1080 output.mp4

import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { VideoView, useVideoPlayer } from "expo-video";
import { useEventListener } from "expo";
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

  useEventListener(player, "statusChange", ({ status, error }) => {
    console.log("Player status changed: ", status);
    if (error) {
      console.error("Player error: ", error);
    }
  });

  return (
    <View style={styles.container}>
      {/* This text was repeated with an external card */}
      {/* {description && <Text style={styles.title}>{description}</Text>} */}

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
