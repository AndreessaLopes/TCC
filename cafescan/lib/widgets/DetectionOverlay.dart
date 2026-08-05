import 'package:cafescan/models/Detection.dart';
import 'package:cafescan/theme/CoffeColors.dart';
import 'package:flutter/material.dart';

/// Desenha as caixas delimitadoras das detecções sobre a imagem exibida.
///
/// As coordenadas das detecções são normalizadas, de modo que o desenho
/// acompanha automaticamente as dimensões atribuídas ao widget.
class DetectionOverlay extends StatelessWidget {
  final List<Detection> detections;

  /// Exibe o valor de confiança acima de cada caixa.
  final bool showConfidence;

  const DetectionOverlay({
    super.key,
    required this.detections,
    this.showConfidence = false,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return CustomPaint(
          size: Size(constraints.maxWidth, constraints.maxHeight),
          painter: _DetectionPainter(
            detections: detections,
            showConfidence: showConfidence,
          ),
        );
      },
    );
  }
}

class _DetectionPainter extends CustomPainter {
  final List<Detection> detections;
  final bool showConfidence;

  _DetectionPainter({required this.detections, required this.showConfidence});

  @override
  void paint(Canvas canvas, Size size) {
    final strokeWidth = size.shortestSide * 0.005;

    final boxPaint = Paint()
      ..color = CoffeColors.accent
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth < 1.5 ? 1.5 : strokeWidth;

    for (final detection in detections) {
      final rect = detection.toRect(size.width, size.height);

      canvas.drawRRect(
        RRect.fromRectAndRadius(rect, const Radius.circular(3)),
        boxPaint,
      );

      if (showConfidence) {
        _paintConfidence(canvas, rect, detection.confidence, size);
      }
    }
  }

  void _paintConfidence(Canvas canvas, Rect rect, double confidence, Size size) {
    final fontSize = size.shortestSide * 0.028;

    final painter = TextPainter(
      text: TextSpan(
        text: confidence.toStringAsFixed(2),
        style: TextStyle(
          color: Colors.white,
          fontSize: fontSize < 9 ? 9 : fontSize,
          fontWeight: FontWeight.w600,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();

    final labelRect = Rect.fromLTWH(
      rect.left,
      rect.top - painter.height - 2,
      painter.width + 6,
      painter.height + 2,
    );

    canvas.drawRRect(
      RRect.fromRectAndRadius(labelRect, const Radius.circular(3)),
      Paint()..color = CoffeColors.accent,
    );

    painter.paint(canvas, Offset(labelRect.left + 3, labelRect.top + 1));
  }

  @override
  bool shouldRepaint(_DetectionPainter oldDelegate) =>
      oldDelegate.detections != detections ||
      oldDelegate.showConfidence != showConfidence;
}
