import 'dart:io';

import 'package:cafescan/services/BatchRunner.dart';
import 'package:cafescan/services/Imageselectionservice.dart';
import 'package:cafescan/theme/ConfigStore.dart';
import 'package:cafescan/theme/CoffeColors.dart';
import 'package:cafescan/theme/CoffeFonts.dart';
import 'package:cafescan/theme/MetricsStore.dart';
import 'package:cafescan/widgets/ModalHelp.dart';
import 'package:cafescan/widgets/NavBar.dart';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:wakelock_plus/wakelock_plus.dart';

/// Execução em lote sobre um conjunto de imagens selecionadas.
///
/// Constitui o instrumento de coleta das métricas previstas no protocolo
/// experimental.
class BatchesPage extends StatefulWidget {
  const BatchesPage({super.key});

  @override
  State<BatchesPage> createState() => _BatchesPageState();
}

class _BatchesPageState extends State<BatchesPage> {
  final _store = ConfigStore.instance;

  BatchRunner? _runner;
  ImageSelection? _selection;

  int _warmupCount = 3;

  bool _picking = false;
  bool _running = false;
  int _processed = 0;
  int _totalSteps = 0;
  bool _isWarmup = false;
  String? _currentFile;
  double _lastLatency = 0;

  BatchResult? _result;
  String? _error;

  List<File> get _files => _selection?.files ?? const [];

  @override
  void dispose() {
    WakelockPlus.disable();
    super.dispose();
  }

  /// Solicita a seleção das imagens que comporão o lote.
  Future<void> _selectImages() async {
    if (_picking || _running) return;

    setState(() {
      _picking = true;
      _error = null;
    });

    try {
      final selection = await ImageSelectionService.pick();
      if (selection == null) return;

      if (!mounted) return;

      if (selection.isEmpty) {
        setState(() {
          _error =
              'Nenhuma imagem pôde ser lida. Verifique se os arquivos '
              'estão armazenados na memória do dispositivo.';
          _selection = null;
        });
        return;
      }

      setState(() {
        _selection = selection;
        _result = null;
        _processed = 0;

        if (selection.unresolved > 0) {
          _error =
              '${selection.unresolved} '
              '${selection.unresolved == 1 ? "arquivo não pôde ser lido" : "arquivos não puderam ser lidos"}. '
              'Arquivos mantidos em serviços de armazenamento remoto não '
              'são acessíveis à aplicação.';
        }
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = 'Falha ao selecionar imagens: $e');
    } finally {
      if (mounted) setState(() => _picking = false);
    }
  }

  /// Verifica as condições do dispositivo e solicita confirmação quando
  /// houver situação que comprometa a comparabilidade das medições.
  Future<bool> _confirmConditions(BatchRunner runner) async {
    final conditions = await runner.checkConditions();
    if (!conditions.hasWarnings) return true;
    if (!mounted) return false;

    final proceed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Condições do dispositivo'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            for (final w in conditions.warnings)
              Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Text(w, style: const TextStyle(fontSize: 13)),
              ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Executar mesmo assim'),
          ),
        ],
      ),
    );

    return proceed ?? false;
  }

  /// Executa a inferência sobre todas as imagens selecionadas.
  Future<void> _start() async {
    if (_files.isEmpty) return;

    try {
      await _store.ensureLoaded();

      if (_store.error != null) {
        setState(() => _error = _store.error);
        return;
      }

      final runner = BatchRunner(_store.service);

      if (!await _confirmConditions(runner)) return;

      if (!mounted) return;
      setState(() {
        _running = true;
        _processed = 0;
        _totalSteps = _files.length + _warmupCount.clamp(0, _files.length);
        _result = null;
        _error = null;
      });

      // Mantém a tela ativa durante a execução. A suspensão do processo
      // pelo sistema operacional produz medições de latência incompatíveis
      // com o desempenho real do modelo.
      await WakelockPlus.enable();

      _runner = runner;

      final result = await runner.run(
        files: _files,
        config: _store.config,
        warmupCount: _warmupCount,
        onProgress: (processed, total, isWarmup, latency, fileName) {
          if (!mounted) return;
          setState(() {
            _processed = processed;
            _totalSteps = total;
            _isWarmup = isWarmup;
            _currentFile = fileName;
            if (!isWarmup) _lastLatency = latency;
          });
        },
      );

      if (!mounted) return;

      setState(() => _result = result);
      _saveRun(result);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    } finally {
      await WakelockPlus.disable();
      if (mounted) setState(() => _running = false);
      _runner = null;
    }
  }

  void _cancel() {
    _runner?.cancel();
    setState(() => _running = false);
  }

  /// Registra a execução no repositório compartilhado de métricas.
  void _saveRun(BatchResult result) {
    final s = result.statistics;

    MetricsStore.instance.addRun(
      LastRun(
        configLabel: result.config.label,
        delegate: result.config.delegateLabel,
        imagesTotal: s.imagesProcessed,
        timestamp: _formatTime(result.startedAt),
        avgLatencyMs: s.meanTotalMs.toStringAsFixed(1),
        stdDevMs: s.stdDevTotalMs.toStringAsFixed(1),
        avgInferenceMs: s.meanInferenceMs.toStringAsFixed(1),
        stdDevInferenceMs: s.stdDevInferenceMs.toStringAsFixed(1),
        fps: s.fps.toStringAsFixed(2),
        ramMB: s.peakMemoryMB,
        totalDetections: s.totalDetections,
        batteryUsedPct: result.batteryUsed?.toString(),
        tempC: null,
        tempDelta: null,
      ),
    );
  }

  String _formatTime(DateTime dt) =>
      '${dt.hour.toString().padLeft(2, '0')}:'
      '${dt.minute.toString().padLeft(2, '0')}';

  /// Exporta as medições em formato de valores separados por vírgula.
  Future<void> _export() async {
    final result = _result;
    if (result == null) return;

    try {
      final dir = await getTemporaryDirectory();
      final stamp = result.startedAt.millisecondsSinceEpoch;
      final name = result.config.label
          .replaceAll(' · ', '_')
          .replaceAll(' ', '');

      final file = File('${dir.path}/lote_${name}_$stamp.csv');
      await file.writeAsString(result.toCsv());

      await SharePlus.instance.share(
        ShareParams(
          files: [XFile(file.path)],
          text: 'Medições — ${result.config.label}',
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Falha ao exportar: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final pct = _totalSteps > 0 ? _processed / _totalSteps : 0.0;

    return Scaffold(
      backgroundColor: CoffeColors.bg,
      appBar: AppBar(
        backgroundColor: CoffeColors.bg,
        title: Text(
          'Execução em lote',
          style: CoffeFonts.primaryText.copyWith(fontSize: 20),
        ),
        actions: [
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
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _configBadge(),
            const SizedBox(height: 12),
            _selectionCard(),
            const SizedBox(height: 16),
            if (_running) ...[_progressCard(pct), const SizedBox(height: 16)],
            if (_error != null) ...[_errorCard(), const SizedBox(height: 16)],
            if (_result != null) ...[
              _resultCard(_result!),
              const SizedBox(height: 16),
            ],
            _controls(),
          ],
        ),
      ),
      bottomNavigationBar: const NavBar(currentIndex: 2),
    );
  }

  Widget _configBadge() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 14),
      decoration: BoxDecoration(
        color: CoffeColors.accent100,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          Icon(Icons.tune_rounded, size: 15, color: CoffeColors.accent600),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              _store.config.label,
              style: TextStyle(fontSize: 13, color: CoffeColors.accent800),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Widget _selectionCard() {
    final selection = _selection;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: CoffeColors.surface,
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            selection == null
                ? 'Nenhuma imagem selecionada'
                : '${selection.length} '
                      '${selection.length == 1 ? "imagem selecionada" : "imagens selecionadas"}',
            style: CoffeFonts.primaryText.copyWith(fontSize: 16),
          ),
          const SizedBox(height: 4),
          Text(
            selection?.commonDirectory ??
                'Selecione as imagens do conjunto de teste. Utilize a opção '
                    'de seleção múltipla do gerenciador de arquivos.',
            style: CoffeFonts.normalText.copyWith(
              fontSize: 12,
              color: CoffeColors.neutral600,
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: (_running || _picking) ? null : _selectImages,
              icon: _picking
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.photo_library_outlined, size: 18),
              label: Text(
                _picking
                    ? 'Carregando...'
                    : selection == null
                    ? 'Selecionar imagens'
                    : 'Trocar seleção',
              ),
            ),
          ),
          Divider(color: CoffeColors.divider, height: 24),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Aquecimento',
                      style: CoffeFonts.normalText.copyWith(fontSize: 13),
                    ),
                    Text(
                      'Inferências descartadas antes de medir',
                      style: CoffeFonts.normalText.copyWith(
                        fontSize: 11,
                        color: CoffeColors.neutral600,
                      ),
                    ),
                  ],
                ),
              ),
              _stepper(),
            ],
          ),
        ],
      ),
    );
  }

  Widget _stepper() {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        IconButton(
          onPressed: _running || _warmupCount == 0
              ? null
              : () => setState(() => _warmupCount--),
          icon: const Icon(Icons.remove_circle_outline, size: 20),
          visualDensity: VisualDensity.compact,
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
        ),
        SizedBox(
          width: 26,
          child: Text(
            '$_warmupCount',
            textAlign: TextAlign.center,
            style: CoffeFonts.primaryText.copyWith(fontSize: 15),
          ),
        ),
        IconButton(
          onPressed: _running || _warmupCount >= 10
              ? null
              : () => setState(() => _warmupCount++),
          icon: const Icon(Icons.add_circle_outline, size: 20),
          visualDensity: VisualDensity.compact,
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
        ),
      ],
    );
  }

  Widget _progressCard(double pct) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: CoffeColors.accent100,
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                '$_processed / $_totalSteps',
                style: CoffeFonts.primaryText.copyWith(
                  fontSize: 18,
                  color: CoffeColors.accent800,
                ),
              ),
              const Spacer(),
              if (_isWarmup)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 3,
                  ),
                  decoration: BoxDecoration(
                    color: CoffeColors.neutral200,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    'aquecimento',
                    style: TextStyle(
                      fontSize: 10,
                      color: CoffeColors.neutral700,
                    ),
                  ),
                )
              else
                Text(
                  '${(pct * 100).toStringAsFixed(0)}%',
                  style: TextStyle(color: CoffeColors.accent800),
                ),
            ],
          ),
          const SizedBox(height: 10),
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: LinearProgressIndicator(
              value: pct,
              minHeight: 8,
              backgroundColor: CoffeColors.neutral200,
              color: _isWarmup ? CoffeColors.neutral500 : CoffeColors.accent,
            ),
          ),
          const SizedBox(height: 10),
          if (_currentFile != null)
            Text(
              _currentFile!,
              style: TextStyle(fontSize: 12, color: CoffeColors.accent700),
              overflow: TextOverflow.ellipsis,
            ),
          if (!_isWarmup)
            Text(
              'Última latência: ${_lastLatency.toStringAsFixed(1)} ms',
              style: TextStyle(fontSize: 12, color: CoffeColors.accent700),
            ),
          const SizedBox(height: 6),
          Row(
            children: [
              Icon(
                Icons.lightbulb_outline,
                size: 13,
                color: CoffeColors.accent600,
              ),
              const SizedBox(width: 5),
              Expanded(
                child: Text(
                  'Mantenha o aplicativo em primeiro plano durante a execução.',
                  style: TextStyle(fontSize: 11, color: CoffeColors.accent600),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _errorCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red[50],
        borderRadius: BorderRadius.circular(24),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.error_outline, size: 18, color: Colors.red[900]),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              _error!,
              style: TextStyle(
                fontSize: 13,
                color: Colors.red[900],
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _resultCard(BatchResult result) {
    final s = result.statistics;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: CoffeColors.surface,
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            result.wasCancelled
                ? 'Execução interrompida'
                : 'Execução concluída',
            style: CoffeFonts.primaryText.copyWith(fontSize: 16),
          ),
          const SizedBox(height: 2),
          Text(
            '${s.imagesProcessed} imagens em ${s.elapsed.inSeconds} s'
            '${result.warmupCount > 0 ? " · ${result.warmupCount} de aquecimento" : ""}',
            style: CoffeFonts.normalText.copyWith(
              fontSize: 13,
              color: CoffeColors.neutral600,
            ),
          ),
          if (s.outliersExcluded > 0) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: CoffeColors.neutral200,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                '${s.outliersExcluded} ${s.outliersExcluded == 1 ? "medição foi excluída" : "medições foram excluídas"} '
                'por apresentar latência incompatível com a distribuição '
                'observada. Os valores permanecem registrados no arquivo '
                'exportado.',
                style: TextStyle(
                  fontSize: 11.5,
                  color: CoffeColors.neutral700,
                  height: 1.4,
                ),
              ),
            ),
          ],
          const SizedBox(height: 14),
          _row('Latência média', '${s.meanTotalMs.toStringAsFixed(1)} ms'),
          _row('Desvio padrão', '${s.stdDevTotalMs.toStringAsFixed(1)} ms'),
          _row(
            'Coeficiente de variação',
            '${s.coefficientOfVariation.toStringAsFixed(1)} %',
          ),
          _row('Mínima', '${s.minTotalMs.toStringAsFixed(1)} ms'),
          _row('Máxima', '${s.maxTotalMs.toStringAsFixed(1)} ms'),
          Divider(color: CoffeColors.divider, height: 20),
          _row(
            'Pré-processamento',
            '${s.meanPreprocessMs.toStringAsFixed(1)} ms',
          ),
          _row('Inferência', '${s.meanInferenceMs.toStringAsFixed(1)} ms'),
          _row(
            'Desvio (inferência)',
            '${s.stdDevInferenceMs.toStringAsFixed(1)} ms',
          ),
          _row(
            'Pós-processamento',
            '${s.meanPostprocessMs.toStringAsFixed(1)} ms',
          ),
          Divider(color: CoffeColors.divider, height: 20),
          _row('Taxa de processamento', '${s.fps.toStringAsFixed(2)} FPS'),
          _row('Memória (pico)', '${s.peakMemoryMB} MB'),
          if (result.batteryStart != null)
            _row(
              'Bateria',
              result.batteryUsed != null
                  ? '${result.batteryStart}% → ${result.batteryEnd}% '
                        '(-${result.batteryUsed}%)'
                  : '${result.batteryStart}% → ${result.batteryEnd}%',
            ),
          _row('Detecções (total)', '${s.totalDetections}'),
          _row('Detecções por imagem', s.meanDetections.toStringAsFixed(1)),
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _export,
              icon: const Icon(Icons.download_outlined, size: 18),
              label: const Text('Exportar CSV'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _row(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Text(
              label,
              style: CoffeFonts.normalText.copyWith(
                fontSize: 13,
                color: CoffeColors.neutral700,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Text(
            value,
            style: CoffeFonts.normalText.copyWith(
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _controls() {
    if (_running) {
      return SizedBox(
        width: double.infinity,
        child: OutlinedButton.icon(
          onPressed: _cancel,
          icon: const Icon(Icons.stop_outlined, size: 18),
          label: const Text('Cancelar'),
        ),
      );
    }

    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: _files.isEmpty ? null : _start,
        icon: const Icon(Icons.play_arrow_rounded, size: 20),
        label: Text(_result == null ? 'Iniciar' : 'Executar novamente'),
      ),
    );
  }
}
