import 'package:flutter/material.dart';
import 'package:frontend/providers/category_provider.dart';
import 'package:frontend/services/auth_services.dart';
import 'package:frontend/views/dashboard_screen.dart';
import 'package:frontend/views/login_screen.dart';
import 'package:provider/provider.dart';
import 'theme/app_theme.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => CategoryProvider(),
      child: MaterialApp(
        routes: {
          '/': (context) => AuthCheck(),
          '/dashboard': (context) => const DashboardScreen(),
        },
        initialRoute: '/',
        theme: AppTheme.lightTheme,
      ),
    );
  }
}

class AuthCheck extends StatelessWidget {
  final AuthService _authService = AuthService();

  AuthCheck({super.key});

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
      future: _authService.isLoggedIn(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        } else if (snapshot.hasData && snapshot.data == true) {
          return const DashboardScreen();
        } else {
          return const LoginScreen();
        }
      },
    );
  }
}
