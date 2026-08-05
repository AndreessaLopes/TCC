import 'package:cafescan/theme/CoffeColors.dart';
import 'package:cafescan/theme/CoffeFonts.dart';
import 'package:cafescan/widgets/ButtonDelegate.dart';
import 'package:cafescan/widgets/ButtonModels.dart';
import 'package:cafescan/widgets/ModalHelp.dart';
import 'package:cafescan/widgets/NavBar.dart';
import 'package:flutter/material.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final List<Map<String, dynamic>> models = [
    {
      'model': 'YOLOv8n',
      'modelFile': 'yolov8n_int8.tflite',
      'photoPixelSize': '320x320',
      'modelDescription': 'Rápido, indicado para CPU',
      'photoMemorySize': '6.2MB',
    },
    {
      'model': 'YOLOv5n',
      'modelFile': 'yolov5n_fp16.tflite',
      'photoPixelSize': '320x320',
      'modelDescription': 'Equilíbrio geral',
      'photoMemorySize': '7.4MB',
    },
    {
      'model': 'EfficientDet-Lite0',
      'modelFile': 'efficientdet_lite0.tflite',
      'photoPixelSize': '320x320',
      'modelDescription': 'Leve, boa precisão',
      'photoMemorySize': '4.4MB',
    },
    {
      'model': 'EfficientDet-Lite2',
      'modelFile': 'efficientdet_lite2.tflite',
      'photoPixelSize': '448x448',
      'modelDescription': 'Mais preciso, mais pesado',
      'photoMemorySize': '7.2MB',
    },
    {
      'model': 'MobileNetV3-SSD',
      'modelFile': 'mobilenet_v3_ssd.tflite',
      'photoPixelSize': '300x300',
      'modelDescription': 'Clássico, estável',
      'photoMemorySize': '5.8MB',
    },
  ];
  Delegate delegate = Delegate.gpu;

  String get configLabel {
    return '$selectedModel · ${delegate == Delegate.gpu ? 'GPU' : 'CPU'}';
  }

  String selectedModel = 'YOLOv8n';

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
            ...models.map(
              (model) => ButtonModels(
                model: model['model'],
                modelFile: model['modelFile'],
                photoPixelSize: model['photoPixelSize'],
                modelDescription: model['modelDescription'],
                photoMemorySize: model['photoMemorySize'],
                isActive: selectedModel == model['model'],
                onChanged: (value) {
                  setState(() {
                    selectedModel = value;
                  });
                },
                selectedModel: selectedModel,
                value: model['model'],
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
            SizedBox(height: sizeOf.height * 0.01,)
          ],
        ),
      ),
      bottomNavigationBar: NavBar(currentIndex: 0),
    );
  }
}
