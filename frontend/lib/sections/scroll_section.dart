import 'package:flutter/material.dart';
import 'package:frontend/models/text_recomendation.dart';
import 'package:frontend/services/text_recomendation_service.dart';

class TextRecomendationSection extends StatefulWidget {
  const TextRecomendationSection({super.key});

  @override
  TextRecomendationSectionState createState() => TextRecomendationSectionState();
}

class TextRecomendationSectionState extends State<TextRecomendationSection> {
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: FutureBuilder<List<TextRecomendation>>(
        future: _fetchTextRecomendations(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else {
            final categories = snapshot.data!;

            return ListView.builder(
              itemCount: categories.length,
              itemBuilder: (context, index) {
                final category = categories[index];
                return InkWell(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => TextRecommendationDetailPage(
                          title: category.data,
                          insideText: category.contextExplanation,
                        ),
                      ),
                    );
                  },
                  child: Container(
                    decoration: const BoxDecoration(
                      color: Color(0xFFFFEB3B), // Fondo amarillo
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        const SizedBox(height: 100),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 20.0),
                          child: Text(
                            category.data,
                            textAlign: TextAlign.center,
                            style: const TextStyle(
                              fontFamily: 'Roboto',
                              fontSize: 24.0,
                              fontWeight: FontWeight.bold,
                              color: Colors.black, // Color negro para el texto
                            ),
                          ),
                        ),
                        const SizedBox(height: 20),
                        Text(
                          '//${category.category}/${category.subCategory}', // Mostrar categoría y subcategoría
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontFamily: 'Roboto',
                            fontSize: 16.0,
                            color: Colors.black,
                          ),
                        ),
                        const SizedBox(height: 40),
                        const Icon(
                          Icons.abc_rounded,
                          size: 40,
                          color: Colors.black,
                        ),
                        const Text(
                          'DESLIZAR HACIA LA DERECHA\nVOLVER POR MÁS INFORMACIÓN',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontFamily: 'Roboto',
                            fontSize: 14.0,
                            color: Colors.black,
                          ),
                        ),
                        const SizedBox(height: 50),
                      ],
                    ),
                  ),
                );
              },
            );
          }
        },
      ),
    );
  }
}

class TextRecommendationDetailPage extends StatelessWidget {
  final String title;
  final String insideText;

  const TextRecommendationDetailPage({
    super.key,
    required this.title,
    required this.insideText,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        backgroundColor: const Color(0xFFFFEB3B), // Fondo amarillo en la barra
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Text(
            insideText,
            style: const TextStyle(
              fontSize: 18.0,
              fontFamily: 'Roboto',
              color: Colors.black, // Texto en color negro
            ),
          ),
        ),
      ),
    );
  }
}
