import 'package:flutter/material.dart';
import 'package:frontend/models/category.dart';
import 'package:frontend/models/activity_node.dart';
import 'package:frontend/providers/category_provider.dart';
import 'package:provider/provider.dart';

class CategoryHandler extends StatelessWidget {
  final Category category;

  const CategoryHandler({Key? key, required this.category}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final categoryProvider = Provider.of<CategoryProvider>(context);
    final node = categoryProvider.nodes.firstWhere(
      (node) => node.id == category.rootNode,
      orElse: () => ActivityNode(
          id: -1, description: 'No node found', type: 'CATEGORY_DESCRIPTION'),
    );

    return Scaffold(
      backgroundColor: const Color(0xFFFFFF00), // Yellow background
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'Volver',
          style: TextStyle(color: Colors.black, fontSize: 24),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: Container(
              margin: const EdgeInsets.only(top: 20),
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(30),
                  topRight: Radius.circular(30),
                ),
              ),
              child: categoryProvider.isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : categoryProvider.error != null
                      ? _buildErrorView(categoryProvider.error!)
                      : _buildNodeContent(context, node),
            ),
          ),
          _buildBottomNavigation(),
        ],
      ),
    );
  }

  Widget _buildNodeContent(BuildContext context, ActivityNode node) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 20),
            child: Row(
              children: [
                Icon(Icons.circle, size: 12, color: Colors.black),
                const SizedBox(width: 8),
                Text(
                  '/${category.name}',
                  style: TextStyle(fontSize: 16, color: Colors.black87),
                ),
              ],
            ),
          ),
          _buildNodeTypeContent(context, node),
        ],
      ),
    );
  }

  Widget _buildNodeTypeContent(BuildContext context, ActivityNode node) {
    switch (node.type) {
      case 'CATEGORY_DESCRIPTION':
        return _buildCategoryDescription(context, node);
      case 'TEXT_QUESTION':
        return _buildTextQuestion(context, node);
      case 'SINGLE_CHOICE_QUESTION':
        return _buildSingleChoiceQuestion(context, node);
      case 'MULTIPLE_CHOICE_QUESTION':
        return _buildMultipleChoiceQuestion(context, node);
      case 'SCALE_QUESTION':
        return _buildScaleQuestion(context, node);
      case 'IMAGE_QUESTION':
        return _buildImageQuestion(context, node);
      default:
        return Text('Tipo de nodo no reconocido: ${node.type}');
    }
  }

  Widget _buildCategoryDescription(BuildContext context, ActivityNode node) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          node.description,
          style:
              const TextStyle(fontSize: 18, height: 1.5, color: Colors.black87),
        ),
        const SizedBox(height: 20),
        _buildActionButtons(),
      ],
    );
  }

  Widget _buildTextQuestion(BuildContext context, ActivityNode node) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          node.description,
          style:
              const TextStyle(fontSize: 18, height: 1.5, color: Colors.black87),
        ),
        const SizedBox(height: 20),
        TextField(
          decoration: InputDecoration(
            border: OutlineInputBorder(),
            hintText: 'Escribe tu respuesta aquí',
          ),
          maxLines: 3,
        ),
        const SizedBox(height: 20),
        ElevatedButton(
          child: Text('Enviar Respuesta'),
          onPressed: () {
            // Handle text submission
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blue,
            padding: EdgeInsets.symmetric(horizontal: 50, vertical: 15),
          ),
        ),
      ],
    );
  }

  Widget _buildSingleChoiceQuestion(BuildContext context, ActivityNode node) {
    List<String> options = [
      'Opción 1',
      'Opción 2',
      'Opción 3'
    ]; // Replace with actual options
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          node.description,
          style: const TextStyle(fontSize: 18, height: 1.5),
        ),
        const SizedBox(height: 20),
        ...options
            .map((option) => Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: ElevatedButton(
                    child: Text(option),
                    onPressed: () {
                      // Handle option selection
                    },
                    style: ElevatedButton.styleFrom(
                      foregroundColor: Colors.black,
                      backgroundColor: Colors.white,
                      side: BorderSide(color: Colors.grey),
                      padding: EdgeInsets.symmetric(vertical: 15),
                    ),
                  ),
                ))
            .toList(),
      ],
    );
  }

  Widget _buildMultipleChoiceQuestion(BuildContext context, ActivityNode node) {
    List<String> options = [
      'Opción 1',
      'Opción 2',
      'Opción 3'
    ]; // Replace with actual options
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          node.description,
          style: const TextStyle(fontSize: 18, height: 1.5),
        ),
        const SizedBox(height: 20),
        ...options
            .map((option) => CheckboxListTile(
                  title: Text(option),
                  value: false, // Replace with actual state
                  onChanged: (bool? value) {
                    // Handle checkbox state change
                  },
                ))
            .toList(),
        const SizedBox(height: 20),
        ElevatedButton(
          child: Text('Enviar Selección'),
          onPressed: () {
            // Handle multiple choice submission
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blue,
            padding: EdgeInsets.symmetric(horizontal: 50, vertical: 15),
          ),
        ),
      ],
    );
  }

  Widget _buildScaleQuestion(BuildContext context, ActivityNode node) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          node.description,
          style: const TextStyle(fontSize: 18, height: 1.5),
        ),
        const SizedBox(height: 20),
        Slider(
          value: 5, // Replace with actual value
          min: 1,
          max: 10,
          divisions: 9,
          label: '5', // Replace with actual label
          onChanged: (double value) {
            // Handle slider value change
          },
        ),
        const SizedBox(height: 20),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('1', style: TextStyle(fontSize: 16)),
            Text('10', style: TextStyle(fontSize: 16)),
          ],
        ),
        const SizedBox(height: 20),
        ElevatedButton(
          child: Text('Enviar Calificación'),
          onPressed: () {
            // Handle scale submission
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blue,
            padding: EdgeInsets.symmetric(horizontal: 50, vertical: 15),
          ),
        ),
      ],
    );
  }

  Widget _buildImageQuestion(BuildContext context, ActivityNode node) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          node.description,
          style: const TextStyle(fontSize: 18, height: 1.5),
        ),
        const SizedBox(height: 20),
        Image.network(
          'https://example.com/image.jpg', // Replace with actual image URL
          width: double.infinity,
          height: 200,
          fit: BoxFit.cover,
        ),
        const SizedBox(height: 20),
        TextField(
          decoration: InputDecoration(
            border: OutlineInputBorder(),
            hintText: 'Escribe tu respuesta aquí',
          ),
          maxLines: 3,
        ),
        const SizedBox(height: 20),
        ElevatedButton(
          child: Text('Enviar Respuesta'),
          onPressed: () {
            // Handle image question submission
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blue,
            padding: EdgeInsets.symmetric(horizontal: 50, vertical: 15),
          ),
        ),
      ],
    );
  }

  Widget _buildActionButtons() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        OutlinedButton.icon(
          icon: const Icon(Icons.check_box_outlined),
          label: const Text('Evaluación'),
          onPressed: () {},
          style: OutlinedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          icon: const Icon(Icons.sports),
          label: const Text('Entrenamiento'),
          onPressed: () {},
          style: OutlinedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildBottomNavigation() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(top: BorderSide(color: Colors.grey.shade300)),
      ),
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildNavItem(Icons.calendar_today, 'RECORDAR'),
          _buildNavItem(Icons.check_box_outlined, 'EVALUAR'),
          Image.asset('assets/logo.png', height: 40), // PREIDAS logo
          _buildNavItem(Icons.sports, 'ENTRENAR'),
          _buildNavItem(Icons.person_outline, 'MIS DATOS'),
        ],
      ),
    );
  }

  Widget _buildNavItem(IconData icon, String label) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 24),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }

  Widget _buildErrorView(String error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 48, color: Colors.red[300]),
            const SizedBox(height: 16),
            Text(
              error,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.red),
            ),
          ],
        ),
      ),
    );
  }
}
