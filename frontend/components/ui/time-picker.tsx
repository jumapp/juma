import { Platform, StyleSheet, ViewStyle } from "react-native";
import { useTheme } from "@/providers/theme-provider";

interface TimePickerProps {
  value?: string;
  onChange?: (time: string) => void;
  minuteInterval?: number;
  style?: ViewStyle;
  [key: string]: any;
}

/**
 * Web implementation - uses HTML input[type=time]
 * to avoid the @react-native-community/datetimepicker web warning.
 */
function TimePickerWeb({
  value,
  onChange,
  minuteInterval = 5,
  style,
  ...rest
}: TimePickerProps) {
  const { colors } = useTheme();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(e.target.value);
    }
  };

  // Parse string time to HTML time input format (HH:MM)
  const timeValue = value || "";

  // Flatten the RN style array into a single object and convert RN-only
  // style props into valid CSS properties. Passing a raw style array (or
  // RN-specific keys like paddingVertical) to a DOM element breaks React's
  // DOM reconciliation with:
  // Failed to set an indexed property on CSSStyleDeclaration.
  const flatStyle = (StyleSheet.flatten([styles.timeInput, style]) || {}) as Record<
    string,
    any
  >;
  const { paddingVertical, paddingHorizontal, ...cssStyle } = flatStyle;

  const domStyle = {
    ...cssStyle,
    ...(paddingVertical != null
      ? { paddingTop: paddingVertical, paddingBottom: paddingVertical }
      : {}),
    ...(paddingHorizontal != null
      ? { paddingLeft: paddingHorizontal, paddingRight: paddingHorizontal }
      : {}),
  } as React.CSSProperties;

  return (
    <input
      type="time"
      value={timeValue}
      onChange={handleChange}
      step={(minuteInterval || 5) * 60}
      style={domStyle}
      {...rest}
    />
  );
}

/**
 * Native implementation - uses @react-native-community/datetimepicker
 */
function TimePickerNative({
  value,
  onChange,
  minuteInterval = 5,
  ...rest
}: TimePickerProps) {
  // Parse string time HH:MM to Date object for native DateTimePicker
  const now = new Date();
  let date = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);

  if (value) {
    const [hours, minutes] = value.split(":").map(Number);
    if (!isNaN(hours) && !isNaN(minutes)) {
      date.setHours(hours, minutes);
    }
  }

  const handleChange = (event: any, selectedDate?: Date) => {
    if (selectedDate && onChange) {
      const hours = selectedDate.getHours().toString().padStart(2, "0");
      const minutes = selectedDate.getMinutes().toString().padStart(2, "0");
      onChange(hours + ":" + minutes);
    }
  };

  return (
    <DateTimePicker
      value={date}
      mode={"time" as const}
      display={"spinner" as const}
      onChange={handleChange}
      minuteInterval={
        (minuteInterval || 5) as 1 | 2 | 3 | 4 | 5 | 6 | 10 | 12 | 15 | 20 | 30
      }
      {...rest}
    />
  );
}

import DateTimePicker from "@react-native-community/datetimepicker";

/**
 * Platform-aware TimePicker component.
 * - Web: HTML <input type=time>
 * - Native (iOS/Android): @react-native-community/datetimepicker
 */
export function TimePicker(props: TimePickerProps) {
  if (Platform.OS === "web") {
    return <TimePickerWeb {...props} />;
  }
  return <TimePickerNative {...props} />;
}

const styles = StyleSheet.create({
  timeInput: {
    width: "100%",
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: "#d1d5db",
    borderRadius: 8,
    fontSize: 16,
    fontFamily: "system-ui",
    backgroundColor: "#fff",
    color: "#1f2937",
    cursor: "pointer",
    minHeight: 44,
  },
});