import 'package:flutter/material.dart';
import 'package:frontend/models/category.dart';
import 'package:frontend/views/form_screen.dart';
import 'package:frontend/views/test_results_screen.dart'; // Importa la pantalla de resultados
import 'package:frontend/services/category_service.dart';

class CategoryDetailScreen extends StatefulWidget {
  final Category category;

  const CategoryDetailScreen({super.key, required this.category});

  @override
  CategoryDetailScreenState createState() => CategoryDetailScreenState();
}

class CategoryDetailScreenState extends State<CategoryDetailScreen> {
  Future<void> _loadAndNavigateToTestForm(BuildContext context) async {
    try {
      final categoryService = CategoryService();
      final form = await categoryService.fetchTestFormByCategoryId(widget.category.id);
      if (!context.mounted) return;
      await Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => FormScreen(
            form: form,
            categoryId: widget.category.id,
          ),
        ),
      );
    } catch (e) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al cargar el formulario de test: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.category.name), // Usa widget.category para acceder a las propiedades
        backgroundColor: Colors.yellow,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            widget.category.image.isNotEmpty
                ? Image.memory(
                    widget.category.image,
                    width: 100,
                    height: 100,
                    fit: BoxFit.contain,
                  )
                : const Icon(Icons.category, size: 100, color: Colors.grey),
            const SizedBox(height: 20),
            Text(
              widget.category.description,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w400,
                color: Colors.black,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 30),

            // Botón para comenzar el test
            ElevatedButton(
              onPressed: () => _loadAndNavigateToTestForm(context),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.yellow,
                foregroundColor: Colors.black,
              ),
              child: const Text('Comenzar Test'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => TestResultsScreen(categoryId: widget.category.id),
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
              ),
              child: const Text('Últimos resultados'),
            ),
          ],
        ),
      ),
    );
  }
}