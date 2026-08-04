import 'package:cafescan/theme/CoffeFonts.dart';
import 'package:cafescan/widgets/StartPageCard.dart';
import 'package:flutter/material.dart';

class StartPage extends StatelessWidget {
  const StartPage({super.key});

  @override
  Widget build(BuildContext context) {
    final sizeOf = MediaQuery.of(context).size;
    return Scaffold(
      body: SingleChildScrollView(
        padding: EdgeInsets.symmetric(
          horizontal: sizeOf.width * 0.06,
          vertical: sizeOf.height * 0.15,
        ),
        child: Column(
          children: [
            Padding(
              padding: EdgeInsets.symmetric(horizontal: sizeOf.width * 0.06),

              child: Column(
                spacing: sizeOf.height * 0.01,
                children: [
                  Image.asset(
                    'assets/images/icon.png',
                    width: sizeOf.width * 0.2,
                  ),
                  Text(
                    style: CoffeFonts.primaryText.copyWith(fontSize: 28),
                    'CaféScan',
                  ),
                  Text(
                    textAlign: TextAlign.center,
                    'Ferramenta de campo para comparar modelos de detecção de maturação de grãos de café.',
                    style: TextStyle(fontSize: 14),
                  ),
                ],
              ),
            ),
            SizedBox(height: sizeOf.height * 0.03),
            Column(
              spacing: sizeOf.height * 0.015,
              children: [
                StartPageCard(
                  number: '1',
                  text: 'Escolha o modelo (.tflite) e o delegate - CPU ou GPU.',
                ),
                StartPageCard(
                  number: '2',
                  text:
                      'Capture uma foto, use a galeria ou rode um lote de 285 images.',
                ),
                StartPageCard(
                  number: '3',
                  text:
                      'Veja e exporte as métricas de latência, RAM, temperatura e bateria.',
                ),
              ],
            ),
            SizedBox(height: sizeOf.height * 0.05),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.of(context).pushReplacementNamed('/home');
                },
                child: Text('Começar'),
              ),
            ),
            TextButton(onPressed: () {}, child: Text('Como funciona o app?')),
          ],
        ),
      ),
    );
  }
}
