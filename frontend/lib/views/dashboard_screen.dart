import 'package:flutter/material.dart';
import 'package:frontend/sections/categories_section.dart';
import 'package:frontend/views/login_screen.dart';
import 'package:frontend/services/auth_services.dart';
import 'package:frontend/sections/scroll_section.dart';

class DashboardScreen extends StatefulWidget {
  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class ScrollWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: TextRecomendationSection(),
    );
  }
}

class CategoriesWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: CategoriesSection(),
    );
  }
}

class EvaluateSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text('Evaluar Sección'),
    );
  }
}

class TrainSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text('Entrenar Sección'),
    );
  }
}

class MyDataSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text('Mis Datos Sección'),
    );
  }
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedIndex = 0;
  final AuthService _authService = AuthService();

  final List<Widget> _widgetOptions = <Widget>[
    ScrollWidget(),
    EvaluateSection(),
    TrainSection(),
    MyDataSection(),
    CategoriesWidget(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  Future<void> _logout() async {
    // Lógica de cierre de sesión
    await _authService.logout();

    // Navegar a la pantalla de inicio de sesión después del cierre de sesión
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (context) => LoginScreen(),
      ),
    );
  }

  void _onFabPressed() {
    setState(() {
      _selectedIndex = 4; // Cambia al índice de la nueva sección
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // Sección superior con fondo amarillo y círculo blanco
          Stack(
            clipBehavior:
                Clip.none, // Permite que el círculo sobresalga del contenedor
            children: [
              Container(
                height: 140.0,
                color: Colors.yellow, // Fondo amarillo
              ),
              Positioned(
                top:
                    100.0, // Ajusta la posición superior para reducir el espacio
                left: MediaQuery.of(context).size.width / 2 - 40,
                child: Container(
                  width: 100.0,
                  height: 100.0,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.2),
                        spreadRadius: 2,
                        blurRadius: 4,
                      ),
                    ],
                  ),
                ),
              ),
              // Botón de cierre de sesión en la esquina superior derecha
              Positioned(
                top: 40.0, // Ajusta según sea necesario
                right: 20.0, // Ajusta según sea necesario
                child: IconButton(
                  icon: Icon(Icons.logout, color: Colors.black),
                  onPressed: _logout,
                ),
              ),
            ],
          ),
          // Sección principal donde irán los widgets
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                  horizontal: 8.0), // Margen horizontal
              child: Material(
                elevation: 4.0,
                borderRadius: BorderRadius.circular(10.0),
                shadowColor: Colors.black.withOpacity(0.2),
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius:
                        BorderRadius.circular(10.0), // Bordes redondeados
                  ),
                  child: _widgetOptions.elementAt(_selectedIndex),
                ),
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex < 4 ? _selectedIndex : 0,
        onTap: _onItemTapped,
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.bookmark),
            label: 'Recordar',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.star),
            label: 'Evaluar',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.fitness_center),
            label: 'Entrenar',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Mis Datos',
          ),
        ],
        type: BottomNavigationBarType.fixed,
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _onFabPressed,
        child: Icon(Icons.home),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
    );
  }
}

void main() => runApp(MaterialApp(
      home: DashboardScreen(),
      routes: {
        '/login': (context) => LoginScreen(),
      },
    ));
