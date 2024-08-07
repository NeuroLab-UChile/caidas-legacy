class Category {
  final int id;
  final String name;
  final String image;
  final String description;
  final String createdAt;
  final String updatedAt;
  final String icon;

  Category({
    required this.id,
    required this.name,
    required this.image,
    required this.description,
    required this.createdAt,
    required this.updatedAt,
    required this.icon,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'],
      name: json['name'],
      image: json['image'],
      description: json['description'],
      createdAt: json['created_at'],
      updatedAt: json['updated_at'],
      icon: json['icon'],
    );
  }
}
