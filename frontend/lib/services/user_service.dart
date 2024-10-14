import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frontend/services/auth_services.dart';
import '../models/user.dart';

class UserService {
  static const String _baseUrl =
      "http://127.0.0.1:8000/api/prevcad/user/profile/";
  final AuthService _authService = AuthService();

  Future<User> fetchUserProfile() async {
    final accessToken =
        await _authService.getAccessToken(); // Obtener el token de acceso
    final response = await http.get(
      Uri.parse(_baseUrl),
      headers: {
        'Authorization': 'Bearer $accessToken',
      },
    );

    print('Response status: ${response.statusCode}');
    print('Response body: ${response.body}');

    if (response.statusCode == 200) {
      Map<String, dynamic> jsonResponse =
          json.decode(utf8.decode(response.bodyBytes));
      print('Parsed JSON: $jsonResponse');
      return User.fromJson(jsonResponse); // Convertir el JSON al modelo User
    } else {
      throw Exception('Failed to load user profile');
    }
  }
}
