import 'dart:io';

import 'package:cafescan/models/Detection.dart';
import 'package:cafescan/theme/CoffeColors.dart';
import 'package:cafescan/widgets/DetectionOverlay.dart';
import 'package:flutter/material.dart';

/// Exibe uma imagem com as detecções sobrepostas.
///
/// As coordenadas das detecções são normalizadas em relação à imagem
/// completa. O widget exibe a imagem sem recorte, de modo que a área
/// desenhada corresponde exatamente à área analisada pelo modelo.
class DetectedPhoto extends StatefulWidget {
  final File photo;
  final List<Detection> detections;
  final bool showConfidence;

  const DetectedPhoto({
    super.key,
    required this.photo,
    this.detections = const [],
    this.showConfidence = false,
  });

  @override
  State<DetectedPhoto> createState() => _DetectedPhotoState();
}

class _DetectedPhotoState extends State<DetectedPhoto> {
  double? _aspectRatio;

  @override
  void initState() {
    super.initState();
    _resolveAspectRatio();
  }

  @override
  void didUpdateWidget(DetectedPhoto oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.photo.path != widget.photo.path) {
      _aspectRatio = null;
      _resolveAspectRatio();
    }
  }

  /// Obtém as proporções reais da imagem, necessárias para que a área de
  /// desenho coincida com a área exibida.
  void _resolveAspectRatio() {
    final stream = FileImage(widget.photo).resolve(const ImageConfiguration());

    stream.addListener(
      ImageStreamListener((info, _) {
        if (!mounted) return;
        setState(() {
          _aspectRatio = info.image.width / info.image.height;
        });
      }),
    );
  }

  @override
  Widget build(BuildContext context) {
    final ratio = _aspectRatio;

    if (ratio == null) {
      return AspectRatio(
        aspectRatio: 4 / 3,
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            color: CoffeColors.neutral200,
          ),
          child: const Center(child: CircularProgressIndicator()),
        ),
      );
    }

    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: AspectRatio(
        aspectRatio: ratio,
        child: Stack(
          fit: StackFit.expand,
          children: [
            // A proporção do contêiner corresponde à da imagem, de modo que
            // a exibição preenche integralmente a área sem recorte nem
            // distorção.
            Image.file(widget.photo, fit: BoxFit.contain),
            if (widget.detections.isNotEmpty)
              DetectionOverlay(
                detections: widget.detections,
                showConfidence: widget.showConfidence,
              ),
          ],
        ),
      ),
    );
  }
}
