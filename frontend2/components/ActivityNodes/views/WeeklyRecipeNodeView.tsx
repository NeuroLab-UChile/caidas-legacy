import React from "react";
import { View, Text, StyleSheet, ScrollView } from "react-native";
import { theme } from "@/src/theme";

interface MealInfo {
  meal: string;
  proteins: string;
  notes?: string;
}

interface DayMeals {
  BREAKFAST?: MealInfo;
  LUNCH?: MealInfo;
  DINNER?: MealInfo;
}

interface WeeklyPlan {
  [key: string]: DayMeals;
}

interface RecipeNodeViewProps {
  data:
    | {
        description: string;
        id: number;
        next_node_id: number | null;
        title: string;
        type: string;
        weekly_plan: WeeklyPlan;
      }
    | Array<any>;
}

const DAY_NAMES = {
  MON: "Lunes",
  TUE: "Martes",
  WED: "Miércoles",
  THU: "Jueves",
  FRI: "Viernes",
  SAT: "Sábado",
  SUN: "Domingo",
};

const MEAL_NAMES = {
  BREAKFAST: "Desayuno",
  LUNCH: "Almuerzo",
  DINNER: "Cena",
};

export const WeeklyRecipeNodeView: React.FC<RecipeNodeViewProps> = ({
  data,
}) => {
  const nodeData = data as {
    description: string;
    id: number;
    next_node_id: number | null;
    title: string;
    type: string;
    weekly_plan: WeeklyPlan;
  };
  console.log("recipe node data", nodeData);
  const weeklyPlan = nodeData.weekly_plan;

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>{nodeData.title}</Text>
      <Text style={styles.description}>{nodeData.description}</Text>

      {Object.entries(weeklyPlan).map(([day, meals]) => (
        <View key={day} style={styles.dayContainer}>
          <Text style={styles.dayTitle}>
            {DAY_NAMES[day as keyof typeof DAY_NAMES]}
          </Text>
          {Object.entries(meals as Record<string, any>).map(
            ([mealType, mealInfo]) => (
              <View key={mealType} style={styles.mealContainer}>
                {/* Línea vertical de color */}
                <View
                  style={[
                    styles.verticalLine,
                    mealType === "BREAKFAST" && {
                      backgroundColor: theme.colors.primary,
                    },
                    mealType === "LUNCH" && {
                      backgroundColor: theme.colors.text,
                    },
                    mealType === "DINNER" && {
                      backgroundColor: theme.colors.primary,
                    },
                  ]}
                />
                {/* Contenido */}
                <View style={styles.mealContent}>
                  <Text style={styles.mealType}>
                    {MEAL_NAMES[mealType as keyof typeof MEAL_NAMES]}
                  </Text>
                  <Text style={styles.mealText}>{mealInfo.meal}</Text>
                  <Text style={styles.proteinsText}>{mealInfo.proteins}</Text>
                </View>
              </View>
            )
          )}
        </View>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: theme.colors.background,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: theme.colors.text,
    marginBottom: 8,
    textAlign: "center",
  },
  description: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 16,
    textAlign: "center",
  },
  dayContainer: {
    marginBottom: 24,
    padding: 8,
    backgroundColor: theme.colors.card,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  dayTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: theme.colors.text,
    marginBottom: 12,
  },
  mealContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 12,
  },
  verticalLine: {
    width: 4,
    height: "100%",
    marginRight: 8,
    borderRadius: 2,
  },
  mealContent: {
    flex: 1,
  },
  mealType: {
    fontSize: 16,
    fontWeight: "bold",
    color: theme.colors.text,
    marginBottom: 4,
  },
  mealText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 4,
  },
  proteinsText: {
    fontSize: 12,
    color: theme.colors.text,
    backgroundColor: theme.colors.primary,
    padding: 4,
    borderRadius: 4,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "600",
    width: 100,
  },
});
