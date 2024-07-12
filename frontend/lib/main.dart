import 'package:flutter/material.dart';
import 'package:frontend/services/auth_services.dart';
import 'package:frontend/views/login_screen.dart';
import 'package:frontend/views/categories_list.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      routes: {
        '/': (context) => AuthCheck(),
        '/categories': (context) => CategoriesList(),
      },
      initialRoute: '/',
    );
  }
}

class AuthCheck extends StatelessWidget {
  final AuthService _authService = AuthService();

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
      future: _authService.isLoggedIn(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        } else if (snapshot.hasData && snapshot.data == true) {
          return CategoriesList();
        } else {
          return LoginScreen();
        }
      },
    );
  }
}
