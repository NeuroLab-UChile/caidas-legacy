// This file is a fallback for using MaterialIcons on Android and web.

import {
  Ionicons,
  // AntDesign,
  // MaterialIcons
} from "@expo/vector-icons"; // Add any additional icon families.
import { SymbolWeight } from "expo-symbols";
import React from "react";
import { OpaqueColorValue, StyleProp, ViewStyle } from "react-native";

// // Add your SFSymbol to MaterialIcons mappings here.
// const MAPPING = {
//   // See MaterialIcons here: https://icons.expo.fyi
//   // See SF Symbols in the SF Symbols app on Mac.
//   "house.fill": "home",
//   "paperplane.fill": "send",
//   "chevron.left.forwardslash.chevron.right": "code",
//   "chevron.right": "chevron-right",
//   "chevron.down": "expand-more",
// } as Partial<
//   Record<
//     import("expo-symbols").SymbolViewProps["name"],
//     React.ComponentProps<typeof MaterialIcons>["name"]
//   >
// >;

// Icon typings for each of the supported icon famlies.
// type AntDesignIcons = keyof typeof AntDesign.glyphMap;
// type MaterialDesignIcons = keyof typeof MaterialIcons.glyphMap;
type IonicIcons = keyof typeof Ionicons.glyphMap;
type IconNamespace = "ant" | "ionic" | "material";
type NamespacedIconName = `ionic:${IonicIcons}`;
// | `ant:${AntDesignIcons}`
// | `material:${MaterialDesignIcons}`;
type IconNames = IonicIcons | NamespacedIconName;

/**
 * An icon component that uses native SFSymbols on iOS, and MaterialIcons on Android and web. This ensures a consistent look across platforms, and optimal resource usage.
 *
 * Icon `name`s are based on SFSymbols and require manual mapping to MaterialIcons.
 */
export function IconSymbol({
  name,
  size = 24,
  color,
  style,
}: {
  // name: IconSymbolName;
  // name: keyof typeof MaterialIcons.glyphMap;
  // name: React.ComponentProps<typeof MaterialIcons>["name"];
  name: IconNames; // Use the union type for namespaced icons.
  size?: number;
  color: string | OpaqueColorValue;
  style?: StyleProp<ViewStyle>;
  weight?: SymbolWeight;
}) {
  // return (
  //   <MaterialIcons
  //     color={color}
  //     size={size}
  //     // name={MAPPING[name]}
  //     name={name}
  //     style={style}
  //   />
  // );

  // console.log(name);

  // To allow for namespaced icons, eg. "ant:caretdown"
  if (name.includes(":")) {
    // console.log("Namespaced icon detected:", name);
    const [namespace, iconName] = name.split(":") as [IconNamespace, string];
    switch (namespace) {
      case "ionic":
        return (
          <Ionicons
            name={iconName as IonicIcons}
            size={size}
            color={color}
            style={style}
          />
        );
      // case "ant":
      //   return (
      //     <AntDesign
      //       name={iconName as AntDesignIcons}
      //       size={size}
      //       color={color}
      //       style={style}
      //     />
      //   );
      // case "material":
      //   return (
      //     <MaterialIcons
      //       name={iconName as MaterialDesignIcons}
      //       size={size}
      //       color={color}
      //       style={style}
      //     />
      //   );
      default:
        throw new Error(`Unsupported icon namespace: ${namespace}`);
    }
  }

  return (
    <Ionicons
      name={name as IonicIcons}
      size={size}
      color={color}
      style={style}
    />
  );
}
