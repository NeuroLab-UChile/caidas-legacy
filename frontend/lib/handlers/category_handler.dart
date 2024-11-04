import 'package:flutter/material.dart';
import 'package:frontend/models/category.dart';
import 'package:frontend/views/physical_activity_screen.dart';

class CategoryHandler extends StatelessWidget {
  final Category category;

  const CategoryHandler({super.key, required this.category});

  @override
  Widget build(BuildContext context) {

    switch (category.name) {
      case "Actividad Física":
        return const PhysicalActivityScreen();

      default:
        return _tempCategoryScreen(
          category: category,
          color: Colors.yellow,
          icon: Icons.category,
        );
    }
  }

  // Temporary widget until specific screens are created
  Widget _tempCategoryScreen({
    required Category category,
    required Color color,
    required IconData icon,
  }) {
    return Scaffold(
      appBar: AppBar(
        title: Text(category.name),
        backgroundColor: color,
      ),
      body: Center(
        child: Text('Placeholder for ${category.name} screen'),
      ),
    );
  }
}
