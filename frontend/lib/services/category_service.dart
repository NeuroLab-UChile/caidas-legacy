import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frontend/services/auth_services.dart';
import '../models/category.dart';
import '../models/form.dart';

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
    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = json.decode(utf8.decode(response.bodyBytes));
      return jsonResponse
          .map((category) => Category.fromJson(category))
          .toList();
    } else {
      throw Exception('Failed to load categories');
    }
  }

  Future<FormModel> fetchTestFormByCategoryId(int categoryId) async {
    final accessToken = await _authService.getAccessToken();
    final response = await http.get(
      Uri.parse('$_baseUrl$categoryId/test_form/'),
      headers: {
        'Authorization': 'Bearer $accessToken',
      },
    );

    if (response.statusCode == 200) {
      Map<String, dynamic> jsonResponse = json.decode(utf8.decode(response.bodyBytes));
      return FormModel.fromJson(jsonResponse);
    } else {
      throw Exception('No se encontró el formulario de test para esta categoría');
    }
  }

  Future<Map<String, dynamic>> fetchLastTestResults(int categoryId) async {
    final accessToken = await _authService.getAccessToken();
    final response = await http.get(
      Uri.parse('$_baseUrl$categoryId/last_test_results/'),
      headers: {
        'Authorization': 'Bearer $accessToken',
      },
    );
    
    print('Response status code: ${response.statusCode}');
    print('Response body: ${response.body}');

    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    } else {
      throw Exception('No se encontró ningún resultado para el último test.');
    }
  }
}
