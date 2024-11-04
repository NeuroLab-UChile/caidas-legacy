class PhysicalActivityDetail {
  final String name;
  final String description;
  final String description2;

  const PhysicalActivityDetail({
    required this.name,
    required this.description,
    required this.description2,
  });

  factory PhysicalActivityDetail.fromJson(Map<String, dynamic> json) {
    return PhysicalActivityDetail(
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      description2: json['description_2'] ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'description': description,
    'description_2': description2,
  };
}
