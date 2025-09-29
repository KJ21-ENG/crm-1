import 'package:call_log/call_log.dart';

String callTypeHint(CallType? t) {
  switch (t) {
    case CallType.outgoing:
      return 'out';
    case CallType.missed:
      return 'missed';
    case CallType.rejected:
      return 'rej';
    case CallType.incoming:
      return 'in';
    default:
      return 'unk';
  }
}

String _digits(String? s) => (s ?? '').replaceAll(RegExp(r'[^0-9+]'), '');

Map<String, dynamic> toCrmCallLog(CallLogEntry e, String userMobile) {
  final ts = e.timestamp ?? DateTime.now().millisecondsSinceEpoch;
  final number = (e.number ?? 'Unknown').trim();
  final duration = (e.duration ?? 0);
  // Make device_call_id stable even when duration is 0 or OEM writes late
  final deviceId = 'device_${ts}_${number}_${duration}_${callTypeHint(e.callType)}';

  String callType = 'Incoming';
  switch (e.callType) {
    case CallType.outgoing:
      callType = 'Outgoing';
      break;
    case CallType.missed:
      callType = 'Incoming';
      break;
    default:
      callType = 'Incoming';
  }

  String status = 'Completed';

  // Prioritize native call type over duration for accurate status determination
  switch (e.callType) {
    case CallType.missed:
      status = 'No Answer';  // Native missed calls should be No Answer regardless of duration
      break;
    case CallType.rejected:
      status = 'Canceled';   // Native rejected calls should be Canceled regardless of duration
      break;
    case CallType.outgoing:
      // Outgoing calls with duration = 0 are unanswered
      if (duration == 0) {
        status = 'No Answer';
      }
      // Outgoing calls with duration > 0 are completed
      break;
    case CallType.incoming:
    default:
      // Incoming calls with duration = 0 are missed
      if (duration == 0) {
        status = 'No Answer';
      }
      // Incoming calls with duration > 0 are completed
      break;
  }

  final userDigits = _digits(userMobile);
  final phoneDigits = _digits(number);
  String from = number;
  String to = userMobile;
  if (callType == 'Outgoing') {
    from = userMobile;
    to = number;
  }
  if (userDigits.isNotEmpty && phoneDigits.isNotEmpty) {
    final norm = (String n) => n.endsWith(userDigits) ? userDigits : n;
    final f = norm(_digits(from));
    final t = norm(_digits(to));
    if (t == userDigits) {
      callType = 'Incoming';
      from = number;
      to = userMobile;
    } else if (f == userDigits) {
      callType = 'Outgoing';
      from = userMobile;
      to = number;
    }
  }

  String fmt(int ms) {
    final d = DateTime.fromMillisecondsSinceEpoch(ms);
    String two(int v) => v.toString().padLeft(2, '0');
    return '${d.year}-${two(d.month)}-${two(d.day)} ${two(d.hour)}:${two(d.minute)}:${two(d.second)}';
  }

  final endTs = ts + (duration * 1000);
  return {
    'from': from,
    'to': to,
    'type': callType,
    'status': status,
    'duration': duration,
    'start_time': fmt(ts),
    'end_time': fmt(endTs),
    'device_call_id': deviceId,
    'native_call_type': callTypeHint(e.callType),  // Store original native call type
    'native_duration': duration,  // Store original native duration
    'method': 'Mobile',  // Indicate this came from mobile app
    'source': 'Mobile App',
  };
}


