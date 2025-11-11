import 'package:flutter/material.dart';

class AppTheme {
  // Extracted from the provided logo: deep navy + gold accent
  static const Color primary = Color(0xFF0F2433); // dark navy
  static const Color accentGold = Color(0xFFC8A561); // gold accent for highlights
  static const Color surface = Color(0xFFF5F7FB);

  static ThemeData light() {
    final base = ThemeData(useMaterial3: true);
    final scheme = ColorScheme.fromSeed(
      seedColor: primary,
      primary: primary,
      secondary: accentGold,
      surface: surface,
      background: surface,
      brightness: Brightness.light,
    );
    return base.copyWith(
      colorScheme: scheme,
      scaffoldBackgroundColor: surface,
      appBarTheme: AppBarTheme(
        backgroundColor: scheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: scheme.primary,
        contentTextStyle: const TextStyle(color: Colors.white),
      ),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: scheme.primary,
        foregroundColor: Colors.white,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(backgroundColor: scheme.primary, foregroundColor: Colors.white),
      ),
    );
  }
}



