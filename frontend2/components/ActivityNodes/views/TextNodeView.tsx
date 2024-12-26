import { Text, View } from "react-native";

interface TextNodeViewProps {
  data: any;
}

export const TextNodeView: React.FC<TextNodeViewProps> = ({ data }) => {
  return (
    <View>
      <Text>{data.description}</Text>
    </View>
  );
};
