/// Shared in-memory store for batch run metrics.
/// Simple singleton so BatchesPage and MetricsPage see the same data
/// without wiring a full state-management package.
class LastRun {
  final String configLabel;
  final String delegate;
  final int imagesTotal;
  final String timestamp;
  final String avgLatencyMs;
  final String stdDevMs;
  final int ramMB;
  final String tempC;
  final String tempDelta;
  final String batteryUsedPct;
  const LastRun({
    required this.configLabel,
    required this.delegate,
    required this.imagesTotal,
    required this.timestamp,
    required this.avgLatencyMs,
    required this.stdDevMs,
    required this.ramMB,
    required this.tempC,
    required this.tempDelta,
    required this.batteryUsedPct,
  });
}

class MetricsStore {
  MetricsStore._();
  static final MetricsStore instance = MetricsStore._();

  final List<LastRun> runs = [];

  void addRun(LastRun run) => runs.insert(0, run);
}
