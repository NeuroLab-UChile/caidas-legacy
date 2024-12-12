import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frontend/services/auth_services.dart';
import '../models/category.dart';
import '../models/activity_node.dart';

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

      if (response.statusCode == 200) {
        final Map<String, dynamic> responseBody = jsonDecode(response.body);
        final List<dynamic> categoriesJson = responseBody['categories'] ?? [];

        return categoriesJson.map((json) => Category.fromJson(json)).toList();
      } else {
        _handleHttpError(response.statusCode);
        return [];
      }
    } catch (e) {
      print('Error in fetchCategories: $e');
      rethrow;
    }
  }

  // Mapea la respuesta de categorías
  List<Category> _parseCategories(Map<String, dynamic> responseBody) {
    if (!responseBody.containsKey('categories')) {
      throw Exception('Campo "categories" no encontrado en la respuesta.');
    }
    final List<dynamic> categoriesJson = responseBody['categories'];
    return categoriesJson.map((json) => Category.fromJson(json)).toList();
  }

  // Mapea la respuesta de nodos
  List<ActivityNode> _parseNodes(Map<String, dynamic> responseBody) {
    if (!responseBody.containsKey('nodes')) {
      throw Exception('Campo "nodes" no encontrado en la respuesta.');
    }
    final List<dynamic> nodesJson = responseBody['nodes'];
    return nodesJson.map((json) => ActivityNode.fromJson(json)).toList();
  }

  // Manejo de errores HTTP
  void _handleHttpError(int statusCode) {
    switch (statusCode) {
      case 400:
        throw Exception('Solicitud incorrecta (400).');
      case 401:
        throw Exception('No autorizado (401).');
      case 404:
        throw Exception('Recurso no encontrado (404).');
      case 500:
        throw Exception('Error interno del servidor (500).');
      default:
        throw Exception('Error desconocido: $statusCode');
    }
  }
}
