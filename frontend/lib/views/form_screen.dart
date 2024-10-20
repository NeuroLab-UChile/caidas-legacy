import 'package:flutter/material.dart';
import '../models/form.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class FormScreen extends StatefulWidget {
  final FormModel form;

  const FormScreen({super.key, required this.form});

  @override
  _FormScreenState createState() => _FormScreenState();
}

class _FormScreenState extends State<FormScreen> {
  // Almacena las respuestas seleccionadas por el usuario
  Map<int, dynamic> selectedAnswers = {};

  // Método para enviar las respuestas al backend
  Future<void> _submitAnswers() async {
    final url = "http://127.0.0.1:8000/api/prevcad/health_categories/submit_answers/";
    try {
      // Estructura de datos para enviar al backend
      final responseData = selectedAnswers.entries
          .map((entry) => {'question_id': entry.key, 'answer': entry.value})
          .toList();

      final response = await http.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(responseData),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Respuestas enviadas con éxito')),
        );
      } else {
        throw Exception('Error al enviar las respuestas');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
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
              child: const Text('ENVIAR'),
            ),
          ),
        ],
      ),
    );
  }
}
