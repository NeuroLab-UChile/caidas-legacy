
class FormModel {
  final int id;
  final int categoryId;
  final String title;
  final String description;
  final List<Question> questions;

  FormModel({
    required this.id,
    required this.categoryId,
    required this.title,
    required this.description,
    required this.questions,
  });

  factory FormModel.fromJson(Map<String, dynamic> json) {
    var questionsFromJson = json['questions'] as List;
    List<Question> questionsList =
        questionsFromJson.map((q) => Question.fromJson(q)).toList();

    return FormModel(
      id: json['id'] ?? 0,
      categoryId: json['category_id'] ?? 0, // Inicializar el ID de la categoría desde JSON
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      questions: questionsList,
    );
  }

  @override
  String toString() {
    return 'FormModel(id: $id, categoryId: $categoryId, title: $title, description: $description, questions: $questions)';
  }
}

class Question {
  final int id;
  final String questionText;
  final String questionType;
  final List<Option>? options; // Opciones para preguntas de selección múltiple

  Question({
    required this.id,
    required this.questionText,
    required this.questionType,
    this.options = const [],
  });

  factory Question.fromJson(Map<String, dynamic> json) {
    // Si 'options' está presente y no es null, lo convierte, de lo contrario usa una lista vacía
    var optionsFromJson = json['options'] as List?;
    List<Option>? optionsList;
    if (optionsFromJson != null) {
      optionsList = optionsFromJson.map((o) => Option.fromJson(o)).toList();
    }

    return Question(
      id: json['id'] ?? 0, // Asegurarse de tener un valor predeterminado
      questionText: json['question_text'] ?? '', // Manejar valores null
      questionType: json['question_type'] ?? '', // Manejar valores null
      options: optionsList, // Puede ser null si no hay opciones
    );
  }

  @override
  String toString() {
    return 'Question(id: $id, questionText: $questionText, questionType: $questionType, options: $options)';
  }
}

class Option {
  final int id;
  final String text;

  Option({
    required this.id,
    required this.text,
  });

  factory Option.fromJson(Map<String, dynamic> json) {
    return Option(
      id: json['id'] ?? 0, // Si es null, usa 0 como valor predeterminado
      text: json['text'] ?? '', // Si es null, usa cadena vacía
    );
  }

  @override
  String toString() {
    return 'Option(id: $id, text: $text)';
  }
}
