import 'dart:convert';
import '../models/form.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:frontend/services/auth_services.dart';

class FormScreen extends StatefulWidget {
  final FormModel form;
  final int categoryId; // Nuevo parámetro para el ID de la categoría

  const FormScreen({super.key, required this.form, required this.categoryId});

  @override
  FormScreenState createState() => FormScreenState();
}


class FormScreenState extends State<FormScreen> {
  // Almacena las respuestas seleccionadas por el usuario
  Map<int, dynamic> selectedAnswers = {};

  // Método para enviar las respuestas al backend
  Future<void> _submitAnswers() async {
    final url = "http://127.0.0.1:8000/api/prevcad/health_categories/${widget.categoryId}/test_form/";

    try {
      // Estructura de datos para enviar al backend
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
                          selectedAnswers[question.id] = value; // Guarda la respuesta de texto
                        });
                      },
                    ),
                  );
                } else if (question.questionType == 'multiple_choice') {
                  return ListTile(
                    title: Text(question.questionText),
                    subtitle: Column(
                      children: question.options!
                          .map(
                            (option) => RadioListTile(
                              title: Text(option.text),
                              value: option.id,
                              groupValue: selectedAnswers[question.id],
                              onChanged: (value) {
                                setState(() {
                                  selectedAnswers[question.id] = value; // Guarda la opción seleccionada
                                });
                              },
                            ),
                          )
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
              onPressed: _submitAnswers, // Llama a la función para enviar respuestas
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.yellow, // Fondo del botón
                foregroundColor: Colors.black, // Texto del botón
              ),
              child: const Text('Enviar'),
            ),
          ),
        ],
      ),
    );
  }
}
