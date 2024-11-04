import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static ThemeData get lightTheme {
    // Definir colores principales
    const Color primaryColor =
        Color.fromARGB(255, 242, 255, 42); // Amarillo brillante
    const Color backgroundColor = Colors.white;
    const Color cardColor = Colors.white;
    const Color accentColor = Colors.black;
    const Color buttonColor = Colors.black;

    // Definir fuentes principales
    final TextStyle primaryFont = GoogleFonts.roboto();
    final TextStyle secondaryFont = GoogleFonts.robotoMono();

    return ThemeData(
      useMaterial3: true, // Habilitar Material 3
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryColor,
        brightness: Brightness.light,
        primary: primaryColor,
        secondary: accentColor,
        onPrimary: Colors.black,
        surface: backgroundColor, // Changed from 'background' to 'surface'
      ),
      // Estilo del texto
      textTheme: TextTheme(
        displayLarge: primaryFont.copyWith(
          fontSize: 28,
          fontWeight: FontWeight.bold,
          color: accentColor,
        ),
        titleLarge: primaryFont.copyWith(
          fontSize: 22,
          fontStyle: FontStyle.italic,
          color: accentColor,
        ),
        bodyMedium: secondaryFont.copyWith(
          fontSize: 16,
          color: accentColor,
        ),
        displaySmall: primaryFont.copyWith(
          fontSize: 20,
          color: accentColor,
        ),
        labelLarge: primaryFont.copyWith(
          fontSize: 16,
          fontWeight: FontWeight.bold,
          color: accentColor,
        ),
      ),

      // Estilo de los botones
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          foregroundColor: buttonColor,
          backgroundColor: backgroundColor,
          side: const BorderSide(color: accentColor),
          textStyle: primaryFont.copyWith(fontWeight: FontWeight.bold),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),

      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: buttonColor,
          textStyle: primaryFont.copyWith(fontWeight: FontWeight.bold),
        ),
      ),

      // Estilo de las tarjetas
      cardTheme: CardTheme(
        color: cardColor,
        shadowColor: Colors.black38,
        elevation: 6,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),

      // Estilo de los iconos
      iconTheme: const IconThemeData(
        color: accentColor,
        size: 30,
      ),

      // Estilo de AppBar
      appBarTheme: AppBarTheme(
        backgroundColor: primaryColor,
        elevation: 0,
        iconTheme: const IconThemeData(color: accentColor),
        titleTextStyle: primaryFont.copyWith(
          fontSize: 24,
          fontWeight: FontWeight.bold,
          color: Colors.black,
        ),
      ),

      // Estilo de Checkbox
      checkboxTheme: CheckboxThemeData(
        fillColor: MaterialStateProperty.all(accentColor),
        checkColor: MaterialStateProperty.all(Colors.white),
      ),

      // Estilo de BottomNavigationBar
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: backgroundColor,
        selectedItemColor: primaryColor,
        unselectedItemColor: accentColor,
        showSelectedLabels: true,
        showUnselectedLabels: true,
        selectedLabelStyle: primaryFont.copyWith(fontWeight: FontWeight.bold),
      ),
    );
  }
}
