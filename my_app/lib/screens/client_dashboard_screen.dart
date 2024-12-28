// lib/screens/client_dashboard_screen.dart
import 'package:flutter/material.dart';

class ClientDashboardScreen extends StatelessWidget {
  const ClientDashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Client Dashboard"),
      ),
      body: const Center(
        child: Text("Here you can show client-related info, etc."),
      ),
    );
  }
}
