import { Text, View } from "react-native";

interface VideoNodeViewProps {
  data: any;
}

export const VideoNodeView: React.FC<VideoNodeViewProps> = ({ data }) => {
  return (
    <View>
      <Text>{data.description}</Text>
    </View>
  );
};
