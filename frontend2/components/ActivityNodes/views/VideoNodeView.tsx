import { VideoPlayerView } from "@/components/VideoPlayer";
import { View, StyleSheet, Text } from "react-native";
import { theme } from "@/src/theme";

interface VideoNodeViewProps {
  data: {
    title: string;
    description: string;
    media_url: string;
  };
  onNext?: () => void;
}

export const VideoNodeView: React.FC<VideoNodeViewProps> = ({
  data,
  onNext,
}) => {
  console.log("VideoNodeView data:", data);

  return (
    <View style={styles.container}>
      <View style={{ marginBottom: 16 }}>
        <Text
          style={{
            fontSize: 24,
            fontWeight: "bold",
            color: theme.colors.text,
            textAlign: "center",
          }}
        >
          {data.title}
        </Text>
      </View>

      <Text style={{ color: theme.colors.text, marginBottom: 16, fontSize: 16 }}>
        {data.description}
      </Text>

      <View style={styles.videoCard}>
        <VideoPlayerView url={data.media_url} description={data.description} />
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
