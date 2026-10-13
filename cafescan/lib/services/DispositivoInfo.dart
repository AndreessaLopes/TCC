import 'package:device_info_plus/device_info_plus.dart';

/// Identificação do aparelho em que a medição foi executada.
///
/// O cabeçalho dos arquivos de medição registrava apenas a configuração
/// avaliada. Quando as medições passam a ser coletadas também em aparelhos
/// de terceiros, essa informação torna-se indispensável: sem ela os
/// arquivos recebidos não podem ser atribuídos a um dispositivo, e a
/// comparação entre fornecedores de processador gráfico, que motiva a
/// coleta, fica inviável.
///
/// A leitura é assíncrona, ao passo que o cabeçalho é montado de forma
/// síncrona. Por isso os dados são lidos uma única vez e mantidos em
/// memória.
class DispositivoInfo {
  static Map<String, String>? _dados;

  static bool get carregado => _dados != null;

  /// Lê as informações do aparelho. Chamadas subsequentes não repetem a
  /// leitura.
  static Future<void> carregar() async {
    if (_dados != null) return;

    try {
      final info = await DeviceInfoPlugin().androidInfo;
      _dados = {
        'Fabricante': info.manufacturer,
        // Nao usar a chave 'Modelo': ela ja nomeia o arquivo .tflite mais
        // adiante no mesmo cabecalho, e a repeticao faz um leitor que
        // monte um dicionario perder um dos dois valores.
        'Aparelho': info.model,
        'Codinome': info.device,
        'Placa': info.board,
        'Hardware': info.hardware,
        'Android': info.version.release,
        'Nivel de API': '${info.version.sdkInt}',
        'Arquitetura': info.supportedAbis.isEmpty
            ? 'desconhecida'
            : info.supportedAbis.first,
        'Aparelho fisico': info.isPhysicalDevice ? 'sim' : 'nao',
      };
    } catch (erro) {
      // A leitura falha fora do Android. O lote não deve ser perdido por
      // causa disso, de modo que a falha apenas se registra no cabeçalho.
      _dados = {'Identificacao do aparelho': 'indisponivel ($erro)'};
    }
  }

  /// Linhas de comentário para o cabeçalho do arquivo de medição.
  ///
  /// Os campos Placa e Hardware não nomeiam o processador diretamente, mas
  /// o identificam de forma unívoca dentro de cada fabricante, o que basta
  /// para distinguir os aparelhos na análise.
  static List<String> linhasCsv() {
    final dados = _dados;
    if (dados == null) {
      return ['# Aparelho: nao identificado'];
    }
    return [for (final e in dados.entries) '# ${e.key}: ${e.value}'];
  }
}
