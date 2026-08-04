import 'package:flutter/material.dart';

class NavBar extends StatelessWidget {
  final int currentIndex;
  const NavBar({super.key, required this.currentIndex});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            offset: Offset(0, -2),
          ),
        ],
      ),
      child: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: currentIndex,
        onTap: (index) {
          if (index == currentIndex) return;
          const routes = ['/home', '/capture', '/batch', '/metrics'];
          Navigator.pushReplacementNamed(context, routes[index]);
        },
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
