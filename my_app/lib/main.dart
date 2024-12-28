import 'package:flutter/material.dart';
// Import your LoginScreen here
import 'login_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Makazihub Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      // Define your routes
      routes: {
        '/': (context) => const LoginScreen(),
        '/login': (context) => const LoginScreen(),
        '/adminDashboard': (context) => const AdminDashboardScreen(),
        '/agentDashboard': (context) => const AgentDashboardScreen(),
        '/ownerDashboard': (context) => const OwnerDashboardScreen(),
        '/clientDashboard': (context) => const ClientDashboardScreen(),
      },
      // Start at the login page
      initialRoute: '/login',
    );
  }
}

// ---------------------------------------------------------------------------
// Below are placeholder dashboard screens. Replace with real UIs as needed.
// ---------------------------------------------------------------------------
class AdminDashboardScreen extends StatelessWidget {
  const AdminDashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Admin Dashboard'),
      ),
      body: Center(
        child: Text(
          'Welcome, Superuser!',
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ),
    );
  }
}

class AgentDashboardScreen extends StatelessWidget {
  const AgentDashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Agent Dashboard'),
      ),
      body: Center(
        child: Text(
          'Welcome, Agent!',
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ),
    );
  }
}

class OwnerDashboardScreen extends StatelessWidget {
  const OwnerDashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Owner Dashboard'),
      ),
      body: Center(
        child: Text(
          'Welcome, Property Owner!',
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ),
    );
  }
}

class ClientDashboardScreen extends StatelessWidget {
  const ClientDashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Client Dashboard'),
      ),
      body: Center(
        child: Text(
          'Welcome, Client!',
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ),
    );
  }
}
