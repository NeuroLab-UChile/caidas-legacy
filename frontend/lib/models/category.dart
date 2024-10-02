import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';

class Category {
  final int id;
  final String name;
  final Uint8List image; // Aquí guardaremos la imagen como bytes
  final String description;
  final String createdAt;
  final String updatedAt;

  final Uint8List icon; // Aquí guardaremos la imagen como bytes

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
        image: base64Decode(json['image']),
        description: json['description'],
        createdAt: json['created_at'],
        updatedAt: json['updated_at'],
        icon: base64Decode(json['icon']));
  }
}
