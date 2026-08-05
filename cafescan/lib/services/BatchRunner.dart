import 'dart:io';

import 'package:battery_plus/battery_plus.dart';
import 'package:cafescan/models/DetectionConfig.dart';
import 'package:cafescan/services/DetectionService.dart';

/// Medição individual referente ao processamento de uma imagem.
class BatchSample {
  final String fileName;
  final int detections;
  final double preprocessMs;
  final double inferenceMs;
  final double postprocessMs;
  final int memoryMB;

  const BatchSample({
    required this.fileName,
    required this.detections,
    required this.preprocessMs,
    required this.inferenceMs,
    required this.postprocessMs,
    required this.memoryMB,
  });

  double get totalMs => preprocessMs + inferenceMs + postprocessMs;
}

/// Estatísticas agregadas de uma execução em lote.
///
/// Reúne os indicadores previstos no protocolo experimental: latência média,
/// estabilidade de execução, taxa de processamento e consumo de memória.
class BatchStatistics {
  final int imagesProcessed;
  final int totalDetections;

  final double meanTotalMs;
  final double meanPreprocessMs;
  final double meanInferenceMs;
  final double meanPostprocessMs;

  /// Desvio padrão amostral da latência total, adotado como indicador de
  /// estabilidade de execução.
  final double stdDevTotalMs;

  /// Desvio padrão amostral do tempo de inferência, isolando a variabilidade
  /// atribuível ao modelo.
  final double stdDevInferenceMs;

  final double minTotalMs;
  final double maxTotalMs;

  final int peakMemoryMB;
  final Duration elapsed;

  const BatchStatistics({
    required this.imagesProcessed,
    required this.totalDetections,
    required this.meanTotalMs,
    required this.meanPreprocessMs,
    required this.meanInferenceMs,
    required this.meanPostprocessMs,
    required this.stdDevTotalMs,
    required this.stdDevInferenceMs,
    required this.minTotalMs,
    required this.maxTotalMs,
    required this.peakMemoryMB,
    required this.elapsed,
  });

  /// Taxa de processamento, obtida a partir da latência total média.
  double get fps => meanTotalMs > 0 ? 1000 / meanTotalMs : 0;

  /// Média de detecções por imagem.
  double get meanDetections =>
      imagesProcessed > 0 ? totalDetections / imagesProcessed : 0;

  /// Coeficiente de variação da latência total, expresso em porcentagem.
  ///
  /// Permite comparar a estabilidade entre configurações com latências
  /// médias distintas, uma vez que o desvio padrão absoluto tende a
  /// acompanhar a magnitude da medida.
  double get coefficientOfVariation =>
      meanTotalMs > 0 ? (stdDevTotalMs / meanTotalMs) * 100 : 0;

  factory BatchStatistics.from(List<BatchSample> samples, Duration elapsed) {
    if (samples.isEmpty) {
      return BatchStatistics(
        imagesProcessed: 0,
        totalDetections: 0,
        meanTotalMs: 0,
        meanPreprocessMs: 0,
        meanInferenceMs: 0,
        meanPostprocessMs: 0,
        stdDevTotalMs: 0,
        stdDevInferenceMs: 0,
        minTotalMs: 0,
        maxTotalMs: 0,
        peakMemoryMB: 0,
        elapsed: elapsed,
      );
    }

    final n = samples.length;

    double mean(double Function(BatchSample) selector) =>
        samples.fold<double>(0, (a, s) => a + selector(s)) / n;

    /// Variância amostral, conforme a formulação adotada na metodologia.
    double variance(double Function(BatchSample) selector, double m) {
      if (n < 2) return 0;
      final sumSquares = samples.fold<double>(
        0,
        (a, s) => a + (selector(s) - m) * (selector(s) - m),
      );
      return sumSquares / (n - 1);
    }

    final meanTotal = mean((s) => s.totalMs);
    final meanInference = mean((s) => s.inferenceMs);

    final totals = samples.map((s) => s.totalMs).toList()..sort();

    return BatchStatistics(
      imagesProcessed: n,
      totalDetections: samples.fold<int>(0, (a, s) => a + s.detections),
      meanTotalMs: meanTotal,
      meanPreprocessMs: mean((s) => s.preprocessMs),
      meanInferenceMs: meanInference,
      meanPostprocessMs: mean((s) => s.postprocessMs),
      stdDevTotalMs: _sqrt(variance((s) => s.totalMs, meanTotal)),
      stdDevInferenceMs: _sqrt(variance((s) => s.inferenceMs, meanInference)),
      minTotalMs: totals.first,
      maxTotalMs: totals.last,
      peakMemoryMB: samples.fold<int>(
        0,
        (a, s) => s.memoryMB > a ? s.memoryMB : a,
      ),
      elapsed: elapsed,
    );
  }

  static double _sqrt(double value) {
    if (value <= 0) return 0;
    var x = value;
    var previous = 0.0;
    while ((x - previous).abs() > 1e-9) {
      previous = x;
      x = (x + value / x) / 2;
    }
    return x;
  }
}

/// Resultado completo de uma execução em lote.
class BatchResult {
  final DetectionConfig config;
  final List<BatchSample> samples;
  final BatchStatistics statistics;
  final DateTime startedAt;
  final int warmupCount;
  final int? batteryStart;
  final int? batteryEnd;

  const BatchResult({
    required this.config,
    required this.samples,
    required this.statistics,
    required this.startedAt,
    required this.warmupCount,
    this.batteryStart,
    this.batteryEnd,
  });

  /// Variação do nível de bateria durante a execução, quando disponível.
  int? get batteryUsed {
    if (batteryStart == null || batteryEnd == null) return null;
    final delta = batteryStart! - batteryEnd!;
    return delta >= 0 ? delta : null;
  }

  /// Gera o conteúdo em formato de valores separados por vírgula, contendo
  /// uma linha por imagem processada.
  String toCsv() {
    final buffer = StringBuffer();
    final s = statistics;

    buffer.writeln('# Configuracao: ${config.label}');
    buffer.writeln('# Modelo: ${config.variant.fileName}');
    buffer.writeln('# Delegate: ${config.delegateLabel}');
    buffer.writeln('# Inicio: ${startedAt.toIso8601String()}');
    buffer.writeln('# Imagens medidas: ${s.imagesProcessed}');
    buffer.writeln('# Inferencias de aquecimento descartadas: $warmupCount');
    buffer.writeln('# Duracao total: ${s.elapsed.inSeconds} s');
    buffer.writeln('# Latencia media: ${s.meanTotalMs.toStringAsFixed(2)} ms');
    buffer.writeln('# Desvio padrao: ${s.stdDevTotalMs.toStringAsFixed(2)} ms');
    buffer.writeln(
      '# Coeficiente de variacao: '
      '${s.coefficientOfVariation.toStringAsFixed(2)} %',
    );
    buffer.writeln(
      '# Inferencia media: ${s.meanInferenceMs.toStringAsFixed(2)} ms',
    );
    buffer.writeln('# Memoria de pico: ${s.peakMemoryMB} MB');

    if (batteryStart != null) {
      buffer.writeln('# Bateria inicial: $batteryStart %');
      buffer.writeln('# Bateria final: $batteryEnd %');
      if (batteryUsed != null) {
        buffer.writeln('# Bateria consumida: $batteryUsed %');
      }
    }

    buffer.writeln();

    buffer.writeln(
      'arquivo,deteccoes,preprocessamento_ms,inferencia_ms,'
      'posprocessamento_ms,total_ms,memoria_mb',
    );

    for (final sample in samples) {
      buffer.writeln(
        '${sample.fileName},'
        '${sample.detections},'
        '${sample.preprocessMs.toStringAsFixed(2)},'
        '${sample.inferenceMs.toStringAsFixed(2)},'
        '${sample.postprocessMs.toStringAsFixed(2)},'
        '${sample.totalMs.toStringAsFixed(2)},'
        '${sample.memoryMB}',
      );
    }

    return buffer.toString();
  }
}

/// Executa a inferência sobre um conjunto de imagens, registrando as
/// medições previstas no protocolo experimental.
class BatchRunner {
  final DetectionService service;
  final Battery _battery = Battery();

  BatchRunner(this.service);

  bool _cancelled = false;

  void cancel() => _cancelled = true;

  /// Processa a lista de arquivos informada.
  ///
  /// As primeiras [warmupCount] inferências são executadas sem registro,
  /// uma vez que a alocação inicial de recursos pelo interpretador e a
  /// ausência de dados em memória cache elevam substancialmente a latência
  /// das primeiras execuções, o que distorce as estatísticas agregadas.
  ///
  /// O parâmetro [onProgress] é invocado após cada imagem, permitindo à
  /// interface acompanhar o andamento sem bloquear a execução.
  Future<BatchResult> run({
    required List<File> files,
    required DetectionConfig config,
    int warmupCount = 3,
    void Function(
      int processed,
      int total,
      bool isWarmup,
      double latencyMs,
      String fileName,
    )?
    onProgress,
  }) async {
    _cancelled = false;

    final samples = <BatchSample>[];
    final startedAt = DateTime.now();

    final batteryStart = await _readBatteryLevel();

    // O aquecimento utiliza as primeiras imagens da lista, que são
    // posteriormente processadas de forma regular.
    final effectiveWarmup = warmupCount.clamp(0, files.length);

    for (var i = 0; i < effectiveWarmup; i++) {
      if (_cancelled) break;

      try {
        await service.detectFile(files[i]);
      } catch (_) {
        // Falhas durante o aquecimento não interrompem a execução.
      }

      onProgress?.call(
        i + 1,
        files.length + effectiveWarmup,
        true,
        0,
        files[i].path.split(Platform.pathSeparator).last,
      );

      await Future<void>.delayed(Duration.zero);
    }

    final watch = Stopwatch()..start();

    for (var i = 0; i < files.length; i++) {
      if (_cancelled) break;

      final file = files[i];

      try {
        final result = await service.detectFile(file);

        final sample = BatchSample(
          fileName: file.path.split(Platform.pathSeparator).last,
          detections: result.count,
          preprocessMs: result.preprocessMs,
          inferenceMs: result.inferenceMs,
          postprocessMs: result.postprocessMs,
          memoryMB: _currentMemoryMB(),
        );

        samples.add(sample);

        onProgress?.call(
          effectiveWarmup + samples.length,
          files.length + effectiveWarmup,
          false,
          sample.totalMs,
          sample.fileName,
        );
      } catch (_) {
        // Imagens que não puderem ser processadas são omitidas do conjunto
        // de medições, preservando a integridade das estatísticas.
        continue;
      }

      // Cede o controle ao laço de eventos, permitindo a atualização da
      // interface durante execuções prolongadas.
      await Future<void>.delayed(Duration.zero);
    }

    watch.stop();

    final batteryEnd = await _readBatteryLevel();

    return BatchResult(
      config: config,
      samples: samples,
      statistics: BatchStatistics.from(samples, watch.elapsed),
      startedAt: startedAt,
      warmupCount: effectiveWarmup,
      batteryStart: batteryStart,
      batteryEnd: batteryEnd,
    );
  }

  /// Nível de carga da bateria, em porcentagem.
  ///
  /// Retorna nulo quando a informação não estiver disponível, situação que
  /// ocorre em ambientes virtualizados.
  Future<int?> _readBatteryLevel() async {
    try {
      return await _battery.batteryLevel;
    } catch (_) {
      return null;
    }
  }

  /// Consumo de memória residente do processo, em megabytes.
  int _currentMemoryMB() {
    try {
      return (ProcessInfo.currentRss / (1024 * 1024)).round();
    } catch (_) {
      return 0;
    }
  }
}
