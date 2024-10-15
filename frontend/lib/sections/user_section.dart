import 'dart:convert'; // Para decodificar base64
import 'package:flutter/material.dart';
import 'package:frontend/services/user_service.dart';

class UserDataSection extends StatefulWidget {
  const UserDataSection({Key? key}) : super(key: key);

  @override
  _UserDataSectionState createState() => _UserDataSectionState();
}

class _UserDataSectionState extends State<UserDataSection> {
  final UserService _userService = UserService();
  String username = '';
  String email = '';
  String firstName = '';
  String lastName = '';

  Map<String, dynamic> profile = {};

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    try {
      // Llama al servicio de autenticación para obtener los datos del usuario
      final user = await _userService.fetchUserProfile();

      // Actualiza el estado para mostrar los datos en la UI
      setState(() {
        username = user.username;
        email = user.email;
        firstName = user.firstName;
        lastName = user.lastName;

        profile = user.profile;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al cargar los datos del usuario: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
        child: Column(
          children: [
            CircleAvatar(
              radius: 50,
              backgroundImage:
                  _getProfilePicture(), // Lógica para obtener la imagen de perfil
              backgroundColor: Colors.grey[200],
              child: profile['profile_picture'] == null ||
                      profile['profile_picture'] == ''
                  ? Icon(Icons.person,
                      size: 50,
                      color: Colors.grey[600]) // Icono si no hay imagen
                  : null,
            ),
            const SizedBox(height: 10),
            const Text(
              'EDITAR IMAGEN',
              style: TextStyle(
                fontSize: 16,
                color: Colors.black54,
                fontWeight: FontWeight.w400,
              ),
            ),
            const SizedBox(height: 30),
            _buildInfoField('Nombre de usuario', username),
            _buildInfoField('Correo electrónico', email),
            _buildInfoField('Nombre y Apellido', firstName + ' ' + lastName),
          ],
        ),
      ),
    );
  }

  // Lógica para obtener la imagen de perfil
  ImageProvider? _getProfilePicture() {
    if (profile['profile_picture'] != null &&
        profile['profile_picture'] != '') {
      String base64Image = profile['profile_picture'];

      // Verifica si la cadena tiene el prefijo de base64
      if (base64Image.startsWith('data:image')) {
        // Remover el prefijo antes de decodificar
        base64Image = base64Image.split(',').last;
      }

      try {
        return MemoryImage(
            base64Decode(base64Image)); // Decodifica y usa la imagen
      } catch (e) {
        print('Error al decodificar la imagen: $e');
        return null; // Si ocurre un error, retorna null
      }
    }
    return null; // Si no hay imagen, retorna null
  }

  Widget _buildInfoField(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.black,
          ),
        ),
        const SizedBox(height: 5),
        Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.normal,
            color: Colors.grey,
          ),
        ),
        const Divider(
          height: 30,
          thickness: 1,
          color: Colors.black26,
        ),
      ],
    );
  }
}
