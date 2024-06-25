class Category {
  final String title;
  final String icon;

  Category({required this.title, required this.icon});

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      title: json['title'],
      icon: json['icon'],
    );
  }
}
