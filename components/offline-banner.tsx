import { StyleSheet, Text, View } from 'react-native';

import { useNetworkStatus } from '@/hooks/use-network-status';
import { useThemeColor } from '@/hooks/use-theme-color';

export function OfflineBanner() {
  const { isOffline } = useNetworkStatus();
  const backgroundColor = useThemeColor({ light: '#FDE68A', dark: '#78350F' }, 'background');
  const textColor = useThemeColor({ light: '#78350F', dark: '#FDE68A' }, 'text');

  if (!isOffline) {
    return null;
  }

  return (
    <View style={[styles.banner, { backgroundColor }]}>
      <Text style={[styles.text, { color: textColor }]}>{`You're offline — showing cached data`}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    fontSize: 13,
    fontWeight: '600',
  },
});