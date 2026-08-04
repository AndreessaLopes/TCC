import 'package:cafescan/theme/CoffeColors.dart';
import 'package:cafescan/theme/CoffeFonts.dart';
import 'package:flutter/material.dart';

class ModalHelp {
  static void showHelpDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: CoffeColors.bg,
          title: Text(
            'Como usar o CaféScan',
            style: CoffeFonts.primaryText.copyWith(fontSize: 20),
          ),
          content: RichText(
            text: TextSpan(
              style: TextStyle(fontSize: 14, color: Colors.black),
              children: [
                TextSpan(
                  text: 'Configuração —',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                TextSpan(
                  text:
                      ' toque em um modelo (.tflite) e escolha CPU ou GPU. A troca é instantânea, sem recarregar o app.\n\n',
                ),
                TextSpan(
                  text: 'Captura —',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                TextSpan(
                  text:
                      " tire uma foto ou escolha da galeria. Os grãos detectados aparecem com caixas coloridas: terracota = cereja, verde = verde, marrom = seco.\n\n",
                ),
                TextSpan(
                  text: "Lote —",
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                TextSpan(
                  text:
                      " roda 285 imagens automaticamente com a configuração ativa, mostrando progresso e métricas ao vivo.\n\n",
                ),
                TextSpan(
                  text: "Métricas —",
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                TextSpan(
                  text:
                      " depois de um lote, veja latência média, desvio padrão, RAM, temperatura e bateria, e exporte em CSV ou como texto.",
                ),
                TextSpan(
                  text:
                      '\n\nToque no ícone "?" em qualquer tela para reabrir esta ajuda.',
                  style: TextStyle(color: CoffeColors.neutral400),
                ),
              ],
            ),
          ),
          actions: <Widget>[
            ElevatedButton(
              child: Text('Entendi'),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
          ],
        );
      },
    );
  }
}
