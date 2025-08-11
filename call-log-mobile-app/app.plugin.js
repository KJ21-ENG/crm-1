// Expo config plugin to ensure the Background Actions service is declared
const { withAndroidManifest } = require('@expo/config-plugins');

function ensureArray(v) {
  if (!v) return [];
  return Array.isArray(v) ? v : [v];
}

function hasService(application, serviceName) {
  const services = ensureArray(application.service);
  return services.some((s) => s['$']?.['android:name'] === serviceName);
}

function addService(application, attrs) {
  const services = ensureArray(application.service);
  services.push({ $: attrs });
  application.service = services;
}

module.exports = function withBackgroundActionsService(config) {
  return withAndroidManifest(config, (config) => {
    const manifest = config.modResults;
    if (!manifest?.manifest?.application?.[0]) return config;

    const app = manifest.manifest.application[0];

    // Ensure the foreground data sync permission (if prebuild missed it)
    manifest.manifest['uses-permission'] = ensureArray(manifest.manifest['uses-permission']);
    const permValue = 'android.permission.FOREGROUND_SERVICE_DATA_SYNC';
    const hasPerm = manifest.manifest['uses-permission'].some(
      (p) => p?.$?.['android:name'] === permValue
    );
    if (!hasPerm) {
      manifest.manifest['uses-permission'].push({ $: { 'android:name': permValue } });
    }

    // Add BackgroundActions headless task service if missing
    const serviceName = 'com.zoontek.rnbackgroundactions.HeadlessTaskService';
    if (!hasService(app, serviceName)) {
      addService(app, {
        'android:name': serviceName,
        'android:exported': 'false',
        'android:foregroundServiceType': 'dataSync',
      });
    }

    return config;
  });
};




