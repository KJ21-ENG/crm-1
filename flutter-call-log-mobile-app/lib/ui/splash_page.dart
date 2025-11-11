import 'dart:async';
import 'package:flutter/material.dart';

import '../api_service.dart';
import 'home_page.dart';
import 'login_page.dart';

class SplashPage extends StatefulWidget {
  const SplashPage({super.key});

  @override
  State<SplashPage> createState() => _SplashPageState();
}

class _SplashPageState extends State<SplashPage> {
  @override
  void initState() {
    super.initState();
    _boot();
  }

  Future<void> _boot() async {
    await ApiService.instance.init();
    await Future.delayed(const Duration(milliseconds: 1500));
    final authed = await ApiService.instance.isAuthenticated();
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => authed ? const HomePage() : const LoginPage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SizedBox.expand(
        child: Image.asset(
          'raw_assets/eshin_app_splashscreen.gif',
          fit: BoxFit.cover,
        ),
      ),
    );
  }
}


