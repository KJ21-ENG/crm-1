package com.eshin.crm.boot

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import androidx.core.content.ContextCompat

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val action = intent.action ?: return
        if (action == Intent.ACTION_BOOT_COMPLETED || action == Intent.ACTION_LOCKED_BOOT_COMPLETED) {
            // Start the flutter_foreground_task service via explicit intent
            try {
                val i = Intent(context, Class.forName("com.pravera.flutter_foreground_task.service.ForegroundService"))
                i.action = "ACTION_START_FOREGROUND_SERVICE"
                ContextCompat.startForegroundService(context, i)
            } catch (_: Exception) {
                // Ignore failures silently; the app can start service on next launch
            }
        }
    }
}


