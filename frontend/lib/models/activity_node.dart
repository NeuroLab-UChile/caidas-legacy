class ActivityNode {
  final int id;
  final String description;
  final String type; // Agregar un tipo para determinar la vista

  ActivityNode(
      {required this.id, required this.description, required this.type});

  factory ActivityNode.fromJson(Map<String, dynamic> json) {
    return ActivityNode(
      id: json['id'],
      description: json['description'],
      type: json['type'],
    );
  }
}
