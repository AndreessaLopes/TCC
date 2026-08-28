import 'dart:io';
import 'dart:typed_data';

import 'package:cafescan/models/Detection.dart';
import 'package:cafescan/models/DetectionConfig.dart';
import 'package:cafescan/widgets/ButtonDelegate.dart' as app_delegate;
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';

/// Indica que a combinação de modelo e delegate não é suportada pelo
/// dispositivo.
class UnsupportedConfigurationException implements Exception {
  final String message;
  const UnsupportedConfigurationException(this.message);

  @override
  String toString() => message;
}

/// Serviço responsável pela execução local dos modelos de detecção.
///
/// Encapsula o carregamento do interpretador TensorFlow Lite, o
/// pré-processamento das imagens, a execução da inferência e a decodificação
/// das saídas, que diferem conforme a arquitetura utilizada.
class DetectionService {
  Interpreter? _interpreter;
  DetectionConfig? _config;

  /// Buffers reutilizados entre inferências consecutivas.
  Float32List? _inputBuffer;
  Float32List? _outputBuffer;
  List<int>? _outputShape;

  double confidenceThreshold = 0.25;
  double nmsThreshold = 0.7;
  int maxDetections = 300;

  DetectionConfig? get config => _config;
  bool get isReady => _interpreter != null;

  /// Carrega a configuração informada, substituindo a anterior.
  Future<void> load(DetectionConfig config) async {
    await dispose();

    final options = InterpreterOptions();

    if (config.delegate == app_delegate.Delegate.gpu) {
      options.addDelegate(GpuDelegateV2());
    } else {
      options.threads = Platform.numberOfProcessors;
    }

    try {
      final interpreter = await Interpreter.fromAsset(
        config.variant.assetPath,
        options: options,
      );

      final inputShape = interpreter.getInputTensor(0).shape;
      _outputShape = interpreter.getOutputTensor(0).shape;

      _inputBuffer = Float32List(inputShape.reduce((a, b) => a * b));
      _outputBuffer = Float32List(_outputShape!.reduce((a, b) => a * b));

      _interpreter = interpreter;
      _config = config;
    } catch (e) {
      throw UnsupportedConfigurationException(_describeFailure(config, e));
    }
  }

  /// Descreve a falha de carregamento em termos compreensíveis.
  ///
  /// A combinação de quantização em inteiros com o delegate de GPU não é
  /// suportada para o YOLOv10, uma vez que a operação de seleção das
  /// melhores detecções, adotada em substituição à supressão não máxima,
  /// não possui implementação disponível nesse mecanismo de aceleração.
  String _describeFailure(DetectionConfig config, Object error) {
    final isGpu = config.delegate == app_delegate.Delegate.gpu;
    final isInt8 = config.variant.precision == Precision.int8;
    final isV10 = config.variant.architecture == Architecture.yolov10n;

    if (isGpu && isInt8 && isV10) {
      return 'Combinação não suportada pelo dispositivo.\n\n'
          'O delegate de GPU não implementa a operação de seleção das '
          'melhores detecções (TOPK_V2), utilizada pelo YOLOv10 em '
          'substituição à supressão não máxima. Apenas 13 das 345 operações '
          'do modelo puderam ser delegadas.';
    }

    if (isGpu) {
      return 'Não foi possível inicializar o delegate de GPU para esta '
          'configuração.\n\nDetalhe técnico: $error';
    }

    return 'Não foi possível carregar o modelo.\n\nDetalhe técnico: $error';
  }

  Future<void> dispose() async {
    _interpreter?.close();
    _interpreter = null;
    _config = null;
    _inputBuffer = null;
    _outputBuffer = null;
    _outputShape = null;
  }

  /// Executa a detecção sobre o arquivo de imagem informado.
  Future<InferenceResult> detectFile(File file) async {
    final bytes = await file.readAsBytes();
    return detectBytes(bytes);
  }

  /// Executa a detecção sobre os bytes de uma imagem codificada.
  Future<InferenceResult> detectBytes(Uint8List bytes) async {
    final interpreter = _interpreter;
    final config = _config;
    final inputBuffer = _inputBuffer;
    final outputBuffer = _outputBuffer;
    final outputShape = _outputShape;

    if (interpreter == null ||
        config == null ||
        inputBuffer == null ||
        outputBuffer == null ||
        outputShape == null) {
      throw StateError(
        'Nenhuma configuração carregada. Invoque load() antes de detectar.',
      );
    }

    // --- Pré-processamento ---
    final preprocessWatch = Stopwatch()..start();

    var decoded = img.decodeImage(bytes);
    if (decoded == null) {
      throw const FormatException('Não foi possível decodificar a imagem.');
    }

    _fillInputBuffer(decoded, inputBuffer);

    // Libera a referência à imagem decodificada imediatamente após o
    // preenchimento do tensor. Em execuções sobre conjuntos extensos, a
    // retenção dessas estruturas eleva progressivamente o consumo de
    // memória do processo.
    decoded = null;

    preprocessWatch.stop();

    // --- Inferência ---
    final inferenceWatch = Stopwatch()..start();

    interpreter.runInference([inputBuffer.buffer.asUint8List()]);

    final outputTensor = interpreter.getOutputTensor(0);
    outputBuffer.setAll(
      0,
      outputTensor.data.buffer.asFloat32List(0, outputBuffer.length),
    );

    inferenceWatch.stop();

    // --- Decodificação ---
    final postprocessWatch = Stopwatch()..start();

    final detections = config.variant.architecture == Architecture.yolov8n
        ? _decodeYolov8(outputBuffer, outputShape)
        : _decodeYolov10(outputBuffer, outputShape);

    postprocessWatch.stop();

    return InferenceResult(
      detections: detections,
      preprocessMs: preprocessWatch.elapsedMicroseconds / 1000,
      inferenceMs: inferenceWatch.elapsedMicroseconds / 1000,
      postprocessMs: postprocessWatch.elapsedMicroseconds / 1000,
    );
  }

  // ---------------------------------------------------------------------
  // Pré-processamento
  // ---------------------------------------------------------------------

  /// Prepara a imagem e preenche o buffer de entrada.
  ///
  /// O redimensionamento preserva a proporção original da imagem, sendo as
  /// margens remanescentes preenchidas com valor uniforme, procedimento
  /// correspondente ao adotado durante o treinamento.
  void _fillInputBuffer(img.Image source, Float32List buffer) {
    const size = ModelVariant.inputSize;
    const padValue = 114 / 255.0;

    final scale =
        size / (source.width > source.height ? source.width : source.height);

    final scaledWidth = (source.width * scale).round();
    final scaledHeight = (source.height * scale).round();

    final padX = ((size - scaledWidth) / 2).floor();
    final padY = ((size - scaledHeight) / 2).floor();

    final resized = img.copyResize(
      source,
      width: scaledWidth,
      height: scaledHeight,
      interpolation: img.Interpolation.linear,
    );

    buffer.fillRange(0, buffer.length, padValue);

    for (var y = 0; y < scaledHeight; y++) {
      var index = ((y + padY) * size + padX) * 3;

      for (var x = 0; x < scaledWidth; x++) {
        final pixel = resized.getPixel(x, y);
        buffer[index++] = pixel.rNormalized.toDouble();
        buffer[index++] = pixel.gNormalized.toDouble();
        buffer[index++] = pixel.bNormalized.toDouble();
      }
    }
  }

  // ---------------------------------------------------------------------
  // Decodificação — YOLOv8n
  // ---------------------------------------------------------------------

  /// Decodifica a saída do YOLOv8n, de formato (1, 5, 18900).
  ///
  /// O buffer é organizado por atributo: os primeiros valores correspondem
  /// às coordenadas horizontais do centro, os seguintes às verticais, e
  /// assim sucessivamente, até a confiança.
  List<Detection> _decodeYolov8(Float32List buffer, List<int> shape) {
    final numCandidates = shape[2];

    const offsetCx = 0;
    final offsetCy = numCandidates;
    final offsetW = numCandidates * 2;
    final offsetH = numCandidates * 3;
    final offsetConf = numCandidates * 4;

    final candidates = <Detection>[];

    for (var i = 0; i < numCandidates; i++) {
      final confidence = buffer[offsetConf + i];
      if (confidence < confidenceThreshold) continue;

      final cx = buffer[offsetCx + i];
      final cy = buffer[offsetCy + i];
      final w = buffer[offsetW + i];
      final h = buffer[offsetH + i];

      candidates.add(
        Detection(
          left: (cx - w / 2).clamp(0.0, 1.0),
          top: (cy - h / 2).clamp(0.0, 1.0),
          right: (cx + w / 2).clamp(0.0, 1.0),
          bottom: (cy + h / 2).clamp(0.0, 1.0),
          confidence: confidence,
        ),
      );
    }

    return _nonMaximumSuppression(candidates);
  }

  /// Supressão não máxima.
  List<Detection> _nonMaximumSuppression(List<Detection> candidates) {
    if (candidates.isEmpty) return const [];

    candidates.sort((a, b) => b.confidence.compareTo(a.confidence));

    final selected = <Detection>[];

    for (final candidate in candidates) {
      var overlaps = false;

      for (final accepted in selected) {
        if (candidate.iou(accepted) > nmsThreshold) {
          overlaps = true;
          break;
        }
      }

      if (!overlaps) {
        selected.add(candidate);
        if (selected.length >= maxDetections) break;
      }
    }

    return selected;
  }

  // ---------------------------------------------------------------------
  // Decodificação — YOLOv10n
  // ---------------------------------------------------------------------

  /// Decodifica a saída do YOLOv10n, de formato (1, 300, 6).
  ///
  /// A arquitetura dispensa a supressão não máxima, entregando as detecções
  /// já filtradas e ordenadas por confiança decrescente.
  List<Detection> _decodeYolov10(Float32List buffer, List<int> shape) {
    final numDetections = shape[1];
    final stride = shape[2];

    final detections = <Detection>[];

    for (var i = 0; i < numDetections; i++) {
      final base = i * stride;
      final confidence = buffer[base + 4];

      if (confidence < confidenceThreshold) break;

      detections.add(
        Detection(
          left: buffer[base].clamp(0.0, 1.0),
          top: buffer[base + 1].clamp(0.0, 1.0),
          right: buffer[base + 2].clamp(0.0, 1.0),
          bottom: buffer[base + 3].clamp(0.0, 1.0),
          confidence: confidence,
          classIndex: buffer[base + 5].toInt(),
        ),
      );
    }

    return detections;
  }
}
