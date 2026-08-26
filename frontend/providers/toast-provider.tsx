import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
} from "react";
import {
  Animated,
  StyleSheet,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useTheme } from "@/providers/theme-provider";
import { Text } from "@/components/ui/text";

export type ToastType = "success" | "error" | "info" | "warning";

export interface ToastOptions {
  message: string;
  type?: ToastType;
  duration?: number;
}

export interface ToastContextValue {
  showToast: (options: ToastOptions | string) => void;
  hideToast: () => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const { colors, radii, shadows, spacing } = useTheme();
  const insets = useSafeAreaInsets();
  const [toast, setToast] = useState<ToastOptions | null>(null);
  const opacity = useState(new Animated.Value(0))[0];

  const hideToast = useCallback(() => {
    Animated.timing(opacity, {
      toValue: 0,
      duration: 200,
      useNativeDriver: true,
    }).start(() => setToast(null));
  }, [opacity]);

  const showToast = useCallback(
    (options: ToastOptions | string) => {
      const opts: ToastOptions =
        typeof options === "string" ? { message: options, type: "info" } : options;
      
      setToast(opts);
      Animated.timing(opacity, {
        toValue: 1,
        duration: 200,
        useNativeDriver: true,
      }).start();

      const duration = opts.duration ?? 3000;
      setTimeout(() => {
        hideToast();
      }, duration);
    },
    [opacity, hideToast]
  );

  const getBackgroundColor = (type?: ToastType): string => {
    switch (type) {
      case "success":
        return colors.success;
      case "error":
        return colors.error;
      case "warning":
        return colors.warning;
      case "info":
      default:
        return colors.surfaceVariant;
    }
  };

  const getTextColor = (type?: ToastType): string => {
    switch (type) {
      case "success":
      case "error":
      case "warning":
        return "#ffffff";
      case "info":
      default:
        return colors.text;
    }
  };

  return (
    <ToastContext.Provider value={{ showToast, hideToast }}>
      {children}
      {toast ? (
        <Animated.View
          pointerEvents="none"
          style={[
            styles.container,
            {
              top: insets.top + spacing.md,
              opacity,
            },
          ]}
        >
          <View
            style={[
              styles.toast,
              {
                backgroundColor: getBackgroundColor(toast.type),
                borderRadius: radii.md,
                paddingHorizontal: spacing.lg,
                paddingVertical: spacing.md,
                ...shadows.md,
              },
            ]}
          >
            <Text
              variant="bodySmallBold"
              style={{ color: getTextColor(toast.type), textAlign: "center" }}
            >
              {toast.message}
            </Text>
          </View>
        </Animated.View>
      ) : null}
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const context = useContext(ToastContext);
  if (!context) {
    return {
      showToast: () => {},
      hideToast: () => {},
    };
  }
  return context;
}

const styles = StyleSheet.create({
  container: {
    position: "absolute",
    left: 20,
    right: 20,
    alignItems: "center",
    zIndex: 9999,
  },
  toast: {
    minWidth: 200,
    maxWidth: "100%",
    alignItems: "center",
    justifyContent: "center",
  },
});
