import 'package:cafescan/theme/CoffeFonts.dart';
import 'package:cafescan/widgets/ModalHelp.dart';
import 'package:flutter/material.dart';
import '../theme/CoffeColors.dart';
import '../widgets/NavBar.dart';

/// Batch (Lote) screen: progress card, current-file preview, live metrics,
/// completion card, and start/pause/cancel controls.
class BatchesPage extends StatefulWidget {
  const BatchesPage({super.key});

  @override
  State<BatchesPage> createState() => _BatchesPageState();
}

class _BatchesPageState extends State<BatchesPage> {
  bool running = false;
  bool done = false;
  int progress = 0;
  double latencyMs = 0;
  double ramMb = 0;

  static const total = 285;
  final String configLabel = 'NanoDet-Plus · GPU';

  void start() {
    setState(() {
      running = true;
      done = false;
      progress = 0;
      latencyMs = 0;
      ramMb = 0;
    });
    Future.doWhile(() async {
      await Future.delayed(const Duration(milliseconds: 90));
      if (!running) return false;
      setState(() {
        progress = (progress + 3).clamp(0, total);
        latencyMs = 19 + (progress % 7);
        ramMb = 96 + progress * 0.08;
        if (progress >= total) {
          running = false;
          done = true;
        }
      });
      return running;
    });
  }

  void cancel() => setState(() {
    running = false;
    done = false;
    progress = 0;
    latencyMs = 0;
    ramMb = 0;
  });

  @override
  Widget build(BuildContext context) {
    final pct = progress / total;

    return Scaffold(
      backgroundColor: CoffeColors.bg,
      appBar: AppBar(
        backgroundColor: CoffeColors.bg,
        title: Row(
          children: [
            Text(
              "Execução em lote",
              style: CoffeFonts.primaryText.copyWith(fontSize: 20),
            ),
            Spacer(),
            Container(
              padding: EdgeInsets.all(8),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(30),
                color: CoffeColors.accent100,
              ),
              child: Text(
                configLabel,
                style: TextStyle(fontSize: 12, color: CoffeColors.accent800),
              ),
            ),
          ],
        ),
        actions: [
          GestureDetector(
            onTap: () {
              ModalHelp.showHelpDialog(context);
            },
            child: Padding(
              padding: const EdgeInsets.only(right: 20),
              child: Container(
                padding: EdgeInsets.all(10),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: CoffeColors.divider, width: 1),
                ),
                child: Text(
                  "?",
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
      bottomNavigationBar: const NavBar(currentIndex: 2),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Progress card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: CoffeColors.surface,
                borderRadius: BorderRadius.circular(40),
                boxShadow: [
                  BoxShadow(
                    color: CoffeColors.neutral400.withValues(alpha: 0.2),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '$progress / $total imagens',
                        style: CoffeFonts.primaryText,
                      ),
                      Container(
                        width: 9,
                        height: 9,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: running
                              ? CoffeColors.accent2
                              : CoffeColors.neutral400,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(999),
                    child: LinearProgressIndicator(
                      value: pct,
                      minHeight: 10,
                      backgroundColor: CoffeColors.neutral200,
                      color: CoffeColors.accent,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    running
                        ? 'Processando lote com $configLabel…'
                        : done
                        ? 'Concluído.'
                        : progress > 0
                        ? 'Pausado.'
                        : 'Pronto para iniciar.',
                    style: CoffeFonts.normalText.copyWith(
                      color: CoffeColors.neutral600,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),

            // Current file preview
            Row(
              children: [
                Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    color: CoffeColors.neutral300,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.image_outlined,
                    color: CoffeColors.neutral600,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'grao_${(progress + 1).clamp(1, total).toString().padLeft(3, '0')}.jpg',
                        style: CoffeFonts.modelFileText.copyWith(fontSize: 14),
                      ),
                      Text(
                        'imagem atual do lote',
                        style: CoffeFonts.normalText.copyWith(
                          color: CoffeColors.neutral600,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),

            // Live metrics
            Row(
              children: [
                Expanded(
                  child: _metricCard(
                    'Latência média (ao vivo)',
                    '${latencyMs.toStringAsFixed(1)} ms',
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _metricCard('RAM (ao vivo)', '${ramMb.round()} MB'),
                ),
              ],
            ),
            const SizedBox(height: 14),

            if (done)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: CoffeColors.accent2_100,
                  borderRadius: BorderRadius.circular(30),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.check,
                          color: CoffeColors.accent2_700,
                          size: 18,
                        ),
                        SizedBox(width: 6),
                        Text(
                          'Lote concluído',
                          style: CoffeFonts.primaryText.copyWith(
                            fontWeight: FontWeight.bold,
                            color: CoffeColors.accent2_700,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '$total imagens processadas com $configLabel.',
                      style: CoffeFonts.normalText.copyWith(fontSize: 14),
                    ),
                    const SizedBox(height: 8),
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton(
                        onPressed: () =>
                            Navigator.pushNamed(context, '/metrics'),
                        child: const Text(
                          'Ver métricas completas',
                          style: TextStyle(fontSize: 14),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

            const SizedBox(height: 20),
            Row(
              children: [
                if (!running)
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: running ? null : start,
                      icon: const Icon(Icons.play_arrow),
                      label: Text(
                        done
                            ? 'Executar novamente'
                            : progress > 0
                            ? 'Retomar lote'
                            : 'Iniciar lote',
                      ),
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _metricCard(String label, String value) {
    final sizeOf = MediaQuery.of(context).size;
    return Container(
      height: sizeOf.height * 0.1,
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
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
}
