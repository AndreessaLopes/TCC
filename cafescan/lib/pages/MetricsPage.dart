import 'dart:io';
import 'package:cafescan/theme/CoffeFonts.dart';
import 'package:cafescan/theme/MetricsStore.dart';
import 'package:cafescan/widgets/ModalHelp.dart';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import '../theme/CoffeColors.dart';
import '../widgets/NavBar.dart';

class MetricsPage extends StatefulWidget {
  const MetricsPage({super.key});

  @override
  State<MetricsPage> createState() => _MetricsPageState();
}

class _MetricsPageState extends State<MetricsPage> {
  List<LastRun> get runs => MetricsStore.instance.runs;

  bool get hasRuns => runs.isNotEmpty;
  LastRun get lastRun => runs.first;

  List<(String, double)> get chartBars => !hasRuns
      ? const []
      : [(lastRun.configLabel, double.tryParse(lastRun.avgLatencyMs) ?? 0)];

  String _buildCsv() {
    final rows = [
      [
        'timestamp',
        'modelo',
        'delegate',
        'imagens',
        'latencia_media_ms',
        'desvio_padrao_ms',
        'ram_mb',
        'temperatura_c',
        'bateria_consumida_pct',
      ],
    ];
    for (final r in runs) {
      rows.add([
        r.timestamp,
        r.configLabel.split(' · ').first,
        r.delegate,
        '${r.imagesTotal}',
        r.avgLatencyMs,
        r.stdDevMs,
        '${r.ramMB}',
        r.tempC,
        r.batteryUsedPct,
      ]);
    }
    return rows.map((r) => r.join(',')).join('\n');
  }

  String _buildReportText() {
    final r = lastRun;
    return 'CaféScan — relatório de lote\n${r.configLabel}\n${r.imagesTotal} imagens\n'
        'Latência média: ${r.avgLatencyMs} ms (σ ${r.stdDevMs} ms)\n'
        'RAM: ${r.ramMB} MB\nTemperatura: ${r.tempC}°C (+${r.tempDelta}°C)\n'
        'Bateria consumida: ${r.batteryUsedPct}%';
  }

  Future<void> _downloadCsv() async {
    if (!hasRuns) return;
    final dir = await getTemporaryDirectory();
    final file = File('${dir.path}/metricas_cafescan.csv');
    await file.writeAsString(_buildCsv());
    await Share.shareXFiles([
      XFile(file.path),
    ], text: 'Métricas CaféScan (CSV)');
  }

  Future<void> _shareReport() async {
    if (!hasRuns) return;
    await Share.share(_buildReportText());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: CoffeColors.bg,
      appBar: AppBar(
        backgroundColor: CoffeColors.bg,
        title: Text(
          'Métricas',
          style: CoffeFonts.primaryText.copyWith(fontSize: 20),
        ),
        actions: [
          IconButton(
            onPressed: hasRuns ? _downloadCsv : null,
            icon: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: CoffeColors.divider),
              ),
              child: const Icon(Icons.download_rounded, size: 16),
            ),
          ),
          IconButton(
            onPressed: hasRuns ? _shareReport : null,
            icon: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: CoffeColors.divider),
              ),
              child: const Icon(Icons.share_rounded, size: 16),
            ),
          ),
          GestureDetector(
            onTap: () => ModalHelp.showHelpDialog(context),
            child: Padding(
              padding: const EdgeInsets.only(right: 20),
              child: Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: CoffeColors.divider, width: 1),
                ),
                child: Text(
                  '?',
                  style: CoffeFonts.primaryText.copyWith(
                    fontSize: 20,
                    color: Colors.black,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: const NavBar(currentIndex: 3),
      body: !hasRuns
          ? _emptyState(context)
          : SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: CoffeColors.accent100,
                      borderRadius: BorderRadius.circular(30),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'ÚLTIMA EXECUÇÃO',
                          style: TextStyle(
                            fontSize: 11,
                            color: CoffeColors.accent600,
                            letterSpacing: 1.3,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          lastRun.configLabel,
                          style: CoffeFonts.primaryText.copyWith(
                            fontSize: 16,
                            color: CoffeColors.accent800,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${lastRun.imagesTotal} imagens · ${lastRun.timestamp}',
                          style: CoffeFonts.normalText.copyWith(fontSize: 13),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),

                  GridView.count(
                    crossAxisCount: 2,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    mainAxisSpacing: 10,
                    crossAxisSpacing: 10,
                    childAspectRatio: 1.5,
                    children: [
                      _metricCard(
                        'Latência média',
                        '${lastRun.avgLatencyMs} ms',
                        'σ ${lastRun.stdDevMs} ms',
                      ),
                      _metricCard(
                        'RAM',
                        '${lastRun.ramMB} MB',
                        'pico do processo',
                      ),
                      _metricCard(
                        'Temperatura',
                        '${lastRun.tempC}°C',
                        '+${lastRun.tempDelta}°C no lote',
                      ),
                      _metricCard(
                        'Bateria',
                        '-${lastRun.batteryUsedPct}%',
                        'consumida no lote',
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),

                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: CoffeColors.surface,
                      borderRadius: BorderRadius.circular(30),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'LATÊNCIA POR CONFIGURAÇÃO (MS)',
                          style: TextStyle(
                            fontSize: 11,
                            color: CoffeColors.accent600,
                            letterSpacing: 1.3,
                          ),
                        ),
                        const SizedBox(height: 12),
                        ...chartBars.map((c) => _chartRow(c.$1, c.$2)),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  Text(
                    'Histórico de lotes',
                    style: CoffeFonts.primaryText.copyWith(
                      fontSize: 15,
                      color: CoffeColors.neutral600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ...runs.map(
                    (h) => Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: CoffeColors.surface,
                        borderRadius: BorderRadius.circular(30),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                h.configLabel,
                                style: CoffeFonts.primaryText.copyWith(
                                  fontSize: 14,
                                ),
                              ),
                              Text(
                                '${h.timestamp} · ${h.avgLatencyMs} ms · ${h.ramMB} MB',
                                style: CoffeFonts.normalText.copyWith(
                                  fontSize: 11,
                                  color: CoffeColors.neutral600,
                                ),
                              ),
                            ],
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(999),
                              color: h.delegate == 'GPU'
                                  ? CoffeColors.accent2_100
                                  : CoffeColors.accent100,
                            ),
                            child: Text(
                              h.delegate,
                              style: TextStyle(
                                fontSize: 10.5,
                                color: h.delegate == 'GPU'
                                    ? CoffeColors.accent2_700
                                    : CoffeColors.accent800,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _metricCard(String label, String value, String sub) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: CoffeColors.surface,
        borderRadius: BorderRadius.circular(30),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: TextStyle(
              fontSize: 11,
              color: CoffeColors.accent600,
              letterSpacing: 1.3,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: CoffeFonts.primaryText.copyWith(
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            sub,
            style: CoffeFonts.normalText.copyWith(
              fontSize: 10.5,
              color: CoffeColors.neutral600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _chartRow(String label, double ms) {
    final maxMs = 60.0;
    final pct = (ms / maxMs).clamp(0.05, 1.0);
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          SizedBox(
            width: 90,
            child: Text(
              label,
              style: CoffeFonts.normalText.copyWith(
                fontSize: 11,
                color: CoffeColors.neutral600,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(999),
              child: LinearProgressIndicator(
                value: pct,
                minHeight: 14,
                backgroundColor: CoffeColors.neutral200,
                color: CoffeColors.accent,
              ),
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
            width: 44,
            child: Text(
              '${ms.toStringAsFixed(0)}ms',
              textAlign: TextAlign.right,
              style: CoffeFonts.modelFileText.copyWith(fontSize: 11.5),
            ),
          ),
        ],
      ),
    );
  }

  Widget _emptyState(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Center(
        child: Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: CoffeColors.surface,
            borderRadius: BorderRadius.circular(30),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.insert_chart_outlined_rounded,
                size: 34,
                color: CoffeColors.neutral500,
              ),
              const SizedBox(height: 8),
              Text(
                'Nenhum lote executado ainda',
                style: CoffeFonts.primaryText.copyWith(fontSize: 15),
              ),
              const SizedBox(height: 4),
              Text(
                'Rode um lote de 285 imagens para ver as métricas aqui.',
                textAlign: TextAlign.center,
                style: CoffeFonts.normalText.copyWith(fontSize: 13),
              ),
              const SizedBox(height: 12),
              ElevatedButton(
                onPressed: () =>
                    Navigator.pushReplacementNamed(context, '/batch'),
                child: const Text('Ir para Lote'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
