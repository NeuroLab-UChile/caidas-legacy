import 'package:flutter/material.dart';
import 'package:frontend/models/physical_activity.dart';
import 'package:frontend/services/physical_activity_service.dart';

class PhysicalActivityScreen extends StatefulWidget {
  const PhysicalActivityScreen({super.key});

  @override
  PhysicalActivityScreenState createState() => PhysicalActivityScreenState();
}

class PhysicalActivityScreenState extends State<PhysicalActivityScreen> {
  PhysicalActivityDetail? activityDetail;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchActivityDetail();
  }

  Future<void> _fetchActivityDetail() async {
    try {
      final detail = await PhysicalActivityService().getPhysicalActivityDetail();
      setState(() {
        activityDetail = detail;
        isLoading = false;
      });
    } catch (e) {
      print('Error fetching activity detail: $e');
      setState(() {
        isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading activity details: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Actividad Física'),
        backgroundColor: Colors.green,
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (activityDetail != null) ...[
                      const SizedBox(height: 16),
                      Text(
                        activityDetail!.description,
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                      const SizedBox(height: 24),
                      Text(
                        activityDetail!.description2,
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    ],
                  ],
                ),
              ),
            ),
    );
  }
}
