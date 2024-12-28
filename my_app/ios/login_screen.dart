import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert'; // for jsonDecode, if needed

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _identifierController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  bool _obscurePassword = true;

  // Pastel gradient background colors
  final List<Color> _bgGradientColors = const [
    Color(0xFFFFA8E8),
    Color(0xFFA0E1FF),
    Color(0xFFBAFFC9),
  ];

  Future<void> _handleLogin() async {
    final identifier = _identifierController.text.trim();
    final password = _passwordController.text;

    if (identifier.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Please enter both username/email and password")),
      );
      return;
    }

    try {
      // Replace with your actual Django endpoint
      // e.g. "http://192.168.100.119:8000/api/login/"
      // or if you have the default login_view as a DRF endpoint, adjust accordingly:
      final url = Uri.parse('http://192.168.100.119:8000/api/login/');

      // Example body keys: "identifier" and "password" if your DRF accepts them
      final response = await http.post(
        url,
        body: {
          'identifier': identifier,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        // This means success from the server.
        // Suppose your server returns JSON with user role info:
        // {
        //   "status": "ok",
        //   "user_type": "owner" or "client" or "agent" etc.
        //   ...
        // }
        final data = jsonDecode(response.body);

        if (data['status'] == 'ok') {
          // For example, check user_type and navigate accordingly:
          final userType = data['user_type'];

          if (userType == 'superuser') {
            // TODO: Navigate to an Admin dashboard screen
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text("Superuser login successful!")),
            );
          } else if (userType == 'agent') {
            // TODO: Navigator.pushNamed(context, '/agentDashboard');
          } else if (userType == 'owner') {
            // TODO: Navigator.pushNamed(context, '/ownerDashboard');
          } else if (userType == 'client') {
            // TODO: Navigator.pushNamed(context, '/clientDashboard');
          } else {
            // Default fallback
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text("Unknown user type.")),
            );
          }
        } else {
          // Show error from server
          final errorMsg = data['message'] ?? "Login failed.";
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(errorMsg)),
          );
        }
      } else {
        // For any 400/500 code
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error: ${response.statusCode}")),
        );
      }
    } catch (e) {
      // e.g. SocketException => connection refused
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Exception: $e")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        // Pastel gradient
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: _bgGradientColors,
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Center(
          child: SingleChildScrollView(
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 20),
              padding: const EdgeInsets.all(24),
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
                  const Text(
                    'Welcome to makazihub',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFFFF75A0),
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 20),
                  // The house icon from your assets
                  Container(
                    margin: const EdgeInsets.only(bottom: 20),
                    child: Image.asset(
                      'assets/images/house.png',
                      width: 80,
                      height: 80,
                    ),
                  ),
                  // Identifier
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
                  // Password
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
                  // Login Button
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
                  // Additional links
                  Column(
                    children: [
                      GestureDetector(
                        onTap: () {
                          // Navigate or do something for Register
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
