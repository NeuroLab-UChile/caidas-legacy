import 'package:flutter/material.dart';
import 'package:frontend/services/auth_services.dart';
import 'package:frontend/views/login_screen.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

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
    return FutureBuilder<String?>(
      future: _authService.getAccessToken(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Center(child: CircularProgressIndicator());
        } else if (snapshot.hasData) {
          return CategoriesList();
        } else {
          return LoginScreen();
        }
      },
    );
  }
}

class CategoriesList extends StatefulWidget {
  @override
  _CategoriesListState createState() => _CategoriesListState();
}

class _CategoriesListState extends State<CategoriesList> {
  final AuthService _authService = AuthService();

  Future<List<Category>> _fetchCategories() async {
    final accessToken = await _authService.getAccessToken();
    try {
      final response = await http.get(
        Uri.parse('http://127.0.0.1:8000/api/prevcad'),
        headers: {
          'Authorization': 'Bearer $accessToken',
        },
      );
      print('Request URL: ${response.request!.url}');
      print('Response status: ${response.statusCode}');
      print('Response body: ${response.body}');
      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        final categories = jsonResponse['categories'] as List;
        return categories
            .map((category) => Category.fromJson(category))
            .toList();
      } else {
        print(
            'Failed to load categories with status code: ${response.statusCode}');
        throw Exception('Failed to load categories');
      }
    } catch (e) {
      print('Connection failed with error: $e');
      throw Exception('Connection failed: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Categories'),
        actions: [
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: () async {
              await _authService.logout();
              Navigator.pushReplacementNamed(context, '/');
            },
          ),
        ],
      ),
      body: FutureBuilder<List<Category>>(
        future: _fetchCategories(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else {
            final categories = snapshot.data!;
            return ListView.builder(
              itemCount: categories.length,
              itemBuilder: (context, index) {
                final category = categories[index];
                return ListTile(
                  leading: Icon(Icons.category),
                  title: Text(category.title),
                );
              },
            );
          }
        },
      ),
    );
  }
}

class Category {
  final String title;
  final String icon;

  Category({required this.title, required this.icon});

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      title: json['title'],
      icon: json['icon'],
    );
  }
}
