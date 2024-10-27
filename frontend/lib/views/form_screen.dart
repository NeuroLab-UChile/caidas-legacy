import 'dart:convert';
import '../models/form.dart';
import '../models/category.dart'; // Importa la clase Category
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:frontend/services/auth_services.dart';
import 'package:frontend/views/category_detail_screen.dart'; // Importa CategoryDetailScreen

class FormScreen extends StatefulWidget {
  final FormModel form;
  final int categoryId;
  final Category category; // Agrega el parámetro de categoría

  const FormScreen({
    super.key, 
    required this.form, 
    required this.categoryId, 
    required this.category, // Asegúrate de recibir la categoría original aquí
  });

  @override
  FormScreenState createState() => FormScreenState();
}


class FormScreenState extends State<FormScreen> {
  Map<int, dynamic> selectedAnswers = {};

  Future<void> _submitAnswers() async {
    final url = "http://127.0.0.1:8000/api/prevcad/health_categories/${widget.categoryId}/test_form/";

    try {
      final responseData = selectedAnswers.entries
          .map((entry) => {'question_id': entry.key, 'answer': entry.value})
          .toList();

      final response = await http.post(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${await AuthService().getAccessToken()}',
        },
        body: jsonEncode({'responses': responseData}),
      );

      if (response.statusCode == 200) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Respuestas enviadas con éxito')),
          );
          // Regresar a la vista de detalle de la categoría usando la categoría original
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) => CategoryDetailScreen(
                category: widget.category, // Pasa la categoría original aquí
              ),
            ),
          );
        }
      } else {
        throw Exception('Error al enviar las respuestas');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  // Construcción de la UI
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.form.title)),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: widget.form.questions.length,
              itemBuilder: (context, index) {
                final question = widget.form.questions[index];
                if (question.questionType == 'text') {
                  return ListTile(
                    title: Text(question.questionText),
                    subtitle: TextField(
                      onChanged: (value) {
                        setState(() {
                          selectedAnswers[question.id] = value;
                        });
                      },
                    ),
                  );
                } else if (question.questionType == 'multiple_choice') {
                  return ListTile(
                    title: Text(question.questionText),
                    subtitle: Column(
                      children: question.options!
                          .map((option) => RadioListTile(
                                title: Text(option.text),
                                value: option.id,
                                groupValue: selectedAnswers[question.id],
                                onChanged: (value) {
                                  setState(() {
                                    selectedAnswers[question.id] = value;
                                  });
                                },
                              ))
                          .toList(),
                    ),
                  );
                }
                return const SizedBox.shrink();
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: ElevatedButton(
              onPressed: _submitAnswers,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.yellow,
                foregroundColor: Colors.black,
              ),
              child: const Text('Enviar'),
            ),
          ),
        ],
      ),
    );
  }
}
