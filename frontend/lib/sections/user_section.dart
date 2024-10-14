import 'package:flutter/material.dart';
import 'package:frontend/services/auth_services.dart';
import 'package:frontend/services/user_service.dart';

class UserDataSection extends StatefulWidget {
  const UserDataSection({Key? key}) : super(key: key);

  @override
  _UserDataSectionState createState() => _UserDataSectionState();
}

class _UserDataSectionState extends State<UserDataSection> {
  final UserService _userService = UserService();
  String username = '';
  String imageUrl = 'https://via.placeholder.com/150';

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    try {
      // Llama al servicio de autenticación para obtener los datos del usuario
      final user = await _userService.fetchUserProfile();
      // Mostrar los datos del usuario en un SnackBar
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('User data: ${user.toString()}')),
      );

      // Actualiza el estado para mostrar los datos en la UI
      setState(() {
        username = user.username;
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
              backgroundImage: NetworkImage(imageUrl),
              backgroundColor: Colors.grey[200],
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
          ],
        ),
      ),
    );
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
