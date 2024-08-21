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
    final response = await http.get(
      Uri.parse(_baseUrl),
      headers: {
        'Authorization': 'Bearer $accessToken',
      },
    );
    print('Response status: ${response.statusCode}');
    print('Response body: ${response.body}');
    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = json.decode(utf8.decode(response.bodyBytes));
      print('Parsed JSON: $jsonResponse');
      return jsonResponse
          .map((category) => Category.fromJson(category))
          .toList();
    } else {
      throw Exception('Failed to load categories');
    }
  }
}
