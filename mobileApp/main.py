import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import os
# Import the instructions window
from instructions import InstructionsWindow
# Import the USB connection window directly
from usb import USBConnectionWindow

class SignalRegistrationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_signals = set()  # Use a set to track selected signals
        self.buttons = {}  # Store button references
        self.info_buttons = {}  # Store info button references
        self.initUI()
    
    def initUI(self):
        # Set window properties
        self.setWindowTitle('Регистрация сигналов')
        self.setGeometry(100, 100, 600, 400)
        # Fix the window size to prevent resizing issues
        self.setFixedSize(600, 400)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout with reduced spacing
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)  # Reduced spacing between elements
        main_layout.setContentsMargins(20, 20, 20, 20)  # Reduced margins
        central_widget.setLayout(main_layout)
        
        # Create and add the logo header
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Try to load the SVG logo
        svg_path = 'imgs/neurotech.svg'
        # Also check for PNG version as fallback
        png_path = 'imgs/neurotech.png'
        
        pixmap = None
        if os.path.exists(svg_path):
            # Try to load SVG directly (may work depending on Qt installation)
            pixmap = QPixmap(svg_path)
            if pixmap.isNull():
                # If SVG loading failed, use text as fallback
                logo_label.setText("NeuroTech")
                logo_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #2E86AB; padding: 10px;")
        elif os.path.exists(png_path):
            # Try to load PNG version
            pixmap = QPixmap(png_path)
            
        # If we have a valid pixmap, set it to the label
        if pixmap and not pixmap.isNull():
            # Scale the logo to fit nicely
            pixmap = pixmap.scaledToHeight(80, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        elif not pixmap:
            # Fallback text if no image file found
            logo_label.setText("NeuroTech")
            logo_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #2E86AB; padding: 10px;")
        
        main_layout.addWidget(logo_label)
        
        # Create and add the instruction label with reduced spacing
        instruction_label = QLabel('выберите, какие сигналы регистрировать:')
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setStyleSheet("font-size: 20px; margin: 5px; padding: 10px;")
        main_layout.addWidget(instruction_label)
        
        # Add stretch to center content vertically
        main_layout.addStretch(1)
        
        # Create buttons layout with reduced spacing
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)  # Reduced spacing between buttons
        buttons_layout.setContentsMargins(20, 15, 20, 15)  # Reduced margins
        
        # Create buttons without EMG
        self.create_signal_button('ЭКГ', buttons_layout)
        self.create_signal_button('Дыхание', buttons_layout)
        # self.create_signal_button('Температура', buttons_layout)
        
        # Add buttons layout to main layout
        main_layout.addLayout(buttons_layout)
        
        # Add another stretch to push continue button to bottom
        main_layout.addStretch(1)
        
        # Create continue button
        self.continue_button = QPushButton('Продолжить')
        self.continue_button.setStyleSheet("""
            font-size: 16px; 
            padding: 15px; 
            background-color: #2E86AB; 
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: bold;
        """)
        self.continue_button.clicked.connect(self.onContinueClicked)
        self.continue_button.setEnabled(False)  # Disabled by default until at least one signal is selected
        main_layout.addWidget(self.continue_button)
    
    def create_signal_button(self, signal_name, layout):
        """Create a signal button with toggle functionality and info button"""
        # Create a container widget for the button and info icon
        container = QWidget()
        container_layout = QGridLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Create main signal button
        button = QPushButton(signal_name)
        button.setStyleSheet("""
            font-size: 16px; 
            padding: 15px; 
            background-color: #f0f0f0; 
            border: 2px solid #cccccc;
            border-radius: 10px;
            font-weight: bold;
        """)
        button.setCheckable(True)  # Make button toggleable
        button.clicked.connect(lambda checked, name=signal_name: self.onSignalButtonClicked(name))
        
        # Create info button with text "ⓘ" to represent information icon
        info_button = QPushButton("ⓘ")
        info_button.setStyleSheet("""
            font-size: 12px; 
            padding: 2px; 
            background-color: transparent; 
            border: none;
            border-radius: 8px;
            font-weight: bold;
            min-width: 20px;
            max-width: 20px;
            min-height: 20px;
            max-height: 20px;
        """)
        info_button.clicked.connect(lambda checked, name=signal_name: self.showSignalInfo(name))
        
        # Add buttons to container layout
        container_layout.addWidget(button, 0, 0)
        container_layout.addWidget(info_button, 0, 0, Qt.AlignTop | Qt.AlignRight)
        
        # Store button references
        self.buttons[signal_name] = button
        self.info_buttons[signal_name] = info_button
        
        # Add container to main layout
        layout.addWidget(container)
    
    def showSignalInfo(self, signal_name):
        """Show information dialog for the selected signal using instructions.py"""
        self.instructions_window = InstructionsWindow(signal_type=signal_name, main_window=self)
        self.instructions_window.show()
        # Hide the main window
        self.hide()
    
    def onSignalButtonClicked(self, signal_name):
        """Handle signal button clicks"""
        button = self.buttons[signal_name]
        
        # Toggle selection
        if signal_name in self.selected_signals:
            # Deselect the signal
            self.selected_signals.remove(signal_name)
            button.setStyleSheet("""
                font-size: 16px; 
                padding: 15px; 
                background-color: #f0f0f0; 
                border: 2px solid #cccccc;
                border-radius: 10px;
                font-weight: bold;
            """)
        else:
            # Select the signal
            self.selected_signals.add(signal_name)
            button.setStyleSheet("""
                font-size: 16px; 
                padding: 15px; 
                background-color: #2E86AB;  /* Blue color matching logo */
                border: 2px solid #2E86AB;
                border-radius: 10px;
                font-weight: bold;
                color: white;
            """)
        
        # Update continue button state
        self.update_continue_button_state()
    
    def update_continue_button_state(self):
        """Enable/disable continue button based on selection"""
        if self.selected_signals:
            self.continue_button.setEnabled(True)
        else:
            self.continue_button.setEnabled(False)
    
    def onContinueClicked(self):
        """Handle continue button click - open USB connection directly"""
        if self.selected_signals:
            # Open the USB connection window directly (skip connection selection)
            self.usb_window = USBConnectionWindow(main_window=self, selected_signals=self.selected_signals)
            self.usb_window.show()
            # Hide the main window
            self.hide()
    
    def showEvent(self, event):
        """Override showEvent to ensure proper cleanup when window is shown again"""
        super().showEvent(event)

def main():
    app = QApplication(sys.argv)
    window = SignalRegistrationApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()