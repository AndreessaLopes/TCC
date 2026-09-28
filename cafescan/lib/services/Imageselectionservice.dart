import 'dart:io';

import 'package:file_picker/file_picker.dart';

/// Extensões reconhecidas na seleção.
const _extensions = ['jpg', 'jpeg', 'png', 'bmp', 'webp'];

/// Conjunto de imagens selecionado para a execução em lote.
class ImageSelection {
  final List<File> files;

  /// Quantidade de itens escolhidos cujo caminho não pôde ser resolvido
  /// pelo sistema, situação que ocorre com arquivos mantidos em serviços
  /// de armazenamento remoto.
  final int unresolved;

  const ImageSelection({required this.files, this.unresolved = 0});

  bool get isEmpty => files.isEmpty;
  int get length => files.length;

  /// Diretório comum aos arquivos selecionados, quando aplicável.
  String? get commonDirectory {
    if (files.isEmpty) return null;

    final first = files.first.parent.path;
    for (final file in files) {
      if (file.parent.path != first) return null;
    }
    return first;
  }
}

/// Realiza a seleção das imagens que compõem o lote.
///
/// A seleção múltipla de arquivos foi adotada em substituição ao seletor de
/// galeria do sistema, cujo limite de itens simultâneos impede a escolha do
/// conjunto completo de teste em determinadas versões do Android.
class ImageSelectionService {
  /// Apresenta o seletor de arquivos e retorna as imagens escolhidas,
  /// ordenadas por nome.
  ///
  /// A ordenação assegura que a mesma sequência seja processada em todas as
  /// configurações avaliadas, condição necessária à comparabilidade das
  /// medições.
  static Future<ImageSelection?> pick() async {
    final result = await FilePicker.pickFiles(
      allowMultiple: true,
      type: FileType.custom,
      allowedExtensions: _extensions,
      dialogTitle: 'Selecione as imagens do conjunto de teste',
    );

    if (result.isEmpty) return null;

    final files = <File>[];
    var unresolved = 0;

    for (final item in result) {
      final path = item.path;

      if (path == null) {
        unresolved++;
        continue;
      }

      final file = File(path);
      if (await file.exists()) {
        files.add(file);
      } else {
        unresolved++;
      }
    }

    files.sort((a, b) => a.path.compareTo(b.path));

    return ImageSelection(files: files, unresolved: unresolved);
  }
}
