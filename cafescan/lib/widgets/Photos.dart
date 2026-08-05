import 'package:flutter/material.dart';
import 'dart:io';
import '../theme/CoffeColors.dart';

class _DashedBorderPainter extends CustomPainter {
  final Color color;
  final double radius;
  const _DashedBorderPainter({required this.color, required this.radius});

  @override
  void paint(Canvas canvas, Size size) {
    const dashWidth = 6.0;
    const dashGap = 5.0;
    final paint = Paint()
      ..color = color
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;
    final rrect = RRect.fromRectAndRadius(
      Rect.fromLTWH(0, 0, size.width, size.height),
      Radius.circular(radius),
    );
    final path = Path()..addRRect(rrect);
    final metrics = path.computeMetrics();
    for (final metric in metrics) {
      double distance = 0;
      while (distance < metric.length) {
        final next = distance + dashWidth;
        canvas.drawPath(
          metric.extractPath(distance, next.clamp(0, metric.length)),
          paint,
        );
        distance = next + dashGap;
      }
    }
  }

  @override
  bool shouldRepaint(covariant _DashedBorderPainter old) =>
      old.color != color || old.radius != radius;
}

/// Reusable photo capture/gallery slot.
/// Usage in your capture screen:
///   Photos(onPhotoSelected: (file) => setState(() => _photo = file))
class Photos extends StatefulWidget {
  final double aspectRatio;
  final File? photo;

  const Photos({super.key, this.aspectRatio = 4 / 3, this.photo});

  @override
  State<Photos> createState() => _PhotosState();
}

class _PhotosState extends State<Photos> {
  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: widget.aspectRatio,
      child: Stack(
        fit: StackFit.expand,
        children: [
          Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              color: CoffeColors.neutral200,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.4),
                  blurRadius: 4,
                  offset: Offset(0, 2),
                ),
              ],
            ),

            child: widget.photo != null
                ? Image.file(
                    widget.photo!,
                    fit: BoxFit.cover,
                    width: double.infinity,
                    height: double.infinity,
                  )
                : _placeholder(),
          ),
          if (widget.photo == null)
            Positioned.fill(
              child: CustomPaint(
                painter: _DashedBorderPainter(
                  color: CoffeColors.neutral500,
                  radius: 16,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _placeholder() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.image_outlined, size: 34, color: CoffeColors.neutral500),
          const SizedBox(height: 10),
          Text(
            'Escolha uma foto da galeria de grãos de café ou toque em Capturar para tirar uma foto.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 12.5, color: CoffeColors.neutral600),
          ),
          const SizedBox(height: 14),
        ],
      ),
    );
  }
}
