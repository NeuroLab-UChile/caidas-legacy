import 'dart:convert';
import 'dart:typed_data';

class Category {
  final int id;
  final String name;
  final Uint8List? icon;
  final String? description;
  final int rootNode;

  Category({
    required this.id,
    required this.name,
    this.icon,
    this.description,
    required this.rootNode,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'],
      name: json['name'] ?? '',
      icon: json['icon'] != null ? base64Decode(json['icon']) : null,
      description: json['description'],
      rootNode: json['root_node'],
    );
  }
}
