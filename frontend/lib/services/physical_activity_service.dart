import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frontend/models/physical_activity.dart';
import 'package:frontend/services/auth_services.dart';

class PhysicalActivityService {
  final String baseUrl = "http://127.0.0.1:8000/api/prevcad/health_categories";
  final AuthService _authService = AuthService();

  Future<PhysicalActivityDetail> getPhysicalActivityDetail() async {
    try {
      // Obtener el token de acceso, refrescando si es necesario
      final token = await _authService.getAccessToken();
      if (token == null) {
        throw Exception('No access token found');
      }

      // Realizar la solicitud con el token en el encabezado
      final response = await http.get(
        Uri.parse('$baseUrl/physical_activities/'),
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'Accept-Charset': 'utf-8',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return PhysicalActivityDetail.fromJson(
          json.decode(utf8.decode(response.bodyBytes))
        );
      } else if (response.statusCode == 401) {
        // Manejar un error 401 (no autorizado)
        await _authService.logout();
        throw Exception('Session expired. Please log in again.');
      } else {
        throw Exception('Failed to load physical activity details: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching physical activity details: $e');
    }
  }
}
