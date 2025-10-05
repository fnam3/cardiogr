import unittest
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from main import SignalRegistrationApp

class TestSignalRegistrationApp(unittest.TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.window = SignalRegistrationApp()
    
    def test_window_title(self):
        """Test that the window has the correct title"""
        self.assertEqual(self.window.windowTitle(), 'Регистрация сигналов')
    
    def test_instruction_label(self):
        """Test that the instruction label exists and has correct text"""
        # Find the label with the instruction text
        labels = self.window.findChildren(QLabel)
        instruction_labels = [label for label in labels if label.text() == 'выберите, какой сигнал регистрировать:']
        self.assertEqual(len(instruction_labels), 1)
    
    def test_buttons_exist(self):
        """Test that all four buttons exist"""
        buttons = self.window.findChildren(QPushButton)
        button_texts = [button.text() for button in buttons]
        
        self.assertIn('ЭКГ', button_texts)
        self.assertIn('ЭМГ', button_texts)
        self.assertIn('ФПГ', button_texts)
        self.assertIn('Дыхание', button_texts)
        self.assertEqual(len(buttons), 4)
    
    def tearDown(self):
        self.window.close()

if __name__ == '__main__':
    unittest.main()