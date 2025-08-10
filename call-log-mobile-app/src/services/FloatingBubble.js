// Optional floating bubble indicator (Android only)
// Gracefully no-op if library is not installed
import { Platform } from 'react-native';

let Bubble = null;
try {
  // eslint-disable-next-line global-require
  Bubble = require('react-native-floating-bubble');
} catch (_) {
  Bubble = null;
}

export async function showBubble() {
  if (Platform.OS !== 'android' || !Bubble) return;
  try {
    const granted = await Bubble.requestPermission();
    if (granted) {
      await Bubble.showFloatingBubble(80, 200);
    }
  } catch (_) {}
}


