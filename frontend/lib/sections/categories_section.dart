import 'package:flutter/material.dart';
import 'package:frontend/providers/category_provider.dart';
import 'package:provider/provider.dart';

class CategoriesSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        title: const Text('Selecciona una categoría'),
      ),
      body: Consumer<CategoryProvider>(
        builder: (context, model, child) {
          if (model.isLoading) {
            return Center(child: CircularProgressIndicator());
          }
          return GridView.builder(
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              crossAxisSpacing: 10.0,
              mainAxisSpacing: 10.0,
            ),
            itemCount: model.categories.length,
            itemBuilder: (context, index) {
              final category = model.categories[index];
              return GestureDetector(
                onTap: () => model.selectCategory(category.id),
                child: Card(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.category, size: 40.0),
                      const SizedBox(height: 20),
                      Text(category.name, textAlign: TextAlign.center),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
