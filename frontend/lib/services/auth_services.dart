import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  final _storage = FlutterSecureStorage();

  Future<void> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('http://127.0.0.1:8000/api/token/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'username': username,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      await _storage.write(key: 'access_token', value: data['access']);
      await _storage.write(key: 'refresh_token', value: data['refresh']);
    } else {
      throw Exception('Failed to login');
    }
  }

  Future<void> logout() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }

  Future<void> refreshToken() async {
    final refreshToken = await _storage.read(key: 'refresh_token');
    final response = await http.post(
      Uri.parse('http://127.0.0.1:8000/api/token/refresh/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'refresh': refreshToken,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      await _storage.write(key: 'access_token', value: data['access']);
    } else {
      throw Exception('Failed to refresh token');
    }
  }

  Future<String?> getAccessToken() async {
    return await _storage.read(key: 'access_token');
  }

  Future<bool> isLoggedIn() async {
    final token = await getAccessToken();
    if (token == null) {
      return false;
    }

    final response = await http.get(
      Uri.parse('http://127.0.0.1:8000/api/prevcad'), // Cambia a un endpoint protegido real
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    return response.statusCode == 200;
  }
}
