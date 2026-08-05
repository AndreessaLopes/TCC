import 'package:cafescan/widgets/ButtonDelegate.dart';

/// Arquitetura do modelo de detecção.
///
/// A distinção importa porque as arquiteturas produzem saídas em formatos
/// diferentes e exigem pós-processamentos distintos.
enum Architecture {
  /// Saída (1, 5, 18900). Requer supressão não máxima na aplicação.
  yolov8n,

  /// Saída (1, 300, 6). Detecções já filtradas pelo próprio modelo.
  yolov10n,
}

/// Estratégia de quantização aplicada durante a conversão para TFLite.
enum Precision { fp32, fp16, int8 }

/// Representa uma das variantes de modelo disponíveis na aplicação.
class ModelVariant {
  final Architecture architecture;
  final Precision precision;
  final String assetPath;
  final double sizeMB;

  const ModelVariant({
    required this.architecture,
    required this.precision,
    required this.assetPath,
    required this.sizeMB,
  });

  String get architectureLabel =>
      architecture == Architecture.yolov8n ? 'YOLOv8n' : 'YOLOv10n';

  String get precisionLabel {
    switch (precision) {
      case Precision.fp32:
        return 'FP32';
      case Precision.fp16:
        return 'FP16';
      case Precision.int8:
        return 'INT8';
    }
  }

  /// Identificador legível, usado na interface e nos registros de métricas.
  String get label => '$architectureLabel · $precisionLabel';

  /// Nome do arquivo, sem o caminho.
  String get fileName => assetPath.split('/').last;

  /// Resolução de entrada. Todas as variantes utilizam 960 x 960 pixels,
  /// correspondente à resolução adotada no treinamento.
  static const int inputSize = 960;

  /// Indica se o modelo espera entrada quantizada em inteiros de 8 bits.
  bool get isQuantized => precision == Precision.int8;

  /// Variantes geradas na etapa de conversão.
  static const List<ModelVariant> all = [
    ModelVariant(
      architecture: Architecture.yolov8n,
      precision: Precision.fp32,
      assetPath: 'assets/models/yolov8n_fp32.tflite',
      sizeMB: 11.96,
    ),
    ModelVariant(
      architecture: Architecture.yolov8n,
      precision: Precision.fp16,
      assetPath: 'assets/models/yolov8n_fp16.tflite',
      sizeMB: 6.02,
    ),
    ModelVariant(
      architecture: Architecture.yolov8n,
      precision: Precision.int8,
      assetPath: 'assets/models/yolov8n_int8.tflite',
      sizeMB: 3.18,
    ),
    ModelVariant(
      architecture: Architecture.yolov10n,
      precision: Precision.fp32,
      assetPath: 'assets/models/yolov10n_fp32.tflite',
      sizeMB: 9.17,
    ),
    ModelVariant(
      architecture: Architecture.yolov10n,
      precision: Precision.fp16,
      assetPath: 'assets/models/yolov10n_fp16.tflite',
      sizeMB: 4.65,
    ),
    ModelVariant(
      architecture: Architecture.yolov10n,
      precision: Precision.int8,
      assetPath: 'assets/models/yolov10n_int8.tflite',
      sizeMB: 2.82,
    ),
  ];

  static ModelVariant byLabel(String label) =>
      all.firstWhere((v) => v.label == label, orElse: () => all.first);
}

/// Configuração experimental: combinação de variante e delegate.
///
/// As seis variantes combinadas com os dois delegates resultam nas doze
/// configurações previstas no protocolo experimental.
class DetectionConfig {
  final ModelVariant variant;
  final Delegate delegate;

  const DetectionConfig({required this.variant, required this.delegate});

  String get delegateLabel => delegate == Delegate.gpu ? 'GPU' : 'CPU';

  String get label => '${variant.label} · $delegateLabel';

  /// Total de configurações previstas no experimento.
  static int get totalConfigurations =>
      ModelVariant.all.length * Delegate.values.length;
}
