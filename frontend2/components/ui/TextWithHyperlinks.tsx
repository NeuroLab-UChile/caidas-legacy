import React from "react";
import { Text, StyleProp, TextStyle, Linking } from "react-native";

type TextWithHyperlinksProps = {
  children: string;
  style?: StyleProp<TextStyle>;
  linkStyle?: StyleProp<TextStyle>;
};

export const TextWithHyperlinks: React.FC<TextWithHyperlinksProps> = ({
  children,
  style = { fontSize: theme.typography.sizes.body1, color: "black" },
  linkStyle = { fontSize: theme.typography.sizes.body1, color: "blue", textDecorationLine: "underline" },
}) => {
  const regex = /\[(.*?)\]\((.*?)\)/g;
  const elements: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(children)) !== null) {
    if (match.index > lastIndex) {
      elements.push(children.substring(lastIndex, match.index));
    }
    const [fullMatch, text, url] = match;
    elements.push(
      <Text
        key={url + match.index}
        style={[
          {
            color: "blue",
            textDecorationLine: "underline",
            fontWeight: "bold",
          },
          linkStyle,
        ]}
        onPress={() => Linking.openURL(url)}
      >
        {text}
      </Text>
    );
    lastIndex = match.index + fullMatch.length;
  }
  if (lastIndex < children.length) {
    elements.push(children.substring(lastIndex));
  }

  return <Text style={style}>{elements}</Text>;
};
