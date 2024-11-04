import 'dart:convert';
import 'dart:typed_data';

class Category {
  final int id;
  final String name;
  final Uint8List? image;

  Category({
    required this.id,
    required this.name,
    this.image,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'],
      name: json['name'] ?? '',
      image: json['image'] != null ? base64Decode(json['image']) : null,

    );
  }
}
