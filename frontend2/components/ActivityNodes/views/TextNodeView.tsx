import { Text, View } from "react-native";
import { TextWithHyperlinks } from "@/components/ui/TextWithHyperlinks";

interface TextNodeViewProps {
  data: any;
}

export const TextNodeView: React.FC<TextNodeViewProps> = ({ data }) => {
  const description = (
    <TextWithHyperlinks>{data.description}</TextWithHyperlinks>
  );
  return (
    <View>
      <Text
        style={{
          fontSize: 24,
          fontWeight: "bold",
          marginBottom: 8,
          textAlign: "center",
        }}
      >
        {data.title}
      </Text>

      {description}
    </View>
  );
};
