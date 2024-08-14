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

class RememberSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text('Recordar Sección'),
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
    CategoriesWidget(),
    RememberSection(),
    EvaluateSection(),
    TrainSection(),
    MyDataSection(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: PreferredSize(
        preferredSize:
            Size.fromHeight(150.0), // Ajusta la altura según sea necesario
        child: Stack(
          children: [
            Container(
              color: Colors.yellow, // Fondo amarillo
              height: 150.0, // Altura del fondo amarillo
            ),
            Align(
              alignment: Alignment.bottomCenter,
              child: ClipPath(
                clipper:
                    InvertedCircleClipper(), // Clipper personalizado para el círculo invertido
                child: Container(
                  color: Colors.white, // Color del círculo
                  height: 75.0, // Altura del círculo
                  width: MediaQuery.of(context).size.width, // Ancho del círculo
                ),
              ),
            ),
          ],
        ),
      ),
      body: Center(
        child: _widgetOptions.elementAt(_selectedIndex),
      ),
      bottomNavigationBar: BottomAppBar(
        shape: CircularNotchedRectangle(),
        notchMargin: 6.0,
        child: Container(
          height: 60.0,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: <Widget>[
              IconButton(
                icon: Icon(Icons.calendar_today),
                onPressed: () {
                  _onItemTapped(0);
                },
              ),
              IconButton(
                icon: Icon(Icons.check),
                onPressed: () {
                  _onItemTapped(1);
                },
              ),
              SizedBox(width: 40), // Espacio para el FAB
              IconButton(
                icon: Icon(Icons.fitness_center),
                onPressed: () {
                  _onItemTapped(2);
                },
              ),
              IconButton(
                icon: Icon(Icons.person),
                onPressed: () {
                  _onItemTapped(3);
                },
              ),
            ],
          ),
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          _onItemTapped(4);
        },
        child: Icon(Icons.home),
      ),
    );
  }
}

void main() => runApp(MaterialApp(
      home: DashboardScreen(),
      routes: {
        '/login': (context) => LoginScreen(),
      },
    ));

// Clipper personalizado para crear el círculo invertido
class InvertedCircleClipper extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    var path = Path();
    double radius = 50.0; // Radio del círculo invertido

    path.lineTo(0, size.height - radius);
    path.arcToPoint(
      Offset(size.width, size.height - radius),
      radius: Radius.circular(radius),
      clockwise: false,
    );
    path.lineTo(size.width, 0);
    path.close();

    return path;
  }

  @override
  bool shouldReclip(CustomClipper<Path> oldClipper) => false;
}
