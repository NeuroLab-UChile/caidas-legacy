import 'package:flutter/material.dart';
import 'package:frontend/models/category.dart';
import 'package:frontend/views/form_screen.dart';
import 'package:frontend/services/category_service.dart';

class CategoryDetailScreen extends StatelessWidget {
  final Category category;

  const CategoryDetailScreen({Key? key, required this.category}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(category.name),
        backgroundColor: Colors.yellow,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Icono de la categoría
            category.image.isNotEmpty
                ? Image.memory(
                    category.image, // Mostrar la imagen
                    width: 100,
                    height: 100,
                    fit: BoxFit.contain,
                  )
                : const Icon(Icons.category, size: 100, color: Colors.grey),

            const SizedBox(height: 20),

            // Descripción de la categoría
            Text(
              category.description,
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
              onPressed: () async {
                try {
                  // Llamar al servicio para obtener el formulario
                  final categoryService = CategoryService();
                  final form = await categoryService.fetchFormByCategoryId(category.id);

                  // Navegar a la pantalla del formulario
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => FormScreen(form: form),
                    ),
                  );
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Error al cargar el formulario: $e'),
                    ),
                  );
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.yellow, // Fondo del botón
                foregroundColor: Colors.black, // Texto del botón
              ),
              child: const Text('COMENZAR TEST'),
            ),
          ],
        ),
      ),
    );
  }
}
