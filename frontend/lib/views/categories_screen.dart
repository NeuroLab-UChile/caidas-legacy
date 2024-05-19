import 'package:flutter/material.dart';
import '../widgets/categories_grid.dart'; // Asegúrate que la ruta es correcta

class CategoriesScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Categorías"),
      ),
      body: CategoriesGrid(),
    );
  }
}
