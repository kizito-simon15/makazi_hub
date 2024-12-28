// lib/screens/owner_dashboard_screen.dart
import 'package:flutter/material.dart';

class OwnerDashboardScreen extends StatelessWidget {
  const OwnerDashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Owner Dashboard"),
      ),
      body: const Center(
        child: Text("Here you can show properties owned, etc."),
      ),
    );
  }
}
