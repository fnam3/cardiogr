import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'main.dart'; // Import main.dart to access Esp32BluetoothPage

class InstructionsScreen extends StatefulWidget {
  const InstructionsScreen({super.key});

  @override
  State<InstructionsScreen> createState() => _InstructionsScreenState();
}

class _InstructionsScreenState extends State<InstructionsScreen> {
  bool _isEcgSelected = false;
  bool _isBreathSelected = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white, // Set background color to white
      body: Stack(
        children: [
          // SVG логотип вверху экрана
          Container(
            alignment: Alignment.topCenter,
            padding: const EdgeInsets.only(top: 50),
            child: SvgPicture.asset(
              'assets/neurotech.svg',
              height: 40,
            ),
          ),
          // Выбор биологического сигнала по центру экрана
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text(
                  'выберите, какой биологический сигнал регистрировать:',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 30),
                Container(
                  width: MediaQuery.of(context).size.width * 0.8,
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // ECG Button
                      ElevatedButton(
                        onPressed: () {
                          setState(() {
                            _isEcgSelected = !_isEcgSelected;
                          });
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _isEcgSelected 
                              ? const Color(0xFF148dc6) // Blue when selected
                              : Colors.white, // White when not selected
                          foregroundColor: _isEcgSelected 
                              ? Colors.white 
                              : Colors.black,
                          textStyle: const TextStyle(
                            fontWeight: FontWeight.bold,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                            side: const BorderSide(
                              color: Color(0xFF148dc6),
                              width: 1,
                            ),
                          ),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 20,
                            vertical: 15,
                          ),
                          minimumSize: const Size.fromHeight(50),
                        ),
                        child: const Text('ЭКГ'),
                      ),
                      const SizedBox(height: 15),
                      // Breathing Button
                      ElevatedButton(
                        onPressed: () {
                          setState(() {
                            _isBreathSelected = !_isBreathSelected;
                          });
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _isBreathSelected 
                              ? const Color(0xFF148dc6) // Blue when selected
                              : Colors.white, // White when not selected
                          foregroundColor: _isBreathSelected 
                              ? Colors.white 
                              : Colors.black,
                          textStyle: const TextStyle(
                            fontWeight: FontWeight.bold,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                            side: const BorderSide(
                              color: Color(0xFF148dc6),
                              width: 1,
                            ),
                          ),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 20,
                            vertical: 15,
                          ),
                          minimumSize: const Size.fromHeight(50),
                        ),
                        child: const Text('дыхание'),
                      ),
                      const SizedBox(height: 30),
                      // Continue Button
                      ElevatedButton(
                        onPressed: (_isEcgSelected || _isBreathSelected)
                            ? () {
                                Navigator.pushReplacement(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) => Esp32BluetoothPage(
                                      isEcgSelected: _isEcgSelected,
                                      isBreathSelected: _isBreathSelected,
                                    ),
                                  ),
                                );
                              }
                            : null,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF148dc6), // Синий цвет
                          foregroundColor: Colors.white, // Белый текст
                          textStyle: const TextStyle(
                            fontWeight: FontWeight.bold,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 20,
                            vertical: 15,
                          ),
                          minimumSize: const Size.fromHeight(50),
                        ),
                        child: const Text('продолжить'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// class _DetailScreen extends StatelessWidget {
//   final String title;

//   const _DetailScreen({required this.title});

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       backgroundColor: Colors.white, // Set background color to white
//       appBar: AppBar(
//         title: Text(title),
//         backgroundColor: Colors.white,
//         foregroundColor: Colors.black,
//         elevation: 0,
//       ),
//       body: Column(
//         mainAxisAlignment: MainAxisAlignment.center,
//         children: [
//           // Отображаем изображение на всю ширину экрана
//           Image.asset(
//             'assets/$title',
//             width: MediaQuery.of(context).size.width, // Полная ширина экрана
//             fit: BoxFit.contain, // Сохраняем пропорции
//             errorBuilder: (context, error, stackTrace) {
//               return Text(
//                 title,
//                 style: const TextStyle(
//                   fontSize: 24,
//                   fontWeight: FontWeight.bold,
//                 ),
//               );
//             },
//           ),
//           const SizedBox(height: 30),
//           // Синяя кнопка "присоединил" in DetailScreen that navigates to the real Bluetooth screen
//           Padding(
//             padding: const EdgeInsets.symmetric(horizontal: 20),
//             child: ElevatedButton(
//               onPressed: () {
//                 Navigator.pushReplacement(
//                   context,
//                   MaterialPageRoute(
//                     builder: (context) => const Esp32BluetoothPage(),
//                   ),
//                 );
//               },
//               style: ElevatedButton.styleFrom(
//                 backgroundColor: const Color(0xFF148dc6), // Синий цвет
//                 foregroundColor: Colors.white, // Белый текст
//                 textStyle: const TextStyle(
//                   fontWeight: FontWeight.bold,
//                 ),
//                 shape: RoundedRectangleBorder(
//                   borderRadius: BorderRadius.circular(8),
//                 ),
//                 padding: const EdgeInsets.symmetric(
//                   horizontal: 20,
//                   vertical: 15,
//                 ),
//                 minimumSize: const Size.fromHeight(50),
//               ),
//               child: const Text('присоединил'),
//             ),
//           ),
//         ],
//       ),
//     );
//   }
// }