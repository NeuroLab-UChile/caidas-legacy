import 'package:flutter/material.dart';
import 'package:frontend/services/category_service.dart';

class TestResultsScreen extends StatefulWidget {
  final int categoryId;

  const TestResultsScreen({super.key, required this.categoryId});

  @override
  TestResultsScreenState createState() => TestResultsScreenState();
}

class TestResultsScreenState extends State<TestResultsScreen> {
  Map<String, dynamic>? lastTestResults;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadLastTestResults();
  }

  Future<void> _loadLastTestResults() async {
    try {
      final categoryService = CategoryService();
      final results = await categoryService.fetchLastTestResults(widget.categoryId);
      setState(() {
        lastTestResults = results;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al cargar los resultados: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Resultados último test")),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : lastTestResults == null
              ? const Center(child: Text("No hay resultados previos."))
              : ListView.builder(
                  itemCount: lastTestResults!['responses'].length,
                  itemBuilder: (context, index) {
                    final response = lastTestResults!['responses'][index];
                    return ListTile(
                      title: Text(response['question']),
                      subtitle: Text("Respuesta: ${response['answer']}"),
                    );
                  },
                ),
    );
  }
}
