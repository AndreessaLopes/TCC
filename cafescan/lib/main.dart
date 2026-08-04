import 'package:cafescan/pages/CapturaPage.dart';
import 'package:cafescan/pages/HomePage.dart';
import 'package:cafescan/pages/StartPage.dart';
import 'package:cafescan/theme/CoffeTheme.dart';
import 'package:flutter/material.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    MaterialApp(
      debugShowCheckedModeBanner: false,
      initialRoute: '/start',
      theme: CoffeTheme.lightTheme,
      routes: {
        '/start': (context) => const StartPage(),
        '/home': (context) => const HomePage(),
        '/capture': (context) => const CapturaPage(),
      },
    ),
  );
}
