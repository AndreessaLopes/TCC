/// Repositório em memória das execuções em lote.
///
/// Mantém os registros compartilhados entre a página de execução e a de
/// métricas, sem a introdução de um pacote de gerenciamento de estado.
class LastRun {
  final String configLabel;
  final String delegate;
  final int imagesTotal;
  final String timestamp;

  /// Latência total média, em milissegundos.
  final String avgLatencyMs;

  /// Desvio padrão da latência total, adotado como indicador de
  /// estabilidade de execução.
  final String stdDevMs;

  /// Tempo médio de inferência, isolado das etapas de preparação e
  /// decodificação.
  final String avgInferenceMs;

  /// Desvio padrão do tempo de inferência.
  final String stdDevInferenceMs;

  /// Taxa de processamento, em quadros por segundo.
  final String fps;

  final int ramMB;

  /// Métricas dependentes de recursos do sistema operacional. Assumem valor
  /// nulo quando indisponíveis no dispositivo.
  final String? tempC;
  final String? tempDelta;
  final String? batteryUsedPct;

  final int totalDetections;

  const LastRun({
    required this.configLabel,
    required this.delegate,
    required this.imagesTotal,
    required this.timestamp,
    required this.avgLatencyMs,
    required this.stdDevMs,
    required this.avgInferenceMs,
    required this.stdDevInferenceMs,
    required this.fps,
    required this.ramMB,
    required this.totalDetections,
    this.tempC,
    this.tempDelta,
    this.batteryUsedPct,
  });

  /// Valor numérico da latência média, utilizado na construção do gráfico
  /// comparativo.
  double get latencyValue => double.tryParse(avgLatencyMs) ?? 0;

  /// Valor numérico do tempo de inferência.
  double get inferenceValue => double.tryParse(avgInferenceMs) ?? 0;
}

class MetricsStore {
  MetricsStore._();
  static final MetricsStore instance = MetricsStore._();

  final List<LastRun> runs = [];

  void addRun(LastRun run) => runs.insert(0, run);

  void clear() => runs.clear();

  /// Agrupa as execuções por configuração, preservando a mais recente de
  /// cada uma. Permite comparar as configurações avaliadas ainda que
  /// alguma tenha sido executada mais de uma vez.
  List<LastRun> get latestPerConfig {
    final seen = <String>{};
    final result = <LastRun>[];

    for (final run in runs) {
      if (seen.add(run.configLabel)) result.add(run);
    }

    return result;
  }
}
