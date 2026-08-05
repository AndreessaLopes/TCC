import 'dart:io';

import 'package:cafescan/models/DetectionConfig.dart';
import 'package:cafescan/services/DetectionService.dart';
import 'package:cafescan/widgets/ButtonDelegate.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:tflite_flutter/tflite_flutter.dart' hide Delegate;

/// Página temporária para verificação do pipeline de inferência.
/// Deve ser removida após a integração nas telas definitivas.
class TestePage extends StatefulWidget {
  const TestePage({super.key});

  @override
  State<TestePage> createState() => _TestePageState();
}

class _TestePageState extends State<TestePage> {
  final _service = DetectionService();
  final _log = <String>[];
  bool _busy = false;

  void _print(String msg) {
    debugPrint(msg);
    setState(() => _log.add(msg));
  }

  /// Inspeciona os formatos de entrada e saída de cada variante.
  Future<void> _inspecionarModelos() async {
    setState(() {
      _busy = true;
      _log.clear();
    });

    for (final variant in ModelVariant.all) {
      try {
        final interpreter = await Interpreter.fromAsset(variant.assetPath);
        final input = interpreter.getInputTensor(0);
        final output = interpreter.getOutputTensor(0);

        _print(variant.label);
        _print('  entrada: ${input.shape} · ${input.type}');
        _print('  saída:   ${output.shape} · ${output.type}');
        _print('');

        interpreter.close();
      } catch (e) {
        _print('${variant.label} — FALHA: $e');
        _print('');
      }
    }

    setState(() => _busy = false);
  }

  /// Executa uma detecção sobre uma imagem escolhida.
  Future<void> _detectar() async {
    final picked = await ImagePicker().pickImage(source: ImageSource.gallery);
    if (picked == null) return;

    setState(() {
      _busy = true;
      _log.clear();
    });

    // Usa a primeira variante em CPU, que é a configuração mais estável.
    final config = DetectionConfig(
      variant: ModelVariant.all.first,
      delegate: Delegate.cpu,
    );

    try {
      _print('Carregando ${config.label}...');
      await _service.load(config);

      _print('Executando inferência...');
      final result = await _service.detectFile(File(picked.path));

      _print('');
      _print('Detecções: ${result.count}');
      _print('Confiança média: ${result.averageConfidence.toStringAsFixed(3)}');
      _print('');
      _print('Pré-processamento: ${result.preprocessMs.toStringAsFixed(1)} ms');
      _print('Inferência:        ${result.inferenceMs.toStringAsFixed(1)} ms');
      _print(
        'Pós-processamento: ${result.postprocessMs.toStringAsFixed(1)} ms',
      );
      _print('Total:             ${result.totalMs.toStringAsFixed(1)} ms');

      if (result.detections.isNotEmpty) {
        _print('');
        _print('Primeiras detecções:');
        for (final d in result.detections.take(3)) {
          _print(
            '  [${d.left.toStringAsFixed(3)}, ${d.top.toStringAsFixed(3)}, '
            '${d.right.toStringAsFixed(3)}, ${d.bottom.toStringAsFixed(3)}] '
            'conf=${d.confidence.toStringAsFixed(3)}',
          );
        }
      }
    } catch (e, s) {
      _print('ERRO: $e');
      _print('$s');
    } finally {
      await _service.dispose();
      setState(() => _busy = false);
    }
  }

  @override
  void dispose() {
    _service.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Teste de inferência')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: _busy ? null : _inspecionarModelos,
                    child: const Text('Inspecionar'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _busy ? null : _detectar,
                    child: const Text('Detectar'),
                  ),
                ),
              ],
            ),
          ),
          if (_busy) const LinearProgressIndicator(),
          Expanded(
            child: Container(
              width: double.infinity,
              color: Colors.black87,
              padding: const EdgeInsets.all(12),
              child: SingleChildScrollView(
                child: SelectableText(
                  _log.join('\n'),
                  style: const TextStyle(
                    color: Colors.greenAccent,
                    fontFamily: 'monospace',
                    fontSize: 12,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
