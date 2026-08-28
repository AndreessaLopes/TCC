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

  /// Indica que a medição apresentou latência incompatível com a
  /// distribuição observada, situação usualmente decorrente de suspensão
  /// do processo pelo sistema operacional.
  final bool isOutlier;

  const BatchSample({
    required this.fileName,
    required this.detections,
    required this.preprocessMs,
    required this.inferenceMs,
    required this.postprocessMs,
    required this.memoryMB,
    this.isOutlier = false,
  });

  double get totalMs => preprocessMs + inferenceMs + postprocessMs;

  BatchSample copyWith({bool? isOutlier}) => BatchSample(
    fileName: fileName,
    detections: detections,
    preprocessMs: preprocessMs,
    inferenceMs: inferenceMs,
    postprocessMs: postprocessMs,
    memoryMB: memoryMB,
    isOutlier: isOutlier ?? this.isOutlier,
  );
}

/// Estatísticas agregadas de uma execução em lote.
class BatchStatistics {
  final int imagesProcessed;
  final int outliersExcluded;
  final int totalDetections;

  final double meanTotalMs;
  final double meanPreprocessMs;
  final double meanInferenceMs;
  final double meanPostprocessMs;

  final double stdDevTotalMs;
  final double stdDevInferenceMs;

  final double minTotalMs;
  final double maxTotalMs;

  final int peakMemoryMB;
  final Duration elapsed;

  const BatchStatistics({
    required this.imagesProcessed,
    required this.outliersExcluded,
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

  double get fps => meanTotalMs > 0 ? 1000 / meanTotalMs : 0;

  double get meanDetections =>
      imagesProcessed > 0 ? totalDetections / imagesProcessed : 0;

  /// Coeficiente de variação da latência total, expresso em porcentagem.
  double get coefficientOfVariation =>
      meanTotalMs > 0 ? (stdDevTotalMs / meanTotalMs) * 100 : 0;

  /// Constrói as estatísticas a partir das medições válidas.
  ///
  /// Medições identificadas como discrepantes são excluídas do cálculo,
  /// embora permaneçam registradas no arquivo exportado para efeito de
  /// rastreabilidade.
  factory BatchStatistics.from(List<BatchSample> samples, Duration elapsed) {
    final valid = samples.where((s) => !s.isOutlier).toList();
    final excluded = samples.length - valid.length;

    if (valid.isEmpty) {
      return BatchStatistics(
        imagesProcessed: 0,
        outliersExcluded: excluded,
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

    final n = valid.length;

    double mean(double Function(BatchSample) f) =>
        valid.fold<double>(0, (a, s) => a + f(s)) / n;

    double variance(double Function(BatchSample) f, double m) {
      if (n < 2) return 0;
      return valid.fold<double>(0, (a, s) => a + (f(s) - m) * (f(s) - m)) /
          (n - 1);
    }

    final meanTotal = mean((s) => s.totalMs);
    final meanInference = mean((s) => s.inferenceMs);
    final totals = valid.map((s) => s.totalMs).toList()..sort();

    return BatchStatistics(
      imagesProcessed: n,
      outliersExcluded: excluded,
      totalDetections: valid.fold<int>(0, (a, s) => a + s.detections),
      meanTotalMs: meanTotal,
      meanPreprocessMs: mean((s) => s.preprocessMs),
      meanInferenceMs: meanInference,
      meanPostprocessMs: mean((s) => s.postprocessMs),
      stdDevTotalMs: _sqrt(variance((s) => s.totalMs, meanTotal)),
      stdDevInferenceMs: _sqrt(variance((s) => s.inferenceMs, meanInference)),
      minTotalMs: totals.first,
      maxTotalMs: totals.last,
      peakMemoryMB: valid.fold<int>(
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

/// Condições do dispositivo verificadas antes da execução.
class DeviceConditions {
  final int? batteryLevel;
  final bool isSaveMode;
  final bool isCharging;

  const DeviceConditions({
    this.batteryLevel,
    this.isSaveMode = false,
    this.isCharging = false,
  });

  /// Situações que comprometem a comparabilidade das medições.
  List<String> get warnings {
    final list = <String>[];

    if (batteryLevel != null && batteryLevel! < 30) {
      list.add(
        'Bateria em $batteryLevel%. Abaixo de 30% o sistema pode reduzir '
        'a frequência do processador, afetando as medições.',
      );
    }

    if (isSaveMode) {
      list.add(
        'Modo de economia de energia ativo. Desative-o para que as '
        'medições reflitam o desempenho pleno do dispositivo.',
      );
    }

    if (isCharging) {
      list.add(
        'Dispositivo conectado ao carregador. O consumo energético não '
        'poderá ser medido.',
      );
    }

    return list;
  }

  bool get hasWarnings => warnings.isNotEmpty;
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
  final bool wasCancelled;

  const BatchResult({
    required this.config,
    required this.samples,
    required this.statistics,
    required this.startedAt,
    required this.warmupCount,
    this.batteryStart,
    this.batteryEnd,
    this.wasCancelled = false,
  });

  int? get batteryUsed {
    if (batteryStart == null || batteryEnd == null) return null;
    final delta = batteryStart! - batteryEnd!;
    return delta >= 0 ? delta : null;
  }

  String toCsv() {
    final buffer = StringBuffer();
    final s = statistics;

    buffer.writeln('# Configuracao: ${config.label}');
    buffer.writeln('# Modelo: ${config.variant.fileName}');
    buffer.writeln('# Delegate: ${config.delegateLabel}');
    buffer.writeln('# Inicio: ${startedAt.toIso8601String()}');
    buffer.writeln('# Imagens medidas: ${s.imagesProcessed}');
    buffer.writeln('# Medicoes descartadas: ${s.outliersExcluded}');
    buffer.writeln('# Inferencias de aquecimento: $warmupCount');
    if (wasCancelled) {
      buffer.writeln('# ATENCAO: execucao interrompida antes da conclusao');
    }
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
    buffer.writeln(
      '# Desvio inferencia: ${s.stdDevInferenceMs.toStringAsFixed(2)} ms',
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
      'posprocessamento_ms,total_ms,memoria_mb,descartada',
    );

    for (final sample in samples) {
      buffer.writeln(
        '${sample.fileName},'
        '${sample.detections},'
        '${sample.preprocessMs.toStringAsFixed(2)},'
        '${sample.inferenceMs.toStringAsFixed(2)},'
        '${sample.postprocessMs.toStringAsFixed(2)},'
        '${sample.totalMs.toStringAsFixed(2)},'
        '${sample.memoryMB},'
        '${sample.isOutlier ? 1 : 0}',
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

  /// Verifica as condições do dispositivo antes da execução.
  Future<DeviceConditions> checkConditions() async {
    int? level;
    var saveMode = false;
    var charging = false;

    try {
      level = await _battery.batteryLevel;
    } catch (_) {}

    try {
      saveMode = await _battery.isInBatterySaveMode;
    } catch (_) {}

    try {
      final state = await _battery.batteryState;
      charging = state == BatteryState.charging || state == BatteryState.full;
    } catch (_) {}

    return DeviceConditions(
      batteryLevel: level,
      isSaveMode: saveMode,
      isCharging: charging,
    );
  }

  /// Processa a lista de arquivos informada.
  ///
  /// As primeiras [warmupCount] inferências são executadas sem registro,
  /// uma vez que a alocação inicial de recursos pelo interpretador eleva
  /// substancialmente a latência das primeiras execuções.
  ///
  /// Ao final, são identificadas as medições cuja latência excede o limite
  /// superior definido pela amplitude interquartil, procedimento destinado
  /// a excluir valores decorrentes de suspensão do processo pelo sistema
  /// operacional, que não refletem o desempenho do modelo avaliado.
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

    final effectiveWarmup = warmupCount.clamp(0, files.length);

    for (var i = 0; i < effectiveWarmup; i++) {
      if (_cancelled) break;

      try {
        await service.detectFile(files[i]);
      } catch (_) {}

      onProgress?.call(
        i + 1,
        files.length + effectiveWarmup,
        true,
        0,
        _nameOf(files[i]),
      );

      await Future<void>.delayed(const Duration(milliseconds: 50));
    }

    final watch = Stopwatch()..start();

    for (var i = 0; i < files.length; i++) {
      if (_cancelled) break;

      final file = files[i];

      try {
        final result = await service.detectFile(file);

        samples.add(
          BatchSample(
            fileName: _nameOf(file),
            detections: result.count,
            preprocessMs: result.preprocessMs,
            inferenceMs: result.inferenceMs,
            postprocessMs: result.postprocessMs,
            memoryMB: _currentMemoryMB(),
          ),
        );

        onProgress?.call(
          effectiveWarmup + samples.length,
          files.length + effectiveWarmup,
          false,
          samples.last.totalMs,
          samples.last.fileName,
        );
      } catch (_) {
        continue;
      }

      // Pausas periódicas mais longas permitem que o coletor de lixo libere
      // as estruturas alocadas durante a decodificação das imagens. Sem
      // esse intervalo, o consumo de memória cresce ao longo do lote e pode
      // levar ao encerramento do processo pelo sistema operacional.
      if (i % 20 == 19) {
        await Future<void>.delayed(const Duration(milliseconds: 150));
      } else {
        await Future<void>.delayed(Duration.zero);
      }
    }

    watch.stop();

    final batteryEnd = await _readBatteryLevel();
    final marked = _markOutliers(samples);

    return BatchResult(
      config: config,
      samples: marked,
      statistics: BatchStatistics.from(marked, watch.elapsed),
      startedAt: startedAt,
      warmupCount: effectiveWarmup,
      batteryStart: batteryStart,
      batteryEnd: batteryEnd,
      wasCancelled: _cancelled,
    );
  }

  /// Identifica medições discrepantes pelo critério da amplitude
  /// interquartil, adotando como limite superior o terceiro quartil
  /// acrescido de três vezes a amplitude.
  ///
  /// O fator ampliado em relação ao usual restringe a exclusão a valores
  /// nitidamente incompatíveis com a distribuição, preservando a
  /// variabilidade natural das medições.
  List<BatchSample> _markOutliers(List<BatchSample> samples) {
    if (samples.length < 8) return samples;

    final sorted = samples.map((s) => s.totalMs).toList()..sort();

    double quantile(double q) {
      final pos = (sorted.length - 1) * q;
      final lower = pos.floor();
      final upper = pos.ceil();
      if (lower == upper) return sorted[lower];
      return sorted[lower] + (sorted[upper] - sorted[lower]) * (pos - lower);
    }

    final q1 = quantile(0.25);
    final q3 = quantile(0.75);
    final iqr = q3 - q1;
    final upperLimit = q3 + 3 * iqr;

    return samples
        .map((s) => s.totalMs > upperLimit ? s.copyWith(isOutlier: true) : s)
        .toList();
  }

  String _nameOf(File file) => file.path.split(Platform.pathSeparator).last;

  Future<int?> _readBatteryLevel() async {
    try {
      return await _battery.batteryLevel;
    } catch (_) {
      return null;
    }
  }

  int _currentMemoryMB() {
    try {
      return (ProcessInfo.currentRss / (1024 * 1024)).round();
    } catch (_) {
      return 0;
    }
  }
}
