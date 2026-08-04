import 'package:cafescan/widgets/NavBar.dart';
import 'package:flutter/material.dart';

class CapturaPage extends StatefulWidget {
  const CapturaPage({super.key});

  @override
  State<CapturaPage> createState() => _CapturaPageState();
}

class _CapturaPageState extends State<CapturaPage> {
  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: Text('Captura Page')),
      bottomNavigationBar: NavBar(),
    );
  }
}
