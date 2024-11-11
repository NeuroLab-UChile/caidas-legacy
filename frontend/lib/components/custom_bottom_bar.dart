import 'package:flutter/material.dart';

class CustomBottomBar extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;
  final List<Color> iconColors;

  const CustomBottomBar({
    Key? key,
    required this.currentIndex,
    required this.onTap,
    required this.iconColors,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: currentIndex,
      onTap: onTap,
      backgroundColor: Colors.black,
      selectedItemColor: Colors.white,
      unselectedItemColor: Colors.grey,
      selectedLabelStyle: const TextStyle(
        fontWeight: FontWeight.normal,
        color: Colors.white,
        fontSize: 12,
      ),
      unselectedLabelStyle: const TextStyle(
        fontWeight: FontWeight.normal,
        color: Colors.grey,
        fontSize: 12,
      ),
      items: <BottomNavigationBarItem>[
        BottomNavigationBarItem(
          icon: Icon(Icons.bookmark, color: iconColors[1]),
          label: 'Recordar',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.star, color: iconColors[2]),
          label: 'Evaluar',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.fitness_center, color: iconColors[3]),
          label: 'Entrenar',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.person, color: iconColors[4]),
          label: 'Mis Datos',
        ),
      ],
      type: BottomNavigationBarType.fixed,
    );
  }
}
