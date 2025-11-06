import { View, Text, StyleSheet, ScrollView } from "react-native";
import { theme } from "@/src/theme";
import { TextWithHyperlinks } from "@/components/ui/TextWithHyperlinks";

interface MealInfo {
  meal?: string;
  proteins?: string;
  notes?: string;
  activity?: string;
  duration?: string;
  intensity?: string;
}

interface DaySchedule {
  BREAKFAST?: MealInfo;
  LUNCH?: MealInfo;
  DINNER?: MealInfo;
  MORNING?: MealInfo;
  AFTERNOON?: MealInfo;
}

interface WeeklyPlan {
  [key: string]: DaySchedule;
}

interface RecipeNodeViewProps {
  data: {
    description: string;
    id: number;
    next_node_id: number | null;
    title: string;
    type: string;
    weekly_plan: WeeklyPlan;
  };
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

const SCHEDULE_NAMES = {
  // Comidas
  BREAKFAST: "Desayuno",
  LUNCH: "Almuerzo",
  DINNER: "Cena",
  // Ejercicios
  MORNING: "Mañana",
  AFTERNOON: "Tarde",
};

export const WeeklyRecipeNodeView: React.FC<RecipeNodeViewProps> = ({
  data,
}) => {
  // Determinar si es un plan de ejercicios basado en la presencia de 'activity' en el primer elemento
  const isExercisePlan =
    Object.values(data.weekly_plan)[0]?.MORNING?.activity !== undefined;

  const description = (
    <TextWithHyperlinks>{data.description}</TextWithHyperlinks>
  );

  const renderScheduleItem = (scheduleInfo: MealInfo, scheduleType: string) => {
    if (!scheduleInfo) return null;

    return (
      <View style={styles.scheduleContainer}>
        <View
          style={[
            styles.verticalLine,
            {
              backgroundColor:
                scheduleType === "MORNING" || scheduleType === "BREAKFAST"
                  ? theme.colors.primary
                  : theme.colors.text,
            },
          ]}
        />
        <View style={styles.scheduleContent}>
          <Text style={styles.scheduleType}>
            {SCHEDULE_NAMES[scheduleType as keyof typeof SCHEDULE_NAMES]}
          </Text>

          {isExercisePlan ? (
            <>
              <Text style={styles.activityText}>{scheduleInfo.activity}</Text>
              <View style={styles.detailsContainer}>
                <Text style={styles.durationText}>{scheduleInfo.duration}</Text>
                <Text style={styles.intensityText}>
                  {scheduleInfo.intensity}
                </Text>
              </View>
            </>
          ) : (
            <>
              <Text style={styles.mealText}>{scheduleInfo.meal}</Text>
              {scheduleInfo.proteins && (
                <Text style={styles.proteinsText}>{scheduleInfo.proteins}</Text>
              )}
              {scheduleInfo.notes && (
                <Text style={styles.notesText}>{scheduleInfo.notes}</Text>
              )}
            </>
          )}
        </View>
      </View>
    );
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>{data.title}</Text>
      {/* <Text style={styles.description}>{data.description}</Text> */}
      {description}

      {Object.entries(data.weekly_plan).map(([day, schedule], index) => (
        <View key={`day-${index}-${day}`} style={styles.dayContainer}>
          <Text style={styles.dayTitle}>
            {DAY_NAMES[day as keyof typeof DAY_NAMES]}
          </Text>
          {Object.entries(schedule).map(([scheduleType, scheduleInfo]) => (
            <View key={`${day}-${scheduleType}`}>
              {renderScheduleItem(scheduleInfo, scheduleType)}
            </View>
          ))}
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
    fontSize: theme.typography.sizes.headline1,
    fontWeight: "bold",
    color: theme.colors.text,
    marginBottom: 8,
    textAlign: "center",
  },
  description: {
    fontSize: theme.typography.sizes.body2,
    color: theme.colors.textSecondary,
    marginBottom: 16,
    textAlign: "center",
  },
  dayContainer: {
    marginBottom: 24,
    padding: 16,
    backgroundColor: theme.colors.card,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  dayTitle: {
    fontSize: theme.typography.sizes.subtitle,
    fontWeight: "bold",
    color: theme.colors.text,
    marginBottom: 12,
  },
  scheduleContainer: {
    flexDirection: "row",
    marginBottom: 12,
  },
  verticalLine: {
    width: 4,
    height: "100%",
    marginRight: 8,
    borderRadius: 2,
  },
  scheduleContent: {
    flex: 1,
  },
  scheduleType: {
    fontSize: theme.typography.sizes.body1,
    fontWeight: "bold",
    color: theme.colors.text,
    marginBottom: 4,
  },
  mealText: {
    fontSize: theme.typography.sizes.body2,
    color: theme.colors.textSecondary,
    marginBottom: 4,
  },
  activityText: {
    fontSize: theme.typography.sizes.body2,
    color: theme.colors.textSecondary,
    marginBottom: 4,
    fontWeight: "500",
  },
  detailsContainer: {
    flexDirection: "row",
    gap: 8,
  },
  durationText: {
    fontSize: theme.typography.sizes.caption,
    color: theme.colors.text,
    backgroundColor: theme.colors.primary,
    padding: 4,
    borderRadius: 4,
    overflow: "hidden",
  },
  intensityText: {
    fontSize: theme.typography.sizes.caption,
    color: theme.colors.text,
    backgroundColor: theme.colors.primary,
    padding: 4,
    borderRadius: 4,
    overflow: "hidden",
  },
  proteinsText: {
    fontSize: theme.typography.sizes.caption,
    color: theme.colors.text,
    backgroundColor: theme.colors.primary,
    padding: 4,
    borderRadius: 4,
    width: 100,
    textAlign: "center",
  },
  notesText: {
    fontSize: theme.typography.sizes.caption,
    color: theme.colors.textSecondary,
    fontStyle: "italic",
    marginTop: 4,
  },
});
