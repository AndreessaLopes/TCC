import 'package:cafescan/theme/CoffeColors.dart';
import 'package:cafescan/theme/CoffeFonts.dart';
import 'package:flutter/material.dart';

final class CoffeTheme {
  static final lightTheme = ThemeData(
    primaryColor: CoffeColors.accent,
    scaffoldBackgroundColor: CoffeColors.bg,
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: CoffeColors.accent,
        foregroundColor: CoffeColors.bg,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
        textStyle: CoffeFonts.primaryText,
        padding: EdgeInsets.symmetric(horizontal: 20, vertical: 15),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        side: BorderSide(color: CoffeColors.neutral500),
        foregroundColor: Colors.black,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
        textStyle: CoffeFonts.primaryText.copyWith(color: Colors.black),
        padding: EdgeInsets.symmetric(horizontal: 20, vertical: 15),
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        textStyle: CoffeFonts.primaryText,
        foregroundColor: CoffeColors.accent,
      ),
    ),
    textTheme: TextTheme(
      bodySmall: CoffeFonts.normalText,
      bodyMedium: CoffeFonts.normalText,
      bodyLarge: CoffeFonts.primaryText,
    ),
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: CoffeColors.surface,
      elevation: 8,
      selectedIconTheme: IconThemeData(color: CoffeColors.accent, size: 35),
      selectedItemColor: CoffeColors.accent700,
      unselectedItemColor: CoffeColors.neutral600,
      selectedLabelStyle: CoffeFonts.normalText.copyWith(
        fontSize: 12,
        fontWeight: FontWeight.bold,
        color: CoffeColors.accent700,
      ),
      unselectedLabelStyle: CoffeFonts.normalText.copyWith(
        fontSize: 12,
        color: CoffeColors.neutral600,
      ),
    ),
  );
}
