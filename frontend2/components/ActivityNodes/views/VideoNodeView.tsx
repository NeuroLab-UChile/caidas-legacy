import { VideoPlayerView } from "@/components/VideoPlayer";
import { View, StyleSheet } from "react-native";
import { theme } from "@/src/theme";

interface VideoNodeViewProps {
  data: {
    description: string;
    media_url: string;
  };
  onNext?: () => void;
}

export const VideoNodeView: React.FC<VideoNodeViewProps> = ({ data, onNext }) => {
  return (
    <View style={styles.container}>
      <View style={styles.videoCard}>
        <VideoPlayerView 
          url={data.media_url}
          description={data.description}
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
  videoCard: {
    backgroundColor: theme.colors.card,
    borderRadius: 24,
    padding: 20,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 4,
    minHeight: 240,
  },
});
