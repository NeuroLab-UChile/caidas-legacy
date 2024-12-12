import 'package:flutter/material.dart';
import 'package:frontend/models/category.dart';
import 'package:frontend/services/category_service.dart';

class CategoryProvider with ChangeNotifier {
  List<Category> _categories = [];
  int? _selectedCategoryId;
  bool _isLoading = false;
  String? _error;

  final CategoryService _categoryService = CategoryService();

  List<Category> get categories => _categories;
  int? get selectedCategoryId => _selectedCategoryId;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchCategories() async {
    if (_isLoading) return;

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _categories = await _categoryService.fetchCategories();
      _error = null;
    } catch (e) {
      _error = e.toString();
      print('Error fetching categories: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void selectCategory(int id) {
    _selectedCategoryId = id;
    notifyListeners();
  }
}
