import 'dart:io';

import 'package:cafescan/theme/CoffeColors.dart';
import 'package:cafescan/theme/CoffeFonts.dart';
import 'package:cafescan/widgets/NavBar.dart';
import 'package:cafescan/widgets/Photos.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

class CapturePage extends StatefulWidget {
  const CapturePage({super.key});

  @override
  State<CapturePage> createState() => _CapturePageState();
}

class _CapturePageState extends State<CapturePage> {
  File? _photo;

  Future<void> _pick(ImageSource source) async {
    final picked = await ImagePicker().pickImage(
      source: source,
      imageQuality: 90,
    );

    if (picked == null) return;

    final file = File(picked.path);

    setState(() => _photo = file);
  }

  @override
  Widget build(BuildContext context) {
    final sizeOf = MediaQuery.of(context).size;
    return Scaffold(
      body: Column(
        spacing: sizeOf.height * 0.02,
        children: [
          Padding(
            padding: EdgeInsets.only(
              top: sizeOf.height * 0.06,
              left: sizeOf.width * 0.05,
              right: sizeOf.width * 0.05,
            ),
            child: Photos(photo: _photo),
          ),
          if (_photo != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: CoffeColors.surface,
                borderRadius: BorderRadius.circular(40),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('5 grãos detectados', style: CoffeFonts.primaryText),
                  const SizedBox(height: 4),
                  Row(
                    spacing: sizeOf.width * 0.03,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          vertical: 4,
                          horizontal: 8,
                        ),
                        decoration: BoxDecoration(
                          color: CoffeColors.neutral200,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '2 cereja',
                          style: CoffeFonts.normalText.copyWith(
                            color: CoffeColors.accent900,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          vertical: 4,
                          horizontal: 8,
                        ),
                        decoration: BoxDecoration(
                          color: CoffeColors.accent2_200,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '2 verde',
                          style: CoffeFonts.normalText.copyWith(
                            color: CoffeColors.accent2_900,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          vertical: 4,
                          horizontal: 8,
                        ),
                        decoration: BoxDecoration(
                          color: CoffeColors.neutral100,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '1 seco',
                          style: CoffeFonts.normalText.copyWith(
                            color: CoffeColors.neutral900,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          Spacer(),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              ElevatedButton.icon(
                onPressed: () => _pick(ImageSource.camera),
                icon: const Icon(Icons.camera_alt_outlined, size: 18),
                label: const Text('Capturar'),
              ),
              OutlinedButton.icon(
                onPressed: () => _pick(ImageSource.gallery),
                icon: const Icon(Icons.photo_library_outlined, size: 18),
                label: const Text('Galeria'),
              ),
            ],
          ),
          SizedBox(height: sizeOf.height * 0.03),
        ],
      ),
      bottomNavigationBar: const NavBar(currentIndex: 1),
    );
  }
}
