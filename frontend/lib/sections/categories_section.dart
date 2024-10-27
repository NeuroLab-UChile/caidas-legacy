import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:frontend/providers/category_provider.dart';
import 'package:frontend/views/category_detail_screen.dart';

class CategoriesSection extends StatelessWidget {
  const CategoriesSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100], // Fondo claro
      body: Consumer<CategoryProvider>(
        builder: (context, model, child) {
          if (model.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 16.0, horizontal: 16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Seleccione una categoría para conocer o evaluar',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w400),
                ),
                const SizedBox(height: 16.0),
                Expanded(
                  child: GridView.builder(
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      crossAxisSpacing: 16.0,
                      mainAxisSpacing: 16.0,
                      childAspectRatio: 0.75, // Ajusta la relación de aspecto de las tarjetas
                    ),
                    itemCount: model.categories.length,
                    itemBuilder: (context, index) {
                      final category = model.categories[index];
                      final isSelected = model.selectedCategoryId == category.id;

                      return GestureDetector(
                        onTap: () {
                          // Navegar a la pantalla de detalle de la categoría
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => CategoryDetailScreen(category: category),
                            ),
                          );
                        },
                        child: Stack(
                          children: [
                            Container(
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(16.0),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black.withOpacity(0.1),
                                    spreadRadius: 1,
                                    blurRadius: 6,
                                    offset: const Offset(0, 3), // sombra suave
                                  ),
                                ],
                              ),
                              child: Padding(
                                padding: const EdgeInsets.all(16.0),
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    // Mostrar la imagen o el ícono
                                    category.image.isNotEmpty
                                        ? Image.memory(
                                            category.image, // Mostrar la imagen
                                            width: 80,
                                            height: 80,
                                            fit: BoxFit.contain,
                                          )
                                        : const Icon(Icons.category, size: 80, color: Colors.grey),
                                    const SizedBox(height: 16),
                                    Text(
                                      category.name,
                                      textAlign: TextAlign.center,
                                      style: const TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.black87,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            // Indicador de selección en la esquina superior izquierda
                            Positioned(
                              top: 8,
                              left: 8,
                              child: isSelected
                                  ? const Icon(
                                      Icons.circle,
                                      color: Colors.black,
                                      size: 24,
                                    )
                                  : const Icon(
                                      Icons.circle_outlined,
                                      color: Colors.black54,
                                      size: 24,
                                    ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
