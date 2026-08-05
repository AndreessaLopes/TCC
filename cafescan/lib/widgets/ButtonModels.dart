import 'package:cafescan/theme/CoffeColors.dart';
import 'package:cafescan/theme/CoffeFonts.dart';
import 'package:flutter/material.dart';

class ButtonModels extends StatefulWidget {
  const ButtonModels({
    super.key,
    this.isActive = false,
    required this.model,
    required this.modelFile,
    required this.photoPixelSize,
    required this.modelDescription,
    required this.photoMemorySize,
    required this.onChanged,
    required this.value,
    required this.selectedModel,
  });

  final bool? isActive;
  final String model;
  final String selectedModel;
  final String modelFile;
  final String photoPixelSize;
  final String modelDescription;
  final String photoMemorySize;
  final ValueChanged<String> onChanged;
  final String value;

  @override
  State<ButtonModels> createState() => _ButtonModelsState();
}

class _ButtonModelsState extends State<ButtonModels> {
  @override
  Widget build(BuildContext context) {
    final sizeOf = MediaQuery.of(context).size;

    return Container(
      padding: EdgeInsets.symmetric(
        vertical: sizeOf.height * 0.01,
        horizontal: sizeOf.width * 0.04,
      ),
      decoration: BoxDecoration(
        color: widget.isActive! ? CoffeColors.accent100 : CoffeColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: widget.isActive!
            ? Border.all(color: CoffeColors.accent)
            : Border.all(style: BorderStyle.none),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        spacing: sizeOf.height * 0.01,
        children: [
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(widget.model, style: CoffeFonts.primaryText),
              Spacer(),
              RadioGroup<String>(
                onChanged: (String? value) {
                  if (value != null) {
                    widget.onChanged(value);
                  }
                },
                groupValue: widget.selectedModel,
                child: Radio<String>(
                  value: widget.value,
                  activeColor: CoffeColors.accent,
                  side: BorderSide(color: CoffeColors.neutral400, width: 2),
                ),
              ),
            ],
          ),
          Text(
            widget.modelFile,
            style: CoffeFonts.modelFileText.copyWith(
              color: CoffeColors.neutral600,
              fontWeight: FontWeight.w600,
            ),
          ),
          Row(
            spacing: sizeOf.width * 0.03,
            children: [
              Container(
                padding: EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: CoffeColors.accent100,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  widget.photoMemorySize,
                  style: CoffeFonts.normalText.copyWith(
                    color: CoffeColors.accent800,
                    fontSize: 12,
                  ),
                ),
              ),
              Container(
                padding: EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: CoffeColors.accent100,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  widget.photoPixelSize,
                  style: CoffeFonts.normalText.copyWith(
                    color: CoffeColors.accent800,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
          Text(
            widget.modelDescription,
            style: CoffeFonts.normalText.copyWith(
              color: CoffeColors.accent700,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
          SizedBox(height: sizeOf.height * 0.003),
        ],
      ),
    );
  }
}
