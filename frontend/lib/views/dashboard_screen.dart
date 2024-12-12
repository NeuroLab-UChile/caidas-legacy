import 'package:flutter/material.dart';
import 'package:frontend/sections/categories_section.dart';
import 'package:frontend/sections/evaluation_section.dart';
import 'package:frontend/sections/train_section.dart';
import 'package:frontend/sections/user_section.dart';
import 'package:frontend/views/login_screen.dart';
import 'package:frontend/services/auth_services.dart';
import 'package:frontend/sections/scroll_section.dart';
import 'package:frontend/components/custom_bottom_bar.dart';
import 'package:frontend/providers/category_provider.dart';
import 'package:provider/provider.dart';
import 'package:frontend/providers/category_provider.dart';
import 'package:provider/provider.dart';

void main() => runApp(MaterialApp(
      home: const DashboardScreen(),
      routes: {
        '/login': (context) => const LoginScreen(),
      },
    ));

// Dashboard Screen
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedIndex = 0;
  bool _isHomeSelected = true;

  final List<Color> _iconColors = List.generate(5, (_) => Colors.grey);
  final AuthService _authService = AuthService();

  final List<Widget> _widgetOptions = [
    const DashboardChild(child: TextRecomendationSection()),
    const DashboardChild(child: EvaluationSection()),
    const DashboardChild(child: TrainingSection()),
    const DashboardChild(child: UserDataSection()),
    const DashboardChild(child: CategoriesSection())
  ];

@override
void initState() {
  super.initState();
  // Schedule the fetch after the widget is built
  WidgetsBinding.instance.addPostFrameCallback((_) {
    Provider.of<CategoryProvider>(context, listen: false).fetchCategories();
  });
}

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
      _isHomeSelected = false;
      _updateIconColors(index);
    });
  }

  void _updateIconColors(int activeIndex) {
    for (int i = 0; i < _iconColors.length; i++) {
      _iconColors[i] = i == activeIndex ? Colors.white : Colors.grey;
    }
  }

  Future<void> _logout() async {
    await _authService.logout();
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (context) => const LoginScreen()),
    );
  }

  void _onFabPressed() {
    setState(() {
      _isHomeSelected = true;
      _iconColors.fillRange(0, _iconColors.length, Colors.grey);
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
              _buildTopBar(context),
              Positioned(
                top: 45.0,
                left: MediaQuery.of(context).size.width / 2 - 40,
                child: _buildCenterCircle(context),
              ),
            ],
          ),
          Expanded(
            child: Material(
              elevation: 4.0,
              borderRadius: BorderRadius.circular(10.0),
              shadowColor: Colors.black.withOpacity(0.2),
              child: _isHomeSelected
                  ? const DashboardChild(child: CategoriesSection())
                  : _widgetOptions.elementAt(_selectedIndex),
            ),
          ),
        ],
      ),
      bottomNavigationBar: CustomBottomBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        iconColors: _iconColors,
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: _isHomeSelected ? Colors.white : Colors.black,
        onPressed: _onFabPressed,
        child: Image.asset(
          _isHomeSelected
              ? 'assets/general/logo_dark.png'
              : 'assets/general/logo.png',
          width: 24,
          height: 24,
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
    );
  }

  Widget _buildTopBar(BuildContext context) {
    return Container(
      height: 90.0,
      color: Theme.of(context).colorScheme.primary,
      child: Align(
        alignment: Alignment.topRight,
        child: IconButton(
          icon: const Icon(Icons.logout, color: Colors.black),
          onPressed: _logout,
        ),
      ),
    );
  }

  Widget _buildCenterCircle(BuildContext context) {
    return Container(
      width: 100.0,
      height: 100.0,
      decoration: BoxDecoration(
        color: _selectedIndex == 0 && !_isHomeSelected
            ? Theme.of(context).colorScheme.primary
            : Colors.white,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: _selectedIndex == 0 && !_isHomeSelected
                ? Theme.of(context).colorScheme.primary
                : Colors.black.withOpacity(0.1),
            spreadRadius: 2,
            blurRadius: 4,
          ),
        ],
      ),
    );
  }
}

class DashboardChild extends StatelessWidget {
  final Widget child;

  const DashboardChild({Key? key, required this.child}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return child;
  }
}
