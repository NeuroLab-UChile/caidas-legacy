import 'dart:convert';
import 'dart:typed_data';
import 'activity_node.dart';

class Category {
  final int id;
  final String name;
  final String? icon;
  final ActivityNode rootNode;
  final EvaluationForm? evaluationForm;

  Category({
    required this.id,
    required this.name,
    this.icon,
    required this.rootNode,
    this.evaluationForm,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'] as int,
      name: json['name'] as String,
      icon: json['icon'] as String?,
      rootNode: ActivityNode.fromJson(json['root_node'] as Map<String, dynamic>),
      evaluationForm: json['evaluation_form'] != null
          ? EvaluationForm.fromJson(json['evaluation_form'] as Map<String, dynamic>)
          : null,
    );
  }
}

class EvaluationForm {
  final int id;
  final List<QuestionNode> questionNodes;
  final DateTime? completionDate;
  final int? score;
  final List<String>? recommendations;

  EvaluationForm({
    required this.id,
    required this.questionNodes,
    this.completionDate,
    this.score,
    this.recommendations,
  });

  factory EvaluationForm.fromJson(Map<String, dynamic> json) {
    return EvaluationForm(
      id: json['id'] as int,
      questionNodes: (json['question_nodes'] as List)
          .map((node) => QuestionNode.fromJson(node))
          .toList(),
      completionDate: json['completion_date'] != null
          ? DateTime.parse(json['completion_date'])
          : null,
      score: json['score'] as int?,
      recommendations: (json['recommendations'] as List?)
          ?.map((r) => r as String)
          .toList(),
    );
  }
}

class QuestionNode {
  final int id;
  final String type;
  final String question;
  final List<String>? options;
  final String? answer;
  final int? minValue;
  final int? maxValue;

  QuestionNode({
    required this.id,
    required this.type,
    required this.question,
    this.options,
    this.answer,
    this.minValue,
    this.maxValue,
  });

  factory QuestionNode.fromJson(Map<String, dynamic> json) {
    return QuestionNode(
      id: json['id'] as int,
      type: json['type'] as String,
      question: json['question'] as String,
      options: (json['options'] as List?)?.map((o) => o as String).toList(),
      answer: json['answer'] as String?,
      minValue: json['min_value'] as int?,
      maxValue: json['max_value'] as int?,
    );
  }
}
