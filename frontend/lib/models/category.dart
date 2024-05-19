import 'package:flutter/material.dart';

class Category {
  final String title;
  final IconData icon;

  Category(this.title, this.icon);

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      json['title'],
      IconData(json['icon'], fontFamily: 'MaterialIcons'),
    );
  }
}
