import 'package:flutter/material.dart';
import 'package:frontend/models/text_recomendation.dart';
import 'package:frontend/services/text_recomendation_service.dart';

class TextRecomendationSection extends StatefulWidget {
  @override
  _TextRecomendationSectionState createState() =>
      _TextRecomendationSectionState();
}

class _TextRecomendationSectionState extends State<TextRecomendationSection> {
  final TextRecommendationService _textRecomendationService =
      TextRecommendationService();

  Future<List<TextRecomendation>> _fetchTextRecomendations() async {
    try {
      final categories =
          await _textRecomendationService.fetchTextRecommendations();
      return categories;
    } catch (e) {
      print('Connection failed with error: $e');
      throw Exception('Connection failed: $e');
    }
  }

  // Función para mapear el nombre del icono a IconData

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Selecciona una categoría'),
      ),
      body: FutureBuilder<List<TextRecomendation>>(
        future: _fetchTextRecomendations(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else {
            final categories = snapshot.data!;
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 10.0),
              child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  crossAxisSpacing: 10.0,
                  mainAxisSpacing: 10.0,
                ),
                itemCount: categories.length,
                itemBuilder: (context, index) {
                  final category = categories[index];
                  return Card(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const SizedBox(height: 20),
                        Text(category.title, textAlign: TextAlign.center),
                      ],
                    ),
                  );
                },
              ),
            );
          }
        },
      ),
    );
  }
}
