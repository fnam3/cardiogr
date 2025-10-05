import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import os
# Import the USB connection window directly
from usb import USBConnectionWindow

class InstructionsWindow(QMainWindow):
    def __init__(self, signal_type, main_window=None):
        super().__init__()
        self.signal_type = signal_type
        self.main_window = main_window
        self.initUI()
    
    def initUI(self):
        # Set window properties
        self.setWindowTitle(f'Инструкции для {self.signal_type}')
        
        # Set different window sizes based on signal type
        if self.signal_type == 'ЭКГ':
            # Larger window for ECG to accommodate the image
            self.setGeometry(150, 150, 500, 500)
            # Fix the window size to prevent resizing issues
            self.setFixedSize(500, 570)
        else:
            # Standard window size for other signal types
            self.setGeometry(150, 150, 500, 400)
            # Fix the window size to prevent resizing issues
            self.setFixedSize(500, 400)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        central_widget.setLayout(main_layout)
        
        # Special handling for ECG (ЭКГ)
        if self.signal_type == 'ЭКГ':
            self.setupECGLayout(main_layout)
        else:
            # Create and add title label for other signal types
            title_label = QLabel(f'Инструкции для регистрации сигнала')
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
            main_layout.addWidget(title_label)
            
            # Create and add instruction text based on signal type
            instruction_text = self.get_instruction_text()
            instruction_label = QLabel(instruction_text)
            instruction_label.setWordWrap(True)
            instruction_label.setAlignment(Qt.AlignLeft)
            instruction_label.setStyleSheet("font-size: 16px; line-height: 1.5;")
            main_layout.addWidget(instruction_label)
            
            # Add stretch to push button to bottom
            main_layout.addStretch()
        
        # Create back button
        back_button = QPushButton('Назад')
        back_button.setStyleSheet("""
            font-size: 16px; 
            padding: 10px; 
            background-color: #f0f0f0; 
            border: 2px solid #cccccc;
            border-radius: 8px;
            font-weight: bold;
        """)
        back_button.clicked.connect(self.goBack)
        main_layout.addWidget(back_button)
    
    def setupECGLayout(self, main_layout):
        """Setup special layout for ECG instructions"""
        # Create and add the electrode connection instruction label
        instruction_label = QLabel('подключите электроды согласно инструкции')
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        main_layout.addWidget(instruction_label)
        
        # Create and add the ECG image
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        
        # Try to load the ECG image
        image_path = 'imgs/EKG.PNG'
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale the image to fit nicely
                pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
            else:
                # Fallback text if image cannot be loaded
                image_label.setText("Изображение ЭКГ")
                image_label.setStyleSheet("font-size: 16px; color: #666;")
        else:
            # Fallback text if image file not found
            image_label.setText("Изображение ЭКГ не найдено")
            image_label.setStyleSheet("font-size: 16px; color: #666;")
        
        main_layout.addWidget(image_label)
        
        # Add stretch to push buttons to bottom
        main_layout.addStretch()
    
    def onConnectedClicked(self):
        """Handle when the 'подключил' button is clicked"""
        # This method is no longer used since we removed the "подключил" button
        pass
    
    def get_instruction_text(self):
        """Return instruction text based on the selected signal type"""
        instructions = {
            'ФПГ': (
                "Инструкции по регистрации фотоплетизмограммы (ФПГ):\n\n"
                "1. Подготовьте фотоэлектрический plethysmograph\n"
                "2. Убедитесь в наличии инфракрасного светодиода и фотодетектора\n"
                "3. Поместите датчик на участок тела с хорошей перфузией\n"
                "4. Обычно используются пальцы рук или мочка уха\n"
                "5. Зафиксируйте датчик с помощью ремешка или зажима\n"
                "6. Убедитесь в плотном контакте с кожей\n"
                "7. Минимизируйте движение пациента во время записи\n"
                "8. Наблюдайте за пульсовым сигналом на экране\n"
                "9. Запишите данные в течение рекомендованного времени"
            ),
            'Дыхание': (
                "Прикрепите к носу датчик дыхания"
            )
        }
        
        return instructions.get(self.signal_type, "Инструкции для данного типа сигнала отсутствуют.")
    
    def goBack(self):
        """Close this window and return to the main window"""
        if self.main_window:
            self.main_window.show()
        self.close()

def main():
    app = QApplication(sys.argv)
    # For testing purposes, we'll show an example with ECG
    window = InstructionsWindow('ЭКГ')
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()