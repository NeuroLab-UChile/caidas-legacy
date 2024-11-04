import 'package:flutter/material.dart';
import 'package:frontend/models/category.dart';
import 'package:frontend/services/category_service.dart';

class CategoryProvider with ChangeNotifier {
  List<Category> _categories = [];
  int? _selectedCategoryId;
  bool _isLoading = false;

  final CategoryService _categoryService = CategoryService();

  List<Category> get categories => _categories;
  int? get selectedCategoryId => _selectedCategoryId;
  bool get isLoading => _isLoading;

  CategoryProvider() {
    fetchCategories(); // Llama a cargar las categorías cuando se inicializa el provider
  }

  void fetchCategories() async {
    _isLoading = true;
    notifyListeners(); // Notificar que está cargando
    try {
      _categories = await _categoryService.fetchCategories(); // Usa la instancia para llamar al método
      notifyListeners(); // Notificar a los listeners que los datos están listos
    } catch (e) {
      print('Error fetching categories: $e');
    } finally {
      _isLoading = false;
      notifyListeners(); // Notificar que la carga ha finalizado
    }
  }

  void selectCategory(int id) {
    _selectedCategoryId = id;
    notifyListeners();
  }
}
