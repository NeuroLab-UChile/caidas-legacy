class TextRecomendation {
  final int id;
  final String theme;
  final String category;
  final String subCategory;
  final String learn;
  final String remember;
  final String data;
  final String practicData;
  final String contextExplanation;
  final String quoteLink;
  final String keywords;

  // Constructor
  TextRecomendation({
    required this.id,
    required this.theme,
    required this.category,
    required this.subCategory,
    required this.learn,
    required this.remember,
    required this.data,
    required this.practicData,
    required this.contextExplanation,
    required this.quoteLink,
    required this.keywords,
  });

  // Factory method para crear una instancia desde JSON
  factory TextRecomendation.fromJson(Map<String, dynamic> json) {
    return TextRecomendation(
      id: json['id'] ?? 0, // Valor por defecto 0 si es null
      theme: json['theme'] ?? 'Sin tema', // Valor por defecto 'Sin tema'
      category: json['category'] ??
          'Sin categoría', // Valor por defecto 'Sin categoría'
      subCategory: json['sub_category'] ??
          'Sin subcategoría', // Valor por defecto 'Sin subcategoría'
      learn: json['learn'] ??
          'Sin información', // Valor por defecto 'Sin información'
      remember: json['remember'] ??
          'Sin recordatorio', // Valor por defecto 'Sin recordatorio'
      data: json['data'] ?? 'Sin dato', // Valor por defecto 'Sin dato'
      practicData: json['practic_data'] ??
          'Sin dato práctico', // Valor por defecto 'Sin dato práctico'
      contextExplanation: json['context_explanation'] ??
          'Sin contexto', // Valor por defecto 'Sin contexto'
      quoteLink: json['quote_link'] ?? '', // Valor por defecto vacío
      keywords: json['keywords'] ?? '', // Valor por defecto vacío
    );
  }

  // Método para convertir la instancia en un Map (JSON)
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'theme': theme,
      'category': category,
      'sub_category': subCategory,
      'learn': learn,
      'remember': remember,
      'data': data,
      'practic_data': practicData,
      'context_explanation': contextExplanation,
      'quote_link': quoteLink,
      'keywords': keywords,
    };
  }
}
