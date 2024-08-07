class TextRecomendation {
  final int id;
  final String title;
  final String insideText;

  TextRecomendation(
      {required this.id, required this.title, required this.insideText});

  factory TextRecomendation.fromJson(Map<String, dynamic> json) {
    return TextRecomendation(
      id: json['id'],
      title: json['title'],
      insideText: json['inside_text'],
    );
  }
}
