import 'package:cafescan/pages/CapturaPage.dart';
import 'package:cafescan/pages/HomePage.dart';
import 'package:cafescan/theme/CoffeColors.dart';
import 'package:flutter/material.dart';

class NavBar extends StatefulWidget {
  const NavBar({super.key});

  @override
  State<NavBar> createState() => _NavBarState();
}

class _NavBarState extends State<NavBar> {
  int currentIndex = 0;

  static const _screens = [HomePage(), CapturaPage()];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: currentIndex, children: _screens),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        backgroundColor: CoffeColors.bg,
        currentIndex: currentIndex,
        onTap: (index) => setState(() => currentIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.tune_rounded),
            label: 'Configuração',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.photo_camera_rounded),
            label: 'Captura',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.grid_view_rounded),
            label: 'Lote',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.bar_chart_rounded),
            label: 'Métricas',
          ),
        ],
      ),
    );
  }
}
