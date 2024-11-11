import 'package:flutter/material.dart';
import 'package:frontend/models/text_recomendation.dart';
import 'package:frontend/services/text_recomendation_service.dart';

class TextRecomendationSection extends StatefulWidget {
  const TextRecomendationSection({super.key});

  @override
  TextRecomendationSectionState createState() =>
      TextRecomendationSectionState();
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
      backgroundColor: Theme.of(context).colorScheme.primary, // Fondo general
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
                return Column(
                  children: [
                    InkWell(
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
                        color: Theme.of(context)
                            .colorScheme
                            .primary, // Fondo de cada tarjeta
                        padding: const EdgeInsets.symmetric(vertical: 20.0),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            Padding(
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 20.0),
                              child: Text(
                                category.data,
                                textAlign: TextAlign.center,
                                style: Theme.of(context)
                                    .textTheme
                                    .displayLarge
                                    ?.copyWith(
                                      color: Theme.of(context)
                                          .colorScheme
                                          .onPrimary,
                                    ),
                              ),
                            ),
                            const SizedBox(height: 20),
                            Text(
                              '//${category.category}/${category.subCategory}', // Mostrar categoría y subcategoría
                              textAlign: TextAlign.center,
                              style: Theme.of(context)
                                  .textTheme
                                  .bodyMedium
                                  ?.copyWith(
                                    color:
                                        Theme.of(context).colorScheme.onPrimary,
                                  ),
                            ),
                            const SizedBox(height: 40),
                            const Icon(
                              Icons.abc_rounded,
                              size: 40,
                              color: Colors.black,
                            ),
                            Text(
                              'DESLIZAR HACIA LA DERECHA\nVOLVER POR MÁS INFORMACIÓN',
                              textAlign: TextAlign.center,
                              style: Theme.of(context)
                                  .textTheme
                                  .bodyMedium
                                  ?.copyWith(
                                    color: Colors.black,
                                  ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    // Añade un Divider solo si no es el último elemento
                    if (index < categories.length - 1)
                      Divider(
                        thickness: 1,
                        color: Colors.grey
                            .withOpacity(0.5), // Color sutil de la línea
                        indent: 20,
                        endIndent: 20,
                      ),
                  ],
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
        backgroundColor: Theme.of(context).colorScheme.primary,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Text(
            insideText,
            style: const TextStyle(
              fontSize: 18.0,
              fontFamily: 'Roboto',
              color: Colors.black,
            ),
          ),
        ),
      ),
    );
  }
}
