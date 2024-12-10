import 'package:flutter/material.dart';
import 'package:frontend/models/category.dart';
import 'package:frontend/models/activity_node.dart';
import 'package:frontend/services/category_service.dart';

class CategoryProvider with ChangeNotifier {
  List<Category> _categories = [];
  List<ActivityNode> _nodes = [];
  int? _selectedCategoryId;
  bool _isLoading = false;
  String? _error;

  final CategoryService _categoryService = CategoryService();

  List<Category> get categories => _categories;
  List<ActivityNode> get nodes => _nodes;
  int? get selectedCategoryId => _selectedCategoryId;
  bool get isLoading => _isLoading;
  String? get error => _error;

  CategoryProvider() {
    fetchCategoriesAndNodes();
  }

  // Método para cargar las categorías y nodos juntos
  Future<void> fetchCategoriesAndNodes() async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      // Obtener tanto categorías como nodos desde el mismo método
      final data = await _categoryService.fetchCategoriesAndNodes();
      _categories = data['categories'] as List<Category>;
      _nodes = data['nodes'] as List<ActivityNode>;
    } catch (e) {
      _error = e.toString();
      print('Error fetching categories and nodes: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Método para seleccionar una categoría
  void selectCategory(int id) {
    _selectedCategoryId = id;
    notifyListeners();
  }
}
