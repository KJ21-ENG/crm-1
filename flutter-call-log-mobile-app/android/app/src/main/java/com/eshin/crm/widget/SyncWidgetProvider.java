package com.eshin.crm.widget;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.Intent;
import android.content.ComponentName;
import android.content.SharedPreferences;
import android.widget.Toast;
import io.flutter.embedding.engine.FlutterEngine;
import io.flutter.embedding.engine.dart.DartExecutor;
import io.flutter.view.FlutterMain;
import io.flutter.plugin.common.MethodChannel;
import android.widget.RemoteViews;
import android.text.format.DateFormat;
import java.text.SimpleDateFormat;
import java.util.TimeZone;
import java.util.Date;

import com.eshin.crm.R;

public class SyncWidgetProvider extends AppWidgetProvider {

    private static final String ACTION_MANUAL_SYNC = "com.eshin.crm.ACTION_WIDGET_MANUAL_SYNC";
    private static final String ACTION_TOGGLE_BG = "com.eshin.crm.ACTION_WIDGET_TOGGLE_BG";

    @Override
    public void onUpdate(Context context, AppWidgetManager appWidgetManager, int[] appWidgetIds) {
        for (int appWidgetId : appWidgetIds) {
            RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.widget_layout);
            Intent syncIntent = new Intent();
            syncIntent.setAction(ACTION_MANUAL_SYNC);
            syncIntent.setComponent(new ComponentName(context.getPackageName(), SyncWidgetProvider.class.getName()));
            syncIntent.setPackage(context.getPackageName());
            PendingIntent syncPending = PendingIntent.getBroadcast(context, 0, syncIntent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            views.setOnClickPendingIntent(R.id.widget_sync_now, syncPending);

            Intent toggleIntent = new Intent();
            toggleIntent.setAction(ACTION_TOGGLE_BG);
            toggleIntent.setComponent(new ComponentName(context.getPackageName(), SyncWidgetProvider.class.getName()));
            toggleIntent.setPackage(context.getPackageName());
            PendingIntent togglePending = PendingIntent.getBroadcast(context, 1, toggleIntent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            views.setOnClickPendingIntent(R.id.widget_toggle_bg, togglePending);

            // Set last sync text from SharedPreferences
            String lastSyncText = getLastSyncText(context);
            views.setTextViewText(R.id.widget_last_sync, lastSyncText);
            appWidgetManager.updateAppWidget(appWidgetId, views);
        }
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        super.onReceive(context, intent);
        if (intent == null) return;
        String action = intent.getAction();
        if ("com.eshin.crm.ACTION_WIDGET_REFRESH".equals(action)) {
            // Refresh widget display from SharedPreferences
            AppWidgetManager m = AppWidgetManager.getInstance(context);
            ComponentName c = new ComponentName(context, SyncWidgetProvider.class);
            RemoteViews rv = new RemoteViews(context.getPackageName(), R.layout.widget_layout);
            rv.setTextViewText(R.id.widget_last_sync, getLastSyncText(context));
            m.updateAppWidget(c, rv);
            return;
        }
        if (ACTION_MANUAL_SYNC.equals(action)) {
            // Update widget UI to indicate request
            AppWidgetManager mgr = AppWidgetManager.getInstance(context);
            ComponentName cn = new ComponentName(context, SyncWidgetProvider.class);
            RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.widget_layout);
            views.setTextViewText(R.id.widget_last_sync, "Sync requested");
            mgr.updateAppWidget(cn, views);
            Toast.makeText(context, "Sync requested", Toast.LENGTH_SHORT).show();
            // Try to forward to a headless Flutter engine so the sync runs without opening UI
            try {
                FlutterMain.startInitialization(context.getApplicationContext());
                FlutterEngine engine = new FlutterEngine(context.getApplicationContext());
                // Run the 'widgetBackgroundMain' Dart entrypoint so we don't need UI
                engine.getDartExecutor().executeDartEntrypoint(
                    DartExecutor.DartEntrypoint.createDefault()
                );
                MethodChannel channel = new MethodChannel(engine.getDartExecutor().getBinaryMessenger(), "crm/widget");
                channel.invokeMethod("manualSync", null, new MethodChannel.Result() {
                    @Override
                    public void success(Object result) {
                        // After sync, refresh last sync text
                        try {
                            String text = getLastSyncText(context);
                            AppWidgetManager m = AppWidgetManager.getInstance(context);
                            ComponentName c = new ComponentName(context, SyncWidgetProvider.class);
                            RemoteViews rv = new RemoteViews(context.getPackageName(), R.layout.widget_layout);
                            rv.setTextViewText(R.id.widget_last_sync, text);
                            m.updateAppWidget(c, rv);
                        } catch (Exception ignore) {}
                        // destroy engine after work
                        engine.destroy();
                    }

                    @Override
                    public void error(String errorCode, String errorMessage, Object errorDetails) {
                        engine.destroy();
                    }

                    @Override
                    public void notImplemented() {
                        engine.destroy();
                    }
                });
            } catch (Exception ex) {
                // ignore - fallback already updates widget UI
            }
        } else if (ACTION_TOGGLE_BG.equals(action)) {
            AppWidgetManager mgr = AppWidgetManager.getInstance(context);
            ComponentName cn = new ComponentName(context, SyncWidgetProvider.class);
            RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.widget_layout);
            views.setTextViewText(R.id.widget_last_sync, "Toggle background requested");
            mgr.updateAppWidget(cn, views);
            Toast.makeText(context, "Toggle background requested", Toast.LENGTH_SHORT).show();
            try {
                FlutterMain.startInitialization(context.getApplicationContext());
                FlutterEngine engine = new FlutterEngine(context.getApplicationContext());
                engine.getDartExecutor().executeDartEntrypoint(DartExecutor.DartEntrypoint.createDefault());
                MethodChannel channel = new MethodChannel(engine.getDartExecutor().getBinaryMessenger(), "crm/widget");
                channel.invokeMethod("toggleBackground", null, new MethodChannel.Result() {
                    @Override
                    public void success(Object result) {
                        // Update text to current last sync (may be unchanged), then destroy
                        try {
                            String text = getLastSyncText(context);
                            AppWidgetManager m = AppWidgetManager.getInstance(context);
                            ComponentName c = new ComponentName(context, SyncWidgetProvider.class);
                            RemoteViews rv = new RemoteViews(context.getPackageName(), R.layout.widget_layout);
                            rv.setTextViewText(R.id.widget_last_sync, text);
                            m.updateAppWidget(c, rv);
                        } catch (Exception ignore) {}
                        engine.destroy();
                    }

                    @Override
                    public void error(String errorCode, String errorMessage, Object errorDetails) {
                        engine.destroy();
                    }

                    @Override
                    public void notImplemented() {
                        engine.destroy();
                    }
                });
            } catch (Exception ex) {
                // ignore
            }
        }
    }

    private static String getLastSyncText(Context context) {
        try {
            SharedPreferences prefs = context.getSharedPreferences("FlutterSharedPreferences", Context.MODE_PRIVATE);
            long lastSync = 0L;
            if (prefs.contains("flutter.last_call_log_sync")) {
                try { lastSync = prefs.getLong("flutter.last_call_log_sync", 0L); } catch (ClassCastException e) {
                    try { String v = prefs.getString("flutter.last_call_log_sync", null); if (v != null) lastSync = Long.parseLong(v); } catch (Exception ignore) {}
                }
            }
            if (lastSync <= 0L && prefs.contains("last_call_log_sync")) {
                try { lastSync = prefs.getLong("last_call_log_sync", 0L); } catch (ClassCastException e) {
                    try { String v = prefs.getString("last_call_log_sync", null); if (v != null) lastSync = Long.parseLong(v); } catch (Exception ignore) {}
                }
            }
            if (lastSync > 0L) {
                // Normalize epoch: some platforms may store seconds instead of milliseconds
                if (lastSync < 1000000000000L) { // less than ~2001-09-09 in ms -> likely seconds
                    lastSync = lastSync * 1000L;
                }
                try {
                    SimpleDateFormat sdf = new SimpleDateFormat("dd/MM/yyyy hh:mm a");
                    sdf.setTimeZone(TimeZone.getDefault());
                    return "Last sync: " + sdf.format(new Date(lastSync));
                } catch (Exception e) {
                    return "Last sync: " + DateFormat.getDateFormat(context).format(new Date(lastSync)) + " " + DateFormat.getTimeFormat(context).format(new Date(lastSync));
                }
            }
        } catch (Exception ignore) {}
        return "Last sync: Never";
    }
}


