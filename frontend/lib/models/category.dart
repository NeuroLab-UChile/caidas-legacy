import 'dart:convert';
import 'dart:typed_data';

class Category {
  final int id;
  final String name;
  final Uint8List? icon;

  Category({
    required this.id,
    required this.name,
    this.icon,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'],
      name: json['name'] ?? '',
      icon: json['icon'] != null ? base64Decode(json['icon']) : null,
    );
  }
}
