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

    // Asegúrate de que el provider esté inicializado y tenga datos
    if (categoryProvider.selectedCategoryId == null) {
      return const Center(child: Text("No category has been selected."));
    }

    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          const Text('Evaluación para la Categoría:'),
          Text(
              'ID: ${categoryProvider.selectedCategoryId}'), // Muestra el ID de la categoría
          Text(
              'Nombre: ${categoryProvider.categories.firstWhere((element) => element.id == categoryProvider.selectedCategoryId).name}'), // Muestra el nombre de la categoría
        ],
      ),
    );
  }
}
