import 'package:cafescan/theme/CoffeColors.dart';
import 'package:cafescan/theme/CoffeFonts.dart';
import 'package:cafescan/widgets/ButtonDelegate.dart';
import 'package:cafescan/widgets/ModalHelp.dart';
import 'package:cafescan/widgets/NavBar.dart';
import 'package:flutter/material.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String model = 'NanoDet-Plus';
  Delegate delegate = Delegate.gpu;

  String get configLabel =>
      '$model · ${delegate == Delegate.gpu ? 'GPU' : 'CPU'}';
  @override
  Widget build(BuildContext context) {
    final sizeOf = MediaQuery.of(context).size;
    return Scaffold(
      backgroundColor: CoffeColors.bg,
      appBar: AppBar(
        backgroundColor: CoffeColors.bg,
        title: Row(
          children: [
            Text(
              "Configuração",
              style: CoffeFonts.primaryText.copyWith(fontSize: 20),
            ),
            Spacer(),
            Container(
              padding: EdgeInsets.all(6),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(30),
                border: Border.all(color: CoffeColors.accent, width: 1.5),
              ),
              child: Text(
                "6 combinações",
                style: TextStyle(fontSize: 12, color: CoffeColors.accent),
              ),
            ),
          ],
        ),
        actions: [
          GestureDetector(
            onTap: () {
              ModalHelp.showHelpDialog(context);
            },
            child: Padding(
              padding: const EdgeInsets.only(right: 20),
              child: Container(
                padding: EdgeInsets.all(10),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: CoffeColors.divider, width: 1),
                ),
                child: Text(
                  "?",
                  style: CoffeFonts.primaryText.copyWith(
                    fontSize: 20,
                    color: Colors.black,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.symmetric(
          horizontal: sizeOf.width * 0.04,
          vertical: sizeOf.height * 0.01,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          spacing: sizeOf.height * 0.02,
          children: [
            Text(
              'Escolha o modelo (.tflite) e o delegate de execução.',
              style: TextStyle(fontSize: 14),
            ),
            Text(
              "MODELO",
              style: CoffeFonts.primaryText.copyWith(
                fontWeight: FontWeight.bold,
                color: CoffeColors.neutral700,
                fontSize: 16,
              ),
            ),
            Text(
              "DELEGATE",
              style: CoffeFonts.primaryText.copyWith(
                fontWeight: FontWeight.bold,
                color: CoffeColors.neutral700,
                fontSize: 16,
              ),
            ),
            ButtonDelegate(
              value: delegate,
              onChanged: (d) => setState(() => delegate = d),
            ),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: CoffeColors.accent100,
                borderRadius: BorderRadius.circular(30),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'CONFIGURAÇÃO ATIVA',
                    style: TextStyle(
                      fontSize: 11,
                      color: CoffeColors.accent600,
                      letterSpacing: 1.3,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    configLabel,
                    style: CoffeFonts.primaryText.copyWith(
                      fontSize: 20,
                      color: CoffeColors.accent800,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Troca instantânea — sem necessidade de recarregar o app. Ideal para comparar em campo.',
                    style: TextStyle(fontSize: 13),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: NavBar(),
    );
  }
}
