import 'package:cafescan/theme/CoffeColors.dart';
import 'package:cafescan/theme/CoffeFonts.dart';
import 'package:flutter/material.dart';

class StartPageCard extends StatelessWidget {
  const StartPageCard({super.key, required this.text, required this.number});

  final String text;
  final String number;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: CoffeColors.surface,
        borderRadius: BorderRadius.circular(45),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.2),
            blurRadius: 4,
            offset: Offset(0, 1),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: CoffeColors.accent,
              shape: BoxShape.circle,
            ),
            child: Text(
              number,
              style: CoffeFonts.primaryText.copyWith(
                color: CoffeColors.bg,
                fontSize: 18,
              ),
            ),
          ),
          Text(text, style: TextStyle(fontSize: 13)),
        ],
      ),
    );
  }
}
