import 'package:flutter/material.dart';
import 'package:frontend/models/text_recomendation.dart';
import 'package:frontend/services/text_recomendation_service.dart';

class TextRecomendationSection extends StatefulWidget {
  const TextRecomendationSection({super.key});

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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        title: const Text('Recomendaciones de Texto'),
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
                          title: category.title,
                          insideText: category.insideText,
                        ),
                      ),
                    );
                  },
                  child: Card(
                    elevation: 5,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const SizedBox(height: 20),
                        Text(
                          category.title,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontFamily: 'Roboto',
                            fontSize: 16.0,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
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

  const TextRecommendationDetailPage({super.key, 
    required this.title,
    required this.insideText,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Text(
            insideText,
            style: const TextStyle(fontSize: 18.0, fontFamily: 'Roboto'),
          ),
        ),
      ),
    );
  }
}
