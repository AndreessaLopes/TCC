import 'package:cafescan/theme/CoffeColors.dart';
import 'package:flutter/material.dart';

enum Delegate { cpu, gpu }

/// Segmented CPU/GPU picker, styled like Organic's `.seg` / `.seg-opt`.
class ButtonDelegate extends StatelessWidget {
  final Delegate value;
  final ValueChanged<Delegate> onChanged;
  const ButtonDelegate({
    super.key,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(4),
      child: Row(
        children: [
          _segment(context, Delegate.cpu, 'CPU', Icons.memory_rounded),
          _segment(context, Delegate.gpu, 'GPU', Icons.bolt_rounded),
        ],
      ),
    );
  }

  Widget _segment(
    BuildContext context,
    Delegate d,
    String label,
    IconData icon,
  ) {
    final selected = value == d;
    return Expanded(
      child: GestureDetector(
        onTap: () => onChanged(d),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          curve: Curves.easeOut,
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            border: Border.all(
              color: selected ? CoffeColors.accent : CoffeColors.divider,
              width: 1.5,
            ),
            color: selected ? CoffeColors.accent : CoffeColors.bg,
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(d == Delegate.cpu ? 30 : 0),
              bottomLeft: Radius.circular(d == Delegate.cpu ? 30 : 0),
              topRight: Radius.circular(d == Delegate.gpu ? 30 : 0),
              bottomRight: Radius.circular(d == Delegate.gpu ? 30 : 0),
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 18,
                color: selected ? CoffeColors.bg : CoffeColors.neutral700,
              ),
              const SizedBox(width: 6),
              Flexible(
                child: Text(
                  label,
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 14,
                    color: selected ? CoffeColors.bg : CoffeColors.neutral700,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
