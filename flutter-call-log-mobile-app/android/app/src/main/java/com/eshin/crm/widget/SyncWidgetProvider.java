package com.eshin.crm.widget;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.Intent;
import android.content.ComponentName;
import android.widget.Toast;
import io.flutter.embedding.engine.FlutterEngine;
import io.flutter.embedding.engine.dart.DartExecutor;
import io.flutter.view.FlutterMain;
import io.flutter.plugin.common.MethodChannel;
import android.widget.RemoteViews;

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

            appWidgetManager.updateAppWidget(appWidgetId, views);
        }
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        super.onReceive(context, intent);
        if (intent == null) return;
        String action = intent.getAction();
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
}


