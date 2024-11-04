import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  final _storage = const FlutterSecureStorage();

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
      // Si falla el refresco, considera cerrar sesión automáticamente
      await logout();
      throw Exception('Failed to refresh token');
    }
  }

  Future<String?> getAccessToken() async {
    String? accessToken = await _storage.read(key: 'access_token');

    if (accessToken != null && _isTokenExpired(accessToken)) {
      await refreshToken();
      accessToken = await _storage.read(key: 'access_token');
    }

    return accessToken;
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

  // Decodifica y verifica si el token ha expirado
  bool _isTokenExpired(String token) {
    final parts = token.split('.');
    if (parts.length != 3) return true;

    final payload = json.decode(utf8.decode(base64Url.decode(base64Url.normalize(parts[1]))));
    final exp = payload['exp'] as int?;
    if (exp == null) return true;

    final expiration = DateTime.fromMillisecondsSinceEpoch(exp * 1000);
    return DateTime.now().isAfter(expiration);
  }
}
