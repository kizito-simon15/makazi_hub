// lib/screens/admin_dashboard_screen.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class AdminDashboardScreen extends StatefulWidget {
  const AdminDashboardScreen({Key? key}) : super(key: key);

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  // Replace with your actual IP or domain if needed
  final String baseUrl = 'http://192.168.100.119:8000';

  // Example data placeholders
  int totalUsers = 0;
  int totalOwners = 0;
  int totalAgents = 0;
  int totalClients = 0;
  bool isLoading = true;
  String? errorMessage;

  // If you want to fetch actual data from your Django admin_dashboard_api:
  Future<void> _fetchAdminData() async {
    try {
      final uri = Uri.parse('$baseUrl/api/admin_dashboard/');
      final response = await http.get(uri);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          totalUsers = data['total_users'];
          totalOwners = data['total_owners'];
          totalAgents = data['total_agents'];
          totalClients = data['total_clients'];
          isLoading = false;
        });
      } else if (response.statusCode == 403) {
        setState(() {
          errorMessage = 'Unauthorized';
          isLoading = false;
        });
      } else {
        setState(() {
          errorMessage = 'Unexpected error: ${response.statusCode}';
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = 'Exception: $e';
        isLoading = false;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    // If you need to fetch real data from Django:
    // _fetchAdminData();
    // If you want a placeholder only:
    setState(() => isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Admin Dashboard"),
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : errorMessage != null
              ? Center(child: Text(errorMessage!))
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Text("Total Users: $totalUsers"),
                      Text("Total Owners: $totalOwners"),
                      Text("Total Agents: $totalAgents"),
                      Text("Total Clients: $totalClients"),
                      const SizedBox(height: 20),
                      // Placeholder for growth charts, etc.
                      const Text("Charts/Advice placeholders here..."),
                    ],
                  ),
                ),
    );
  }
}
