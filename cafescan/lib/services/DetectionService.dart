import 'dart:io';
import 'dart:typed_data';

import 'package:cafescan/models/Detection.dart';
import 'package:cafescan/models/DetectionConfig.dart';
import 'package:cafescan/widgets/ButtonDelegate.dart' as app_delegate;
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';

/// Serviço responsável pela execução local dos modelos de detecção.
///
/// Encapsula o carregamento do interpretador TensorFlow Lite, o
/// pré-processamento das imagens, a execução da inferência e a decodificação
/// das saídas, que diferem conforme a arquitetura utilizada.
class DetectionService {
  Interpreter? _interpreter;
  DetectionConfig? _config;

  /// Buffers reutilizados entre inferências consecutivas.
  ///
  /// A alocação dos tensores representa parcela significativa do tempo de
  /// processamento quando realizada a cada imagem. Como o formato é fixo
  /// para uma dada configuração, os buffers são criados uma única vez no
  /// carregamento e reaproveitados.
  Float32List? _inputBuffer;
  Float32List? _outputBuffer;
  List<int>? _outputShape;

  /// Limiar mínimo de confiança para que uma detecção seja considerada.
  /// Corresponde ao valor adotado na validação em ambiente de
  /// desenvolvimento.
  double confidenceThreshold = 0.25;

  /// Limiar de interseção sobre união empregado na supressão não máxima.
  /// Corresponde ao valor adotado na validação, assegurando comparabilidade
  /// entre as medições realizadas no dispositivo e as obtidas previamente.
  /// Aplicável apenas ao YOLOv8n, uma vez que o YOLOv10n dispensa a etapa.
  double nmsThreshold = 0.7;

  /// Número máximo de detecções retornadas por imagem.
  int maxDetections = 300;

  DetectionConfig? get config => _config;
  bool get isReady => _interpreter != null;

  /// Carrega a configuração informada, substituindo a anterior.
  ///
  /// A troca entre configurações exige recriar o interpretador, uma vez que
  /// tanto o arquivo do modelo quanto o delegate são definidos em sua
  /// construção.
  Future<void> load(DetectionConfig config) async {
    await dispose();

    final options = InterpreterOptions();

    if (config.delegate == app_delegate.Delegate.gpu) {
      // O delegate de GPU redireciona parte do grafo para a unidade de
      // processamento gráfico do dispositivo.
      options.addDelegate(GpuDelegateV2());
    } else {
      // O delegate otimizado para CPU utiliza os núcleos disponíveis.
      options.threads = Platform.numberOfProcessors;
    }

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

    final decoded = img.decodeImage(bytes);
    if (decoded == null) {
      throw const FormatException('Não foi possível decodificar a imagem.');
    }

    _fillInputBuffer(decoded, inputBuffer);
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
  /// margens remanescentes preenchidas com valor uniforme. Esse procedimento
  /// corresponde ao adotado pela biblioteca de treinamento, e sua omissão
  /// introduz distorção geométrica que compromete a correspondência entre as
  /// caixas preditas e os objetos presentes na cena.
  ///
  /// O preenchimento é realizado sobre um buffer contíguo de ponto
  /// flutuante, evitando a criação de estruturas intermediárias. Os valores
  /// são normalizados para o intervalo [0, 1].
  void _fillInputBuffer(img.Image source, Float32List buffer) {
    const size = ModelVariant.inputSize;
    const padValue = 114 / 255.0; // Valor de preenchimento das margens.

    // Escala determinada pelo maior lado, preservando a proporção.
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

    // Preenche integralmente o buffer com o valor das margens e, em
    // seguida, sobrescreve a região correspondente à imagem.
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
  /// O buffer é organizado por atributo: os primeiros 18.900 valores
  /// correspondem às coordenadas horizontais do centro, os seguintes às
  /// verticais, e assim sucessivamente, até a confiança. As coordenadas são
  /// normalizadas em relação à resolução de entrada.
  ///
  /// A arquitetura não realiza filtragem interna, de modo que a supressão
  /// não máxima é aplicada nesta etapa.
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
  ///
  /// Ordena as detecções por confiança decrescente e descarta aquelas cuja
  /// sobreposição com uma detecção já aceita excede o limiar estabelecido.
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
  /// Cada detecção ocupa seis posições consecutivas no buffer: as
  /// coordenadas dos cantos, a confiança e o índice da classe. A arquitetura
  /// dispensa a supressão não máxima, entregando as detecções já filtradas e
  /// ordenadas por confiança decrescente.
  List<Detection> _decodeYolov10(Float32List buffer, List<int> shape) {
    final numDetections = shape[1];
    final stride = shape[2];

    final detections = <Detection>[];

    for (var i = 0; i < numDetections; i++) {
      final base = i * stride;
      final confidence = buffer[base + 4];

      // As detecções vêm ordenadas por confiança decrescente; ao encontrar
      // a primeira abaixo do limiar, as seguintes também estarão.
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
