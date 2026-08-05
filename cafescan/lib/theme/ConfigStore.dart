import 'package:cafescan/models/DetectionConfig.dart';
import 'package:cafescan/services/DetectionService.dart';
import 'package:cafescan/widgets/ButtonDelegate.dart';
import 'package:flutter/foundation.dart';

/// Mantém a configuração experimental ativa e o serviço de detecção
/// correspondente, compartilhados entre as telas da aplicação.
///
/// Segue o padrão adotado em `MetricsStore`, evitando a introdução de um
/// pacote adicional de gerenciamento de estado.
class ConfigStore extends ChangeNotifier {
  ConfigStore._();
  static final ConfigStore instance = ConfigStore._();

  final DetectionService service = DetectionService();

  ModelVariant _variant = ModelVariant.all.first;
  Delegate _delegate = Delegate.cpu;

  bool _loading = false;
  String? _error;

  ModelVariant get variant => _variant;
  Delegate get delegate => _delegate;
  bool get loading => _loading;
  String? get error => _error;

  DetectionConfig get config =>
      DetectionConfig(variant: _variant, delegate: _delegate);

  /// Indica se o serviço está pronto para executar inferências com a
  /// configuração atualmente selecionada.
  bool get isReady => service.isReady && service.config?.label == config.label;

  /// Seleciona uma variante de modelo e recarrega o serviço.
  Future<void> selectVariant(ModelVariant variant) async {
    if (_variant.label == variant.label) return;
    _variant = variant;
    await _reload();
  }

  /// Seleciona o delegate de execução e recarrega o serviço.
  Future<void> selectDelegate(Delegate delegate) async {
    if (_delegate == delegate) return;
    _delegate = delegate;
    await _reload();
  }

  /// Garante que o serviço esteja carregado com a configuração atual.
  ///
  /// Deve ser invocado antes da primeira inferência, uma vez que a seleção
  /// inicial não dispara carregamento automático.
  Future<void> ensureLoaded() async {
    if (isReady || _loading) return;
    await _reload();
  }

  Future<void> _reload() async {
    _loading = true;
    _error = null;
    notifyListeners();

    try {
      await service.load(config);
    } catch (e) {
      _error = e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  @override
  void dispose() {
    service.dispose();
    super.dispose();
  }
}
