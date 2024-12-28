// lib/screens/agent_dashboard_screen.dart
import 'package:flutter/material.dart';

class AgentDashboardScreen extends StatelessWidget {
  const AgentDashboardScreen({Key? key}) : super(key: key);

  // Optionally fetch houses assigned to the agent from an API
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Agent Dashboard"),
      ),
      body: const Center(
        child: Text("Here you can show assigned houses, etc."),
      ),
    );
  }
}
