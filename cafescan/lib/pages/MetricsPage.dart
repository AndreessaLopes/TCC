import 'dart:io';

import 'package:cafescan/theme/CoffeFonts.dart';
import 'package:cafescan/theme/MetricsStore.dart';
import 'package:cafescan/widgets/ModalHelp.dart';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

import '../theme/CoffeColors.dart';
import '../widgets/NavBar.dart';

/// Apresenta as métricas agregadas das execuções em lote realizadas,
/// permitindo comparar as configurações avaliadas.
class MetricsPage extends StatefulWidget {
  const MetricsPage({super.key});

  @override
  State<MetricsPage> createState() => _MetricsPageState();
}

class _MetricsPageState extends State<MetricsPage> {
  /// Alterna entre a comparação por latência total e por tempo de
  /// inferência isolado.
  bool _showInference = false;

  List<LastRun> get runs => MetricsStore.instance.runs;

  bool get hasRuns => runs.isNotEmpty;
  LastRun get lastRun => runs.first;

  /// Configurações a comparar, com a execução mais recente de cada uma.
  List<LastRun> get comparison => MetricsStore.instance.latestPerConfig;

  String _buildCsv() {
    final rows = [
      [
        'timestamp',
        'configuracao',
        'delegate',
        'imagens',
        'latencia_media_ms',
        'desvio_latencia_ms',
        'inferencia_media_ms',
        'desvio_inferencia_ms',
        'fps',
        'ram_mb',
        'deteccoes_total',
        'temperatura_c',
        'bateria_consumida_pct',
      ],
    ];

    for (final r in runs) {
      rows.add([
        r.timestamp,
        r.configLabel,
        r.delegate,
        '${r.imagesTotal}',
        r.avgLatencyMs,
        r.stdDevMs,
        r.avgInferenceMs,
        r.stdDevInferenceMs,
        r.fps,
        '${r.ramMB}',
        '${r.totalDetections}',
        r.tempC ?? '',
        r.batteryUsedPct ?? '',
      ]);
    }

    return rows.map((r) => r.join(',')).join('\n');
  }

  String _buildReportText() {
    final r = lastRun;
    final buffer = StringBuffer()
      ..writeln('CaféScan — relatório de execução')
      ..writeln(r.configLabel)
      ..writeln('${r.imagesTotal} imagens')
      ..writeln('Latência média: ${r.avgLatencyMs} ms (σ ${r.stdDevMs} ms)')
      ..writeln(
        'Inferência: ${r.avgInferenceMs} ms (σ ${r.stdDevInferenceMs} ms)',
      )
      ..writeln('Taxa: ${r.fps} FPS')
      ..writeln('Memória: ${r.ramMB} MB')
      ..writeln('Detecções: ${r.totalDetections}');

    if (r.batteryUsedPct != null) {
      buffer.writeln('Bateria consumida: ${r.batteryUsedPct}%');
    }

    return buffer.toString();
  }

  Future<void> _downloadCsv() async {
    if (!hasRuns) return;

    final dir = await getTemporaryDirectory();
    final file = File('${dir.path}/metricas_cafescan.csv');

    await file.writeAsString(_buildCsv());

    await SharePlus.instance.share(
      ShareParams(
        files: [XFile(file.path)],
        text: 'Métricas CaféScan',
        subject: 'Métricas CaféScan',
      ),
    );
  }

  Future<void> _shareReport() async {
    if (!hasRuns) return;

    await SharePlus.instance.share(
      ShareParams(text: _buildReportText(), subject: 'Relatório CaféScan'),
    );
  }

  void _confirmClear() {
    showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Limpar histórico'),
        content: const Text(
          'As medições registradas serão removidas. Certifique-se de '
          'ter exportado os dados antes de prosseguir.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          TextButton(
            onPressed: () {
              MetricsStore.instance.clear();
              Navigator.pop(context);
              setState(() {});
            },
            child: const Text('Limpar'),
          ),
        ],
      ),
    );
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
            icon: _circleIcon(Icons.download_rounded),
          ),
          IconButton(
            onPressed: hasRuns ? _shareReport : null,
            icon: _circleIcon(Icons.share_rounded),
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
      body: !hasRuns ? _emptyState(context) : _content(),
    );
  }

  Widget _circleIcon(IconData icon) => Container(
    padding: const EdgeInsets.all(8),
    decoration: BoxDecoration(
      shape: BoxShape.circle,
      border: Border.all(color: CoffeColors.divider),
    ),
    child: Icon(icon, size: 16),
  );

  Widget _content() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _lastRunHeader(),
          const SizedBox(height: 14),
          _metricGrid(),
          const SizedBox(height: 14),
          _comparisonChart(),
          const SizedBox(height: 20),
          _history(),
          const SizedBox(height: 12),
          Center(
            child: TextButton.icon(
              onPressed: _confirmClear,
              icon: const Icon(Icons.delete_outline, size: 16),
              label: const Text('Limpar histórico'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _lastRunHeader() {
    return Container(
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
            '${lastRun.imagesTotal} imagens · ${lastRun.timestamp} · '
            '${runs.length} ${runs.length == 1 ? "execução" : "execuções"} registradas',
            style: CoffeFonts.normalText.copyWith(fontSize: 13),
          ),
        ],
      ),
    );
  }

  Widget _metricGrid() {
    final cards = <Widget>[
      _metricCard(
        'Latência total',
        '${lastRun.avgLatencyMs} ms',
        'σ ${lastRun.stdDevMs} ms',
      ),
      _metricCard(
        'Inferência',
        '${lastRun.avgInferenceMs} ms',
        'σ ${lastRun.stdDevInferenceMs} ms',
      ),
      _metricCard('Taxa', '${lastRun.fps} FPS', 'quadros por segundo'),
      _metricCard('Memória', '${lastRun.ramMB} MB', 'pico do processo'),
      _metricCard(
        'Detecções',
        '${lastRun.totalDetections}',
        'no lote completo',
      ),
    ];

    // Métricas dependentes do sistema operacional, exibidas apenas quando
    // efetivamente coletadas.
    if (lastRun.batteryUsedPct != null) {
      cards.add(
        _metricCard(
          'Bateria',
          '-${lastRun.batteryUsedPct}%',
          'consumida no lote',
        ),
      );
    }

    if (lastRun.tempC != null) {
      cards.add(
        _metricCard(
          'Temperatura',
          '${lastRun.tempC}°C',
          lastRun.tempDelta != null ? '+${lastRun.tempDelta}°C no lote' : '',
        ),
      );
    }

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 10,
      crossAxisSpacing: 10,
      childAspectRatio: 1.5,
      children: cards,
    );
  }

  /// Gráfico comparativo entre as configurações avaliadas.
  ///
  /// A escala é determinada pelo maior valor registrado, de modo a
  /// acomodar a amplitude observada nas medições.
  Widget _comparisonChart() {
    final items = comparison;

    final values = items
        .map((r) => _showInference ? r.inferenceValue : r.latencyValue)
        .toList();

    final maxValue = values.isEmpty
        ? 1.0
        : values.reduce((a, b) => a > b ? a : b);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: CoffeColors.surface,
        borderRadius: BorderRadius.circular(30),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  _showInference
                      ? 'INFERÊNCIA POR CONFIGURAÇÃO (MS)'
                      : 'LATÊNCIA TOTAL POR CONFIGURAÇÃO (MS)',
                  style: TextStyle(
                    fontSize: 11,
                    color: CoffeColors.accent600,
                    letterSpacing: 1.2,
                  ),
                ),
              ),
              GestureDetector(
                onTap: () => setState(() => _showInference = !_showInference),
                child: Icon(
                  Icons.swap_horiz_rounded,
                  size: 18,
                  color: CoffeColors.accent600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...items.map(
            (r) => _chartRow(
              r.configLabel,
              _showInference ? r.inferenceValue : r.latencyValue,
              maxValue,
              r.delegate == 'GPU',
            ),
          ),
          if (items.length < 2) ...[
            const SizedBox(height: 6),
            Text(
              'Execute outras configurações para comparar.',
              style: CoffeFonts.normalText.copyWith(
                fontSize: 11.5,
                color: CoffeColors.neutral600,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _history() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Histórico de execuções',
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
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        h.configLabel,
                        style: CoffeFonts.primaryText.copyWith(fontSize: 14),
                      ),
                      Text(
                        '${h.timestamp} · ${h.imagesTotal} img · '
                        '${h.avgLatencyMs} ms · ${h.ramMB} MB',
                        style: CoffeFonts.normalText.copyWith(
                          fontSize: 11,
                          color: CoffeColors.neutral600,
                        ),
                      ),
                    ],
                  ),
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
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            label.toUpperCase(),
            style: TextStyle(
              fontSize: 10.5,
              color: CoffeColors.accent600,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 4),
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              value,
              style: CoffeFonts.primaryText.copyWith(
                fontWeight: FontWeight.bold,
                fontSize: 18,
              ),
            ),
          ),
          const SizedBox(height: 2),
          Text(
            sub,
            style: CoffeFonts.normalText.copyWith(
              fontSize: 10.5,
              color: CoffeColors.neutral600,
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  Widget _chartRow(String label, double ms, double maxMs, bool isGpu) {
    final pct = maxMs > 0 ? (ms / maxMs).clamp(0.03, 1.0) : 0.03;

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          SizedBox(
            width: 110,
            child: Text(
              label,
              style: CoffeFonts.normalText.copyWith(
                fontSize: 10.5,
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
                color: isGpu ? CoffeColors.accent2_700 : CoffeColors.accent,
              ),
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
            width: 52,
            child: Text(
              '${ms.toStringAsFixed(0)} ms',
              textAlign: TextAlign.right,
              style: CoffeFonts.modelFileText.copyWith(fontSize: 11),
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
                'Nenhuma execução registrada',
                style: CoffeFonts.primaryText.copyWith(fontSize: 15),
              ),
              const SizedBox(height: 4),
              Text(
                'Execute um lote para que as métricas sejam exibidas aqui.',
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
