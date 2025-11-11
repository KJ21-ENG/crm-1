package com.eshin.crm

import android.Manifest
import android.content.pm.PackageManager
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import android.content.Intent

class MainActivity: FlutterActivity() {
    private val CHANNEL = "crm/permissions"
    private val WIDGET_CHANNEL = "crm/widget"
    private val REQUEST_READ_CALL_LOG = 10010
    private var pendingResult: MethodChannel.Result? = null
    private var widgetChannel: MethodChannel? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "hasReadCallLog" -> {
                    val granted = ContextCompat.checkSelfPermission(this, Manifest.permission.READ_CALL_LOG) == PackageManager.PERMISSION_GRANTED
                    result.success(granted)
                }
                "requestReadCallLog" -> {
                    val granted = ContextCompat.checkSelfPermission(this, Manifest.permission.READ_CALL_LOG) == PackageManager.PERMISSION_GRANTED
                    if (granted) {
                        result.success(true)
                    } else {
                        pendingResult = result
                        ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.READ_CALL_LOG), REQUEST_READ_CALL_LOG)
                    }
                }
                else -> result.notImplemented()
            }
        }
        // Widget channel - used to pass intents from Android widget to Flutter
        val widgetMethodChannel = MethodChannel(flutterEngine.dartExecutor.binaryMessenger, WIDGET_CHANNEL)
        widgetMethodChannel.setMethodCallHandler { call, result ->
            when (call.method) {
                "refreshWidget" -> {
                    try {
                        val intent = Intent("com.eshin.crm.ACTION_WIDGET_REFRESH")
                        intent.setPackage(packageName)
                        sendBroadcast(intent)
                        result.success(true)
                    } catch (e: Exception) {
                        result.error("ERROR", e.message, null)
                    }
                }
                else -> result.notImplemented()
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleWidgetIntent(intent)
    }

    override fun onResume() {
        super.onResume()
        handleWidgetIntent(intent)
    }

    private fun handleWidgetIntent(intent: Intent?) {
        if (intent == null) return
        val action = intent.action ?: return
        when (action) {
            "com.eshin.crm.ACTION_WIDGET_MANUAL_SYNC" -> {
                try {
                    widgetChannel?.invokeMethod("manualSync", null, object: MethodChannel.Result {
                        override fun success(result: Any?) {}
                        override fun error(errorCode: String, errorMessage: String?, errorDetails: Any?) {}
                        override fun notImplemented() {}
                    })
                } catch (e: Exception) {}
                // Close activity immediately to avoid leaving UI open when widget invoked
                try { runOnUiThread { finish() } } catch (_: Exception) {}
            }
            "com.eshin.crm.ACTION_WIDGET_TOGGLE_BG" -> {
                try {
                    widgetChannel?.invokeMethod("toggleBackground", null, object: MethodChannel.Result {
                        override fun success(result: Any?) {}
                        override fun error(errorCode: String, errorMessage: String?, errorDetails: Any?) {}
                        override fun notImplemented() {}
                    })
                } catch (e: Exception) {}
                // Close activity immediately to avoid leaving UI open when widget invoked
                try { runOnUiThread { finish() } } catch (_: Exception) {}
            }
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_READ_CALL_LOG) {
            val isGranted = grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED
            pendingResult?.success(isGranted)
            pendingResult = null
        }
    }
}
