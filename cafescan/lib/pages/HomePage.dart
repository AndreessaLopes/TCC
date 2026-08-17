import 'package:cafescan/models/DetectionConfig.dart';
import 'package:cafescan/theme/ConfigStore.dart';
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
  final _store = ConfigStore.instance;

  @override
  void initState() {
    super.initState();
    _store.addListener(_onStoreChanged);
  }

  @override
  void dispose() {
    _store.removeListener(_onStoreChanged);
    super.dispose();
  }

  void _onStoreChanged() {
    if (mounted) setState(() {});
  }

  /// Texto descritivo exibido em cada cartão de modelo.
  String _description(ModelVariant variant) {
    switch (variant.precision) {
      case Precision.fp32:
        return 'Precisão original, sem quantização';
      case Precision.fp16:
        return 'Metade do tamanho, perda desprezível';
      case Precision.int8:
        return 'Menor arquivo, quantização inteira';
    }
  }

  @override
  Widget build(BuildContext context) {
    final sizeOf = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: CoffeColors.bg,
      appBar: AppBar(
        backgroundColor: CoffeColors.bg,
        title: Row(
          children: [
            Expanded(
              child: Text(
                "Configuração",
                style: CoffeFonts.primaryText.copyWith(fontSize: 20),
                overflow: TextOverflow.ellipsis,
                maxLines: 1,
              ),
            ),
            const SizedBox(width: 8),
            ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 140),
              child: Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(30),
                  border: Border.all(color: CoffeColors.accent, width: 1.5),
                ),
                child: Text(
                  "${DetectionConfig.totalConfigurations} combinações",
                  style: TextStyle(fontSize: 12, color: CoffeColors.accent),
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                ),
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
                padding: const EdgeInsets.all(10),
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
            const Text(
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
            ...ModelVariant.all.map(
              (variant) => ButtonModels(
                model: variant.label,
                modelFile: variant.fileName,
                photoPixelSize:
                    '${ModelVariant.inputSize}x${ModelVariant.inputSize}',
                modelDescription: _description(variant),
                photoMemorySize: '${variant.sizeMB.toStringAsFixed(2)} MB',
                isActive: _store.variant.label == variant.label,
                onChanged: (value) {
                  _store.selectVariant(ModelVariant.byLabel(value));
                },
                selectedModel: _store.variant.label,
                value: variant.label,
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
              value: _store.delegate,
              onChanged: (d) => _store.selectDelegate(d),
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
                  Row(
                    children: [
                      Text(
                        'CONFIGURAÇÃO ATIVA',
                        style: TextStyle(
                          fontSize: 11,
                          color: CoffeColors.accent600,
                          letterSpacing: 1.3,
                        ),
                      ),
                      const Spacer(),
                      _statusIndicator(),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _store.config.label,
                    style: CoffeFonts.primaryText.copyWith(
                      fontSize: 20,
                      color: CoffeColors.accent800,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _store.error ??
                        'Troca instantânea — sem necessidade de recarregar o app. '
                            'Ideal para comparar em campo.',
                    style: TextStyle(
                      fontSize: 13,
                      color: _store.error != null ? Colors.red[900] : null,
                    ),
                  ),
                ],
              ),
            ),
            SizedBox(height: sizeOf.height * 0.01),
          ],
        ),
      ),
      bottomNavigationBar: const NavBar(currentIndex: 0),
    );
  }

  /// Indica visualmente o estado de carregamento do modelo selecionado.
  Widget _statusIndicator() {
    if (_store.loading) {
      return SizedBox(
        width: 14,
        height: 14,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          color: CoffeColors.accent600,
        ),
      );
    }

    if (_store.error != null) {
      return Icon(Icons.error_outline, size: 16, color: Colors.red[900]);
    }

    if (_store.isReady) {
      return Icon(
        Icons.check_circle_outline,
        size: 16,
        color: CoffeColors.accent600,
      );
    }

    return const SizedBox.shrink();
  }
}
