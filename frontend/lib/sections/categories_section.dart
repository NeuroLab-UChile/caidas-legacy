import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:frontend/providers/category_provider.dart';
import 'package:frontend/handlers/category_handler.dart';

class CategoriesSection extends StatelessWidget {
  const CategoriesSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      body: Consumer<CategoryProvider>(
        builder: (context, model, child) {
          if (model.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          return Padding(
            padding:
                const EdgeInsets.symmetric(vertical: 16.0, horizontal: 16.0),
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
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      crossAxisSpacing: 16.0,
                      mainAxisSpacing: 16.0,
                      childAspectRatio: 0.75,
                    ),
                    itemCount: model.categories.length,
                    itemBuilder: (context, index) {
                      final category = model.categories[index];
                      final isSelected =
                          model.selectedCategoryId == category.id;

                      return GestureDetector(
                        onTap: () {
                          // Navegar a la pantalla de detalle de la categoría
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => CategoryHandler(
                                category: category,
                                bottomNavigationBar: BottomNavigationBar(
                                  items: const [
                                    BottomNavigationBarItem(
                                      icon: Icon(Icons.home),
                                      label: 'Home',
                                    ),
                                    BottomNavigationBarItem(
                                      icon: Icon(Icons.search),
                                      label: 'Search',
                                    ),
                                    BottomNavigationBarItem(
                                      icon: Icon(Icons.settings),
                                      label: 'Settings',
                                    ),
                                  ],
                                ),
                              ),
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
                                    offset: const Offset(0, 3),
                                  ),
                                ],
                              ),
                              child: Padding(
                                padding: const EdgeInsets.all(16.0),
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    category.icon != null
                                        ? Image.memory(
                                            category.icon! as Uint8List,
                                            width: 80,
                                            height: 80,
                                            fit: BoxFit.contain,
                                          )
                                        : const Icon(Icons.category,
                                            size: 80, color: Colors.grey),
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
