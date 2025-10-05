import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
import serial
import serial.tools.list_ports

class USBConnectionWindow(QMainWindow):
    def __init__(self, main_window=None, choose_connect_window=None, selected_signals=None):
        super().__init__()
        self.main_window = main_window
        self.choose_connect_window = choose_connect_window
        self.selected_signals = selected_signals or set()  # Store selected signals
        self.esp32_connected = False
        self.serial_connection = None
        self.data_buffer = []
        self.pulse_value = 0  # Store the current pulse value
        self.last_breath_status = None  # Track breath status
        self.initUI()
        self.startConnectionDetection()
    
    def initUI(self):
        # Set window properties - make it resizable
        self.setWindowTitle('Подключение через USB')
        self.setGeometry(200, 200, 800, 600)
        # Remove fixed size to make it scalable
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        central_widget.setLayout(main_layout)
        
        # Create status label
        self.status_label = QLabel('Подключите устройство')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px; color: #666;")
        main_layout.addWidget(self.status_label)
        
        # Create breath status label (initially hidden)
        self.breath_label = QLabel('Ожидание данных о дыхании...')
        self.breath_label.setAlignment(Qt.AlignCenter)
        self.breath_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #666;")
        self.breath_label.setVisible(False)
        main_layout.addWidget(self.breath_label)
        
        # Create graph display area
        self.graph_widget = GraphWidget(self)
        self.graph_widget.setVisible(False)  # Hidden by default
        main_layout.addWidget(self.graph_widget)
    
    def startConnectionDetection(self):
        """Start periodic checking for ESP32 connection"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkForESP32)
        self.timer.start(2000)  # Check every 2 seconds
        self.checkForESP32()  # Initial check
    
    def checkForESP32(self):
        """Check for connected ESP32 devices"""
        esp32_found = self.detectESP32()
        
        if esp32_found and not self.esp32_connected:
            # ESP32 just got connected
            self.esp32_connected = True
            self.status_label.setVisible(False)  # Hide the status label
            # Show graph display area only if ECG is selected
            if 'ЭКГ' in self.selected_signals:
                self.graph_widget.setVisible(True)
            # Start reading data
            self.startDataReading()
        elif not esp32_found and self.esp32_connected:
            # ESP32 was disconnected
            self.esp32_connected = False
            self.status_label.setVisible(True)  # Show the status label
            self.status_label.setText('Подключите кардиограф')
            self.status_label.setStyleSheet("font-size: 18px; color: #666;")
            # Hide graph display area
            self.graph_widget.setVisible(False)
            # Stop reading data
            self.stopDataReading()
    
    def detectESP32(self):
        """Detect if an ESP32 device is connected via USB"""
        try:
            # Get list of all available ports
            ports = serial.tools.list_ports.comports()
            
            for port in ports:
                # Check if the port description or hardware ID contains ESP32 identifiers
                if any(keyword in port.description.upper() for keyword in ['ESP32', 'CP210', 'CH340', 'FTDI']):
                    # Try to open the port to confirm it's responsive
                    try:
                        ser = serial.Serial(port.device, 9600, timeout=1)
                        ser.close()
                        # Store the port for data reading
                        self.esp32_port = port.device
                        return True
                    except (OSError, serial.SerialException):
                        # Port is busy or not accessible, but it might still be an ESP32
                        # We'll consider it as found since the description matches
                        self.esp32_port = port.device
                        return True
                
                # Some ESP32 boards might not have descriptive names
                # Check common VID/PID combinations for ESP32 boards
                if any(esp32_id in port.hwid for esp32_id in [
                    'VID:10C4',  # CP210x USB to UART Bridge
                    'VID:1A86',  # CH340 USB to Serial
                    'VID:0403',  # FTDI
                ]):
                    self.esp32_port = port.device
                    return True
            
            return False
        except Exception as e:
            print(f"Error detecting ESP32: {e}")
            return False
    
    def startDataReading(self):
        """Start reading data from ESP32"""
        try:
            # Open serial connection
            self.serial_connection = serial.Serial(self.esp32_port, 9600, timeout=1)
            # Start timer to read data
            self.data_timer = QTimer(self)
            self.data_timer.timeout.connect(self.readData)
            self.data_timer.start(50)  # Read data every 50ms for smoother graph
        except Exception as e:
            print(f"Error opening serial connection: {e}")
            self.status_label.setVisible(True)  # Show the status label
            self.status_label.setText('Ошибка подключения к устройству')
            self.status_label.setStyleSheet("font-size: 18px; color: red;")
    
    def stopDataReading(self):
        """Stop reading data from ESP32"""
        if hasattr(self, 'data_timer') and self.data_timer.isActive():
            self.data_timer.stop()
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.data_buffer = []
        # Clear the graph
        self.graph_widget.data = []
        self.graph_widget.update()
    
    def readData(self):
        """Read data from ESP32 and display it"""
        try:
            if self.serial_connection and self.serial_connection.is_open:
                # Read all available data
                while self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.readline().decode('utf-8').strip()
                    if data:
                        if data.split('bpm')[0] == '' and data != '':
                            # Extract BPM value from data
                            bpm_part = data.split('bpm')[1]
                            try:
                                self.pulse_value = int(bpm_part)
                                # Update the graph widget with the new pulse value
                                self.graph_widget.pulse_value = self.pulse_value
                                self.graph_widget.update()  # Trigger repaint to show updated pulse value
                            except ValueError:
                                pass
                        elif data.split('Ошибка')[0] == '' and data != '':
                            pass 
                        elif data == 'breath':
                            # Update breath status
                            self.last_breath_status = 'breath'
                            if 'Дыхание' in self.selected_signals:
                                self.breath_label.setText('Есть дыхание')
                                self.breath_label.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
                                self.breath_label.setVisible(True)
                        elif data == 'noBreath':
                            # Update breath status
                            self.last_breath_status = 'noBreath'
                            if 'Дыхание' in self.selected_signals:
                                self.breath_label.setText('Нет дыхания')
                                self.breath_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
                                self.breath_label.setVisible(True)
                        else: 
                            # Try to convert to number if possible
                            try:
                                num_value = float(data)
                                # Only add to buffer and graph if ECG is selected
                                if 'ЭКГ' in self.selected_signals:
                                    self.data_buffer.append(num_value)
                                    # Update graph with new data
                                    self.graph_widget.addData(num_value)
                            except ValueError:
                                # If not a number, ignore for graph
                                pass
                        
                        # Control visibility of graph based on selected signals
                        if 'ЭКГ' in self.selected_signals:
                            self.graph_widget.setVisible(True)
                        else:
                            self.graph_widget.setVisible(False)
                            
                        # Control visibility of breath label based on selected signals
                        # Only show breath label if breathing is selected and we've received breath data
                        if 'Дыхание' in self.selected_signals and self.last_breath_status is not None:
                            self.breath_label.setVisible(True)
                        elif 'Дыхание' in self.selected_signals and self.last_breath_status is None:
                            # Show placeholder text when breathing is selected but no data received yet
                            self.breath_label.setText('Ожидание данных о дыхании...')
                            self.breath_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #666;")
                            self.breath_label.setVisible(True)
                        else:
                            self.breath_label.setVisible(False)
        except Exception as e:
            print(f"Error reading data: {e}")

class GraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.pulse_value = 0  # Store the current pulse value
        self.max_data_points = 500  # Show last 500 data points
        self.setStyleSheet("background-color: white; border: 1px solid #ccc;")
    
    def addData(self, value):
        """Add a new data point to the graph"""
        self.data.append(value)
        # Limit the number of data points
        if len(self.data) > self.max_data_points:
            self.data = self.data[-self.max_data_points:]
        # Trigger a repaint
        self.update()
    
    def paintEvent(self, event):
        """Draw the graph"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        
        # Define margins for axis labels
        margin_left = 50
        margin_bottom = 30
        margin_top = 20
        margin_right = 20
        
        # Calculate graph area
        graph_width = width - margin_left - margin_right
        graph_height = height - margin_top - margin_bottom
        
        # Draw background
        painter.fillRect(0, 0, width, height, QColor(255, 255, 255))
        
        # Draw grid
        painter.setPen(QPen(QColor(220, 220, 220), 1))
        # Horizontal grid lines (5 lines)
        for i in range(6):
            y = margin_top + (graph_height * i // 5)
            painter.drawLine(margin_left, y, margin_left + graph_width, y)
        # Vertical grid lines (10 lines)
        for i in range(11):
            x = margin_left + (graph_width * i // 10)
            painter.drawLine(x, margin_top, x, margin_top + graph_height)
        
        # Draw axis labels
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)
        
        # Draw Y-axis labels
        if len(self.data) > 1:
            min_val = min(self.data)
            max_val = max(self.data)
            range_val = max_val - min_val if max_val != min_val else 1
            
            # Draw min, middle, and max values
            painter.drawText(5, margin_top + graph_height, f"{min_val:.1f}")
            painter.drawText(5, margin_top + graph_height // 2, f"{(min_val + max_val) / 2:.1f}")
            painter.drawText(5, margin_top + 15, f"{max_val:.1f}")
            
            # Draw Y-axis label
            painter.drawText(10, 15, "Амплитуда")
        
        # Draw X-axis label
        painter.drawText(margin_left + graph_width // 2 - 30, height - 5, "Время")
        
        # Draw pulse value in top-right corner
        if self.pulse_value > 0:
            pulse_font = QFont()
            pulse_font.setPointSize(14)
            pulse_font.setBold(True)
            painter.setFont(pulse_font)
            
            # Determine if pulse is normal (60-100 BPM is considered normal)
            is_normal = 60 <= self.pulse_value <= 100
            
            # Set color: black for normal, red for abnormal
            if is_normal:
                painter.setPen(QPen(QColor(0, 0, 0)))  # Black color for normal pulse
            else:
                painter.setPen(QPen(QColor(200, 0, 0)))  # Red color for abnormal pulse
            
            # Display pulse in Russian
            pulse_text = f"Пульс: {self.pulse_value} уд/мин"
            # Position in top-right corner with some padding
            text_width = painter.fontMetrics().width(pulse_text)
            painter.drawText(width - text_width - 10, 30, pulse_text)
        
        # Draw graph only if we have data
        if len(self.data) > 1:
            # Set up pen for graph line
            painter.setPen(QPen(QColor(0, 150, 200), 2))
            
            # Draw the graph line
            points = []
            for i, value in enumerate(self.data):
                # X coordinate: spread data points across the width
                x = margin_left + int(i * graph_width / max(len(self.data) - 1, 1))
                # Y coordinate: map value to height (invert because Y=0 is top)
                y = margin_top + int(graph_height - ((value - min_val) / range_val) * graph_height)
                # Ensure coordinates are within bounds
                x = max(margin_left, min(margin_left + graph_width, x))
                y = max(margin_top, min(margin_top + graph_height, y))
                points.append((x, y))
            
            # Draw connected lines between points
            for i in range(1, len(points)):
                painter.drawLine(points[i-1][0], points[i-1][1], points[i][0], points[i][1])

def main():
    app = QApplication(sys.argv)
    window = USBConnectionWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()