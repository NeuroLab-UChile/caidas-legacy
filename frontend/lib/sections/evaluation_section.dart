import 'package:flutter/material.dart';
import 'package:frontend/providers/category_provider.dart';
import 'package:provider/provider.dart';

class EvaluationSection extends StatefulWidget {
  const EvaluationSection({super.key});

  @override
  EvaluationSectionState createState() => EvaluationSectionState();
}

class EvaluationSectionState extends State<EvaluationSection> {
  @override
  Widget build(BuildContext context) {
    // Accediendo al provider que mantiene el estado de la categoría seleccionada
    final categoryProvider = Provider.of<CategoryProvider>(context);

    return Container(
      alignment: Alignment.center,
      padding: const EdgeInsets.all(16.0),
      decoration: const BoxDecoration(
        color: Colors.white, // Color de fondo blanco
      ),
      child: categoryProvider.selectedCategoryId == null
          ? Text("No category has been selected.",
              style: Theme.of(context).textTheme.bodyLarge)
          : Column(
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                Text(
                  'Evaluación para la Categoría:',
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                Text(
                  'ID: ${categoryProvider.selectedCategoryId}', // Muestra el ID de la categoría
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                Text(
                  'Nombre: ${categoryProvider.categories.firstWhere((element) => element.id == categoryProvider.selectedCategoryId).name}',
                  style: Theme.of(context).textTheme.bodyMedium,
                ), // Muestra el nombre de la categoría
              ],
            ),
    );
  }
}
