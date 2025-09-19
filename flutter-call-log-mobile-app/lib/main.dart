import 'package:flutter/material.dart';
import 'api_service.dart';
import 'ui/login_page.dart';
import 'ui/home_page.dart';
import 'ui/splash_page.dart';
import 'ui/theme.dart';
import 'ui/scroll_behavior.dart';
import 'widget_bridge.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  WidgetBridge.init();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Eshin',
      theme: AppTheme.light(),
      scrollBehavior: const AppScrollBehavior(),
      home: const SplashPage(),
    );
  }
}

class _AuthGate extends StatefulWidget {
  const _AuthGate({super.key});

  @override
  State<_AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<_AuthGate> {
  bool? _authed;

  @override
  void initState() {
    super.initState();
    _check();
  }

  Future<void> _check() async {
    await ApiService.instance.init();
    final ok = await ApiService.instance.isAuthenticated();
    setState(() => _authed = ok);
  }

  @override
  Widget build(BuildContext context) {
    if (_authed == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()))
          ;
    }
    return _authed == true
        ? const HomePage()
        : LoginPage(
            onLoggedIn: () {
              setState(() => _authed = true);
            },
    );
  }
}
