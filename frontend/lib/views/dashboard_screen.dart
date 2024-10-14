import 'package:flutter/material.dart';
import 'package:frontend/models/user.dart';
import 'package:frontend/sections/categories_section.dart';
import 'package:frontend/sections/evaluation_section.dart';
import 'package:frontend/sections/train_section.dart';
import 'package:frontend/sections/user_section.dart';
import 'package:frontend/views/login_screen.dart';
import 'package:frontend/services/auth_services.dart';
import 'package:frontend/sections/scroll_section.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class ScrollWidget extends StatelessWidget {
  const ScrollWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: TextRecomendationSection(),
    );
  }
}

class CategoriesWidget extends StatelessWidget {
  const CategoriesWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: CategoriesSection(),
    );
  }
}

class EvaluateSection extends StatelessWidget {
  const EvaluateSection({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: EvaluatationSection(),
    );
  }
}

class TrainSection extends StatelessWidget {
  const TrainSection({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: TrainingSection(),
    );
  }
}

class MyDataSection extends StatelessWidget {
  const MyDataSection({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: UserDataSection(),
    );
  }
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedIndex = 0;
  bool _isHomeSelected = true; // Estado adicional para la casita

  List<Color> _iconColors = List.generate(5, (index) => Colors.grey);

  final AuthService _authService = AuthService();

  final List<Widget> _widgetOptions = <Widget>[
    const ScrollWidget(),
    const EvaluateSection(),
    const TrainSection(),
    const MyDataSection(),
    const CategoriesWidget(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
      _isHomeSelected = false;

      // Actualizar colores: blanco si está seleccionado, gris si no
      for (int i = 0; i < _iconColors.length; i++) {
        _iconColors[i] = i == index + 1 ? Colors.white : Colors.grey;
      }
    });
  }

  Future<void> _logout() async {
    await _authService.logout();
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (context) => const LoginScreen(),
      ),
    );
  }

  void _onFabPressed() {
    setState(() {
      _isHomeSelected = true;

      _iconColors =
          List.generate(5, (index) => index == 0 ? Colors.grey : Colors.grey);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          Stack(
            clipBehavior: Clip.none,
            children: [
              Container(
                height: 120.0,
                color: Colors.yellow,
              ),
              Positioned(
                top: 80.0,
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
              Positioned(
                top: 40.0,
                right: 20.0,
                child: IconButton(
                  icon: const Icon(Icons.logout, color: Colors.black),
                  onPressed: _logout,
                ),
              ),
            ],
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 20.0,
                vertical: 10.0,
              ),
              child: Material(
                elevation: 4.0,
                borderRadius: BorderRadius.circular(10.0),
                shadowColor: Colors.black.withOpacity(0.2),
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(10.0),
                  ),
                  child: _isHomeSelected
                      ? const CategoriesWidget() // Muestra la vista de la casita
                      : _widgetOptions.elementAt(
                          _selectedIndex), // Muestra la vista seleccionada del BottomNavigationBar
                ),
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        backgroundColor:
            Colors.black, // Cambia el fondo del BottomNavigationBar a negro
        selectedItemColor:
            Colors.white, // Iconos y texto seleccionados en blanco
        unselectedItemColor:
            Colors.grey, // Iconos y texto no seleccionados en gris
        selectedLabelStyle: const TextStyle(
          fontWeight: FontWeight.normal,
          fontSize: 12,
        ),
        unselectedLabelStyle: const TextStyle(
          fontWeight: FontWeight.normal,
          fontSize: 12,
        ),
        items: <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.bookmark, color: _iconColors[1]),
            label: 'Recordar',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.star, color: _iconColors[2]),
            label: 'Evaluar',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.fitness_center, color: _iconColors[3]),
            label: 'Entrenar',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person, color: _iconColors[4]),
            label: 'Mis Datos',
          ),
        ],
        type: BottomNavigationBarType.fixed,
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: _isHomeSelected
            ? Colors.white
            : Colors.black, // Cambia el color del FAB
        onPressed: _onFabPressed,
        child: Image.asset(
          _isHomeSelected
              ? 'assets/general/logo_dark.png' // Cambia el logo si _isHomeSelected es true
              : 'assets/general/logo.png', // Muestra otro logo si es false
          width: 24, // Ajusta el tamaño del PNG según sea necesario
          height: 24,
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
    );
  }
}

void main() => runApp(MaterialApp(
      home: const DashboardScreen(),
      routes: {
        '/login': (context) => const LoginScreen(),
      },
    ));
