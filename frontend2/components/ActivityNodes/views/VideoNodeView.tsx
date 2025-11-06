import { VideoPlayerView } from "@/components/VideoPlayer";
import { View, StyleSheet, Text } from "react-native";
import { theme } from "@/src/theme";
import { TextWithHyperlinks } from "@/components/ui/TextWithHyperlinks";

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

  const description = (
    <TextWithHyperlinks>{data.description}</TextWithHyperlinks>
  );

  return (
    <View style={styles.container}>
      <View style={{ marginBottom: 16 }}>
        <Text
          style={{
            fontSize: theme.typography.sizes.headline1,
            fontWeight: "bold",
            color: theme.colors.text,
            textAlign: "center",
          }}
        >
          {data.title}
        </Text>
      </View>

      {/* <Text
        style={{ color: theme.colors.text, marginBottom: 16, fontSize: theme.typography.sizes.body1 }}
      >
        {data.description}
      </Text> */}
      {description}

      {/* Video Player */}

      <View style={styles.videoCard}>
        <VideoPlayerView url={data.media_url} description={data.description} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 7,
  },
  videoCard: {
    backgroundColor: theme.colors.card,
    borderRadius: 24,
    padding: 5,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 4,
    // minHeight: 240,
  },
});
