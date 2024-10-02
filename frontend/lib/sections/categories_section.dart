import 'package:flutter/material.dart';
import 'package:frontend/providers/category_provider.dart';
import 'package:provider/provider.dart';
import 'dart:typed_data'; // Asegúrate de importar esta librería

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
                      // Mostrar la imagen decodificada desde los bytes
                      category.image.isNotEmpty
                          ? Image.memory(
                              category.image, // Mostrar la imagen
                              width: 80,
                              height: 80,
                              fit: BoxFit.cover,
                            )
                          : const Icon(Icons.category, size: 80),
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
