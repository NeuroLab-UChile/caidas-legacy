import { Text, View } from "react-native";
import { TextWithHyperlinks } from "@/components/ui/TextWithHyperlinks";
import { theme } from "@/src/theme";

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
          fontSize: theme.typography.sizes.headline1,
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
