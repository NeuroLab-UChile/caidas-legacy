import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frontend/services/auth_services.dart';
import '../models/category.dart';

class CategoryService {
  static const String _baseUrl =
      "http://127.0.0.1:8000/api/prevcad/health_categories/";
  final AuthService _authService = AuthService();

  Future<List<Category>> fetchCategories() async {
    final accessToken = await _authService.getAccessToken();
    try {
      final response = await http.get(
        Uri.parse(_baseUrl),
        headers: {
          'Authorization': 'Bearer $accessToken',
        },
      );
      print(response.body);

      if (response.statusCode == 200) {
        try {
          List<dynamic> jsonResponse =
              json.decode(utf8.decode(response.bodyBytes));
          return jsonResponse.map((category) {
            try {
              return Category.fromJson(category);
            } catch (e) {
              print("Error parsing category: $category");
              print("Parse error: $e");
              rethrow;
            }
          }).toList();
        } catch (e) {
          print("JSON decode error: $e");
          throw Exception('Failed to parse categories response: $e');
        }
      } else {
        throw Exception(
            'Failed to load categories: Status ${response.statusCode}');
      }
    } catch (e) {
      print("Network or parsing error: $e");
      throw Exception('Failed to fetch categories: $e');
    }
  }
}
