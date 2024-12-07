import 'package:flutter/material.dart';
import 'package:frontend/models/category.dart';

class CategoryHandler extends StatelessWidget {
  final Category category;

  const CategoryHandler({super.key, required this.category});

  @override
  Widget build(BuildContext context) {
    print("category.name: ${category.name}");

    switch (category.name) {
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
        child: Text(category.description ?? 'No description'),
      ),
    );
  }
}
