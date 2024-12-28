import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  // Text controllers
  final TextEditingController _identifierController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  // Track whether password is hidden
  bool _obscurePassword = true;

  // Pastel gradient colors from the HTML version
  final List<Color> _bgGradientColors = const [
    Color(0xFFFFA8E8), // #ffa8e8
    Color(0xFFA0E1FF), // #a0e1ff
    Color(0xFFBAFFC9), // #baffc9
  ];

  // Show a simple snack bar
  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  // Handle login button press
  Future<void> _handleLogin() async {
    final identifier = _identifierController.text.trim();
    final password = _passwordController.text.trim();

    if (identifier.isEmpty || password.isEmpty) {
      _showSnackBar("Please enter both username/email and password");
      return;
    }

    try {
      // Replace the IP/port with your actual Django server or use adb reverse
      // e.g. final url = Uri.parse('http://192.168.100.119:8000/api/login/');
      final url = Uri.parse('http://192.168.100.119:8000/api/login/');

      final response = await http.post(
        url,
        body: {
          'identifier': identifier,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);

        // Check if the login was successful
        if (jsonData['success'] == true) {
          // Retrieve the role from the response
          final role = jsonData['role'] as String?;
          if (role == null) {
            _showSnackBar("Unknown role received from server.");
            return;
          }

          // Optionally show a snack bar for immediate feedback
          _showSnackBar("${role[0].toUpperCase()}${role.substring(1)} login success!");

          // Navigate based on role
          if (role == 'superuser') {
            Navigator.pushNamed(context, '/adminDashboard');
          } else if (role == 'agent') {
            Navigator.pushNamed(context, '/agentDashboard');
          } else if (role == 'propertyowner') {
            Navigator.pushNamed(context, '/ownerDashboard');
          } else if (role == 'client') {
            Navigator.pushNamed(context, '/clientDashboard');
          } else {
            _showSnackBar("Unknown user role: $role");
          }
        } else {
          // success == false
          final message =
              jsonData['message'] ?? "Login failed. Check credentials.";
          _showSnackBar(message);
        }
      } else {
        // e.g. 400, 403, 500...
        _showSnackBar("HTTP Error: ${response.statusCode}");
      }
    } catch (e) {
      // Any exceptions from the HTTP request, e.g. no connection
      _showSnackBar("Exception: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Remove any default app bar
      body: Container(
        width: double.infinity,
        height: double.infinity,
        // Pastel gradient background
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: _bgGradientColors,
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        // Align content in the center
        child: Center(
          child: SingleChildScrollView(
            // So screen scrolls if on smaller devices
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 20),
              padding: const EdgeInsets.all(24),
              // Mimic the glassy card effect with some opacity
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.85),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Title
                  const Text(
                    'Welcome to makazihub',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFFFF75A0), // #ff75a0
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 20),

                  // Image icon (house.png)
                  Container(
                    margin: const EdgeInsets.only(bottom: 20),
                    child: Image.asset(
                      'assets/images/house.png',
                      width: 80,
                      height: 80,
                    ),
                  ),

                  // Identifier (username/email) field
                  Container(
                    margin: const EdgeInsets.only(bottom: 20),
                    child: TextField(
                      controller: _identifierController,
                      decoration: InputDecoration(
                        hintText: 'Username or Email',
                        prefixIcon:
                            const Icon(Icons.person, color: Color(0xFFC77DFF)),
                        fillColor: Colors.white,
                        filled: true,
                        contentPadding: const EdgeInsets.symmetric(
                            vertical: 15, horizontal: 15),
                        enabledBorder: OutlineInputBorder(
                          borderSide: const BorderSide(
                              color: Color(0xFFEEDCFF), width: 2),
                          borderRadius: BorderRadius.circular(25),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderSide: const BorderSide(
                              color: Color(0xFFC77DFF), width: 2),
                          borderRadius: BorderRadius.circular(25),
                        ),
                      ),
                    ),
                  ),

                  // Password field
                  Container(
                    margin: const EdgeInsets.only(bottom: 20),
                    child: TextField(
                      controller: _passwordController,
                      obscureText: _obscurePassword,
                      decoration: InputDecoration(
                        hintText: 'Password',
                        prefixIcon:
                            const Icon(Icons.lock, color: Color(0xFFC77DFF)),
                        suffixIcon: GestureDetector(
                          onTap: () =>
                              setState(() => _obscurePassword = !_obscurePassword),
                          child: Icon(
                            _obscurePassword
                                ? Icons.visibility
                                : Icons.visibility_off,
                            color: const Color(0xFFC77DFF),
                          ),
                        ),
                        fillColor: Colors.white,
                        filled: true,
                        contentPadding: const EdgeInsets.symmetric(
                            vertical: 15, horizontal: 15),
                        enabledBorder: OutlineInputBorder(
                          borderSide: const BorderSide(
                              color: Color(0xFFEEDCFF), width: 2),
                          borderRadius: BorderRadius.circular(25),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderSide: const BorderSide(
                              color: Color(0xFFC77DFF), width: 2),
                          borderRadius: BorderRadius.circular(25),
                        ),
                      ),
                    ),
                  ),

                  // Login button
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton(
                      onPressed: _handleLogin,
                      style: ElevatedButton.styleFrom(
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(25),
                        ),
                        backgroundColor: const Color(0xFFFFA8E8),
                      ),
                      child: const Text(
                        'Login',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Bottom text links
                  Column(
                    children: [
                      GestureDetector(
                        onTap: () {
                          // Navigate to a Register screen or open a webview, etc.
                        },
                        child: const Text(
                          "Don't have an account? Register",
                          style: TextStyle(
                            color: Color(0xFFC77DFF),
                            decoration: TextDecoration.underline,
                          ),
                        ),
                      ),
                      const SizedBox(height: 6),
                      GestureDetector(
                        onTap: () {
                          // Forgot password
                        },
                        child: const Text(
                          "Forgot password? Get new one",
                          style: TextStyle(
                            color: Color(0xFFC77DFF),
                            decoration: TextDecoration.underline,
                          ),
                        ),
                      ),
                      const SizedBox(height: 6),
                      GestureDetector(
                        onTap: () {
                          // Browse as guest
                        },
                        child: const Text(
                          "Browse as guest",
                          style: TextStyle(
                            color: Color(0xFFC77DFF),
                            decoration: TextDecoration.underline,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
