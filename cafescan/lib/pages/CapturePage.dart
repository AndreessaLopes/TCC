import 'dart:io';

import 'package:cafescan/models/Detection.dart';
import 'package:cafescan/theme/ConfigStore.dart';
import 'package:cafescan/theme/CoffeColors.dart';
import 'package:cafescan/theme/CoffeFonts.dart';
import 'package:cafescan/widgets/DetectedPhoto.dart';
import 'package:cafescan/widgets/NavBar.dart';
import 'package:cafescan/widgets/Photos.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

class CapturePage extends StatefulWidget {
  const CapturePage({super.key});

  @override
  State<CapturePage> createState() => _CapturePageState();
}

class _CapturePageState extends State<CapturePage> {
  final _store = ConfigStore.instance;

  File? _photo;
  InferenceResult? _result;
  bool _processing = false;
  String? _error;
  bool _showConfidence = false;

  Future<void> _pick(ImageSource source) async {
    final picked = await ImagePicker().pickImage(
      source: source,
      imageQuality: 90,
    );

    if (picked == null) return;
    if (!mounted) return;

    setState(() {
      _photo = File(picked.path);
      _result = null;
      _error = null;
    });

    await _detect();
  }

  /// Executa a detecção sobre a imagem selecionada, utilizando a
  /// configuração ativa.
  Future<void> _detect() async {
    final photo = _photo;
    if (photo == null) return;

    setState(() {
      _processing = true;
      _error = null;
    });

    try {
      await _store.ensureLoaded();

      if (_store.error != null) {
        throw StateError(_store.error!);
      }

      final result = await _store.service.detectFile(photo);

      if (!mounted) return;
      setState(() => _result = result);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _processing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final sizeOf = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: CoffeColors.bg,
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: EdgeInsets.only(
                top: sizeOf.height * 0.02,
                left: sizeOf.width * 0.05,
                right: sizeOf.width * 0.05,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _configBadge(),
                  SizedBox(height: sizeOf.height * 0.015),
                  _photo == null
                      ? const Photos(photo: null)
                      : DetectedPhoto(
                          photo: _photo!,
                          detections: _result?.detections ?? const [],
                          showConfidence: _showConfidence,
                        ),
                ],
              ),
            ),
            SizedBox(height: sizeOf.height * 0.02),
            Expanded(
              child: SingleChildScrollView(
                padding: EdgeInsets.symmetric(horizontal: sizeOf.width * 0.05),
                child: _resultSection(sizeOf),
              ),
            ),
            _actions(sizeOf),
            SizedBox(height: sizeOf.height * 0.02),
          ],
        ),
      ),
      bottomNavigationBar: const NavBar(currentIndex: 1),
    );
  }

  /// Exibe a configuração ativa, permitindo verificar em qual combinação
  /// a detecção foi executada.
  Widget _configBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
      decoration: BoxDecoration(
        color: CoffeColors.accent100,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        _store.config.label,
        style: TextStyle(fontSize: 12, color: CoffeColors.accent800),
      ),
    );
  }

  Widget _resultSection(Size sizeOf) {
    if (_processing) {
      return Column(
        children: [
          SizedBox(height: sizeOf.height * 0.02),
          const CircularProgressIndicator(),
          const SizedBox(height: 12),
          Text(
            'Executando inferência...',
            style: CoffeFonts.normalText.copyWith(
              color: CoffeColors.neutral600,
            ),
          ),
        ],
      );
    }

    if (_error != null) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.red[50],
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          _error!,
          style: TextStyle(fontSize: 13, color: Colors.red[900]),
        ),
      );
    }

    final result = _result;
    if (result == null) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: CoffeColors.surface,
        borderRadius: BorderRadius.circular(30),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  '${result.count} ${result.count == 1 ? "grão detectado" : "grãos detectados"}',
                  style: CoffeFonts.primaryText,
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                ),
              ),
              GestureDetector(
                onTap: () => setState(() => _showConfidence = !_showConfidence),
                child: Icon(
                  _showConfidence
                      ? Icons.visibility_outlined
                      : Icons.visibility_off_outlined,
                  size: 20,
                  color: CoffeColors.neutral600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            'Confiança média: ${result.averageConfidence.toStringAsFixed(3)}',
            style: CoffeFonts.normalText.copyWith(
              color: CoffeColors.neutral600,
              fontSize: 13,
            ),
          ),
          const SizedBox(height: 14),
          Text(
            'LATÊNCIA',
            style: TextStyle(
              fontSize: 11,
              color: CoffeColors.neutral600,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 8),
          _metricRow('Pré-processamento', result.preprocessMs),
          _metricRow('Inferência', result.inferenceMs),
          _metricRow('Pós-processamento', result.postprocessMs),
          Divider(color: CoffeColors.divider, height: 18),
          _metricRow('Total', result.totalMs, emphasis: true),
        ],
      ),
    );
  }

  Widget _metricRow(String label, double ms, {bool emphasis = false}) {
    final style = emphasis
        ? CoffeFonts.primaryText.copyWith(fontSize: 14)
        : CoffeFonts.normalText.copyWith(
            fontSize: 13,
            color: CoffeColors.neutral700,
          );

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Expanded(
            child: Text(
              label,
              style: style,
              overflow: TextOverflow.ellipsis,
              maxLines: 1,
            ),
          ),
          Text('${ms.toStringAsFixed(1)} ms', style: style),
        ],
      ),
    );
  }

  Widget _actions(Size sizeOf) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        Flexible(
          child: ElevatedButton.icon(
            onPressed: _processing ? null : () => _pick(ImageSource.camera),
            icon: const Icon(Icons.camera_alt_outlined, size: 18),
            label: const Text('Capturar', overflow: TextOverflow.ellipsis),
          ),
        ),
        Flexible(
          child: OutlinedButton.icon(
            onPressed: _processing ? null : () => _pick(ImageSource.gallery),
            icon: const Icon(Icons.photo_library_outlined, size: 18),
            label: const Text('Galeria', overflow: TextOverflow.ellipsis),
          ),
        ),
      ],
    );
  }
}
