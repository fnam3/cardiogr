import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';
import 'package:permission_handler/permission_handler.dart';
import 'instructions.dart';

void main() {
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: InstructionsScreen(),
  ));
}

class Esp32BluetoothPage extends StatefulWidget {
  const Esp32BluetoothPage({super.key});

  @override
  State<Esp32BluetoothPage> createState() => _Esp32BluetoothPageState();
}

class _Esp32BluetoothPageState extends State<Esp32BluetoothPage> {
  final FlutterBluetoothSerial _bt = FlutterBluetoothSerial.instance;

  StreamSubscription<BluetoothDiscoveryResult>? _discoverySub;
  final List<BluetoothDiscoveryResult> _scanResults = [];
  bool _isDiscovering = false;

  BluetoothConnection? _connection;
  bool get _isConnected => _connection != null && _connection!.isConnected;

  final _incomingBuffer = StringBuffer(); // для сборки строк по \n
  final List<double> _numericData = [];

  final TextEditingController _txCtrl = TextEditingController(text: "ping\n");

  @override
  void initState() {
    super.initState();
    _init();
  }

  @override
  void dispose() {
    _discoverySub?.cancel();
    _connection?.dispose();
    super.dispose();
  }

  Future<void> _init() async {
    // 1) Разрешения
    await _ensurePermissions();

    // 2) Включить BT при необходимости
    final isEnabled = (await _bt.isEnabled) ?? false;
    if (!isEnabled) {
      await _bt.requestEnable();
    }

    // 3) Подписка на изменения состояния BT (не обязательно)
    _bt.onStateChanged().listen((state) {
      if (mounted) setState(() {});
    });
  }

  Future<void> _ensurePermissions() async {
    // Android 12+ требует BLUETOOTH_SCAN/CONNECT
    final Map<Permission, PermissionStatus> statuses = await [
      Permission.bluetoothScan,
      Permission.bluetoothConnect,
      // Для Android <= 10 (сканирование)
      Permission.locationWhenInUse,
    ].request();

    // Можно отреагировать по-другому (диалог/снекбар), тут — простой чек
    if (statuses.values.any((s) => s.isPermanentlyDenied)) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('Разрешения BT отклонены. Откройте настройки приложения.'),
        ));
      }
      openAppSettings();
    }
  }

  void _startDiscovery() async {
    setState(() {
      _scanResults.clear();
      _isDiscovering = true;
    });

    _discoverySub = _bt.startDiscovery().listen((r) {
      final existingIndex = _scanResults.indexWhere(
        (e) => e.device.address == r.device.address,
      );
      if (existingIndex >= 0) {
        _scanResults[existingIndex] = r;
      } else if (r.device.name == "Cardioreg") {
        _scanResults.add(r);
      }
      if (mounted) setState(() {});
    });

    _discoverySub!.onDone(() {
      if (mounted) {
        setState(() {
          _isDiscovering = false;
        });
      }
    });
  }

  Future<void> _connect(BluetoothDevice device) async {
    try {
      // Примечание: для SPP-профиля (ESP32 SerialBT) UUID по умолчанию:
      // 00001101-0000-1000-8000-00805F9B34FB — плагин использует его под капотом.
      final conn = await BluetoothConnection.toAddress(device.address);
      setState(() => _connection = conn);

      // Подписка на входящий поток
      conn.input?.listen((Uint8List data) {
        // предполагаем текст в UTF-8 с \n на конце
        final chunk = utf8.decode(data, allowMalformed: true);
        _incomingBuffer.write(chunk);

        // разбор построчно
        String current = _incomingBuffer.toString();
        int idx;
        while ((idx = current.indexOf('\n')) != -1) {
          final line = current.substring(0, idx).trimRight();
          
          // Try to parse the line as a number and add to numeric data array
          try {
            final value = double.parse(line);
            _numericData.add(value);
          } catch (e) {
            // If parsing fails, we ignore the value
          }
          
          current = current.substring(idx + 1);
        }
        _incomingBuffer
          ..clear()
          ..write(current);

        if (mounted) setState(() {});
      }).onDone(() {
        // Устройство отключилось
        if (mounted) {
          setState(() {
            _connection = null;
          });
        }
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Не удалось подключиться: $e')),
        );
      }
    }
  }

  Future<void> _disconnect() async {
    await _connection?.close();
    setState(() => _connection = null);
  }

  Future<void> _send() async {
    final text = _txCtrl.text;
    if (text.isEmpty || !_isConnected) return;
    _connection!.output.add(utf8.encode(text));
    await _connection!.output.allSent;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ESP32 Bluetooth (SPP)'),
        actions: [
          IconButton(
            onPressed: _isDiscovering ? null : _startDiscovery,
            icon: Icon(_isDiscovering ? Icons.bluetooth_searching : Icons.search),
            tooltip: 'Сканировать',
          ),
          const SizedBox(width: 4),
        ],
      ),
      body: Column(
        children: [
          _buildBtStateTile(),
          // Show array of numeric data when connected instead of message box
          if (_isConnected) _buildNumericDataDisplay(),
          Expanded(child: _buildScanOrLog()),
        ],
      ),
      floatingActionButton: _isConnected
          ? FloatingActionButton.extended(
              onPressed: _disconnect,
              icon: const Icon(Icons.link_off),
              label: const Text('Отключить'),
            )
          : null,
    );
  }

  Widget _buildBtStateTile() {
    return FutureBuilder<bool?>(
      future: _bt.isEnabled,
      builder: (context, snap) {
        final enabled = snap.data ?? false;
        return ListTile(
          leading: Icon(enabled ? Icons.bluetooth : Icons.bluetooth_disabled),
          title: Text(enabled ? 'Bluetooth включён' : 'Bluetooth выключен'),
          subtitle: Text(_isConnected
              ? 'Подключено'
              : 'Не подключено'),
          trailing: enabled
              ? null
              : ElevatedButton(
                  onPressed: () async {
                    await _bt.requestEnable();
                    setState(() {});
                  },
                  child: const Text('Вкл.'),
                ),
        );
      },
    );
  }

  Widget _buildScanOrLog() {
    if (_isConnected) {
      // Show the array of numeric data instead of individual messages
      return Container();
    }

    // Список найденных устройств
    if (_isDiscovering && _scanResults.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    return ListView.separated(
      padding: const EdgeInsets.all(8),
      itemCount: _scanResults.length,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (_, i) {
        final r = _scanResults[i];
        final d = r.device;
        return ListTile(
          leading: const Icon(Icons.bluetooth),
          title: Text(d.name ?? 'Неизвестное устройство'),
          subtitle: Text('${d.address}${' · RSSI ${r.rssi}'}'),
          trailing: ElevatedButton(
            onPressed: () => _connect(d),
            child: const Text('Подключить'),
          ),
        );
      },
    );
  }

  Widget _buildNumericDataDisplay() {
    return Padding(
      padding: const EdgeInsets.all(12),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey),
          borderRadius: BorderRadius.circular(4),
        ),
        child: Text(
          _numericData.toString(),
          style: const TextStyle(fontFamily: 'monospace'),
        ),
      ),
    );
  }

  // Widget _buildTxBox() {
  //   return Padding(
  //     padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
  //     child: Row(
  //       children: [
  //         Expanded(
  //           child: TextField(
  //             controller: _txCtrl,
  //             decoration: const InputDecoration(
  //               labelText: 'Команда',
  //               hintText: 'например: ping\\n',
  //               border: OutlineInputBorder(),
  //             ),
  //           ),
  //         ),
  //         const SizedBox(width: 8),
  //         ElevatedButton(
  //           onPressed: _send,
  //           child: const Text('Отправить'),
  //         ),
  //       ],
  //     ),
  //   );
  // }
}