import 'dart:ui';

/// Uma detecção individual produzida pelo modelo.
///
/// As coordenadas são normalizadas no intervalo [0, 1] em relação às
/// dimensões da imagem, permitindo desenhar as caixas sobre a imagem
/// exibida independentemente da escala adotada na apresentação.
class Detection {
  /// Borda esquerda, normalizada.
  final double left;

  /// Borda superior, normalizada.
  final double top;

  /// Borda direita, normalizada.
  final double right;

  /// Borda inferior, normalizada.
  final double bottom;

  /// Confiança associada à predição, no intervalo [0, 1].
  final double confidence;

  /// Índice da classe. O conjunto de dados utiliza classe única (`graos`),
  /// de modo que o valor é sempre 0 nesta etapa da pesquisa.
  final int classIndex;

  const Detection({
    required this.left,
    required this.top,
    required this.right,
    required this.bottom,
    required this.confidence,
    this.classIndex = 0,
  });

  double get width => right - left;
  double get height => bottom - top;
  double get area => width * height;

  /// Converte para um retângulo absoluto, dadas as dimensões de exibição.
  Rect toRect(double displayWidth, double displayHeight) => Rect.fromLTRB(
    left * displayWidth,
    top * displayHeight,
    right * displayWidth,
    bottom * displayHeight,
  );

  /// Interseção sobre união entre duas detecções, utilizada na supressão
  /// não máxima.
  double iou(Detection other) {
    final interLeft = left > other.left ? left : other.left;
    final interTop = top > other.top ? top : other.top;
    final interRight = right < other.right ? right : other.right;
    final interBottom = bottom < other.bottom ? bottom : other.bottom;

    final interWidth = interRight - interLeft;
    final interHeight = interBottom - interTop;

    if (interWidth <= 0 || interHeight <= 0) return 0;

    final intersection = interWidth * interHeight;
    final union = area + other.area - intersection;

    return union > 0 ? intersection / union : 0;
  }
}

/// Resultado completo de uma inferência, reunindo as detecções obtidas e
/// as medições de desempenho associadas.
class InferenceResult {
  final List<Detection> detections;

  /// Tempo de preparação da imagem, em milissegundos.
  final double preprocessMs;

  /// Tempo de execução do modelo, em milissegundos.
  final double inferenceMs;

  /// Tempo de decodificação da saída, incluindo supressão não máxima
  /// quando aplicável, em milissegundos.
  final double postprocessMs;

  const InferenceResult({
    required this.detections,
    required this.preprocessMs,
    required this.inferenceMs,
    required this.postprocessMs,
  });

  /// Latência total do processamento de uma imagem.
  double get totalMs => preprocessMs + inferenceMs + postprocessMs;

  int get count => detections.length;

  /// Confiança média das detecções obtidas.
  double get averageConfidence {
    if (detections.isEmpty) return 0;
    final sum = detections.fold<double>(0, (a, d) => a + d.confidence);
    return sum / detections.length;
  }
}
