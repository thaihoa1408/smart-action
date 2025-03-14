from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QListWidget, QLabel, 
                            QLineEdit, QComboBox, QSpinBox, QDialog, QFormLayout,
                            QMessageBox, QTabWidget, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QProcess
import sys
import json
from typing import Dict, List

class ActionStepDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Step")
        self.setModal(True)
        
        layout = QFormLayout()
        
        # Step type selection
        self.type_combo = QComboBox()
        self.type_combo.addItems(["open_app", "open_url", "keyboard", "clipboard"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addRow("Type:", self.type_combo)
        
        # Keyboard input type (only visible when keyboard type is selected)
        self.keyboard_type_combo = QComboBox()
        self.keyboard_type_combo.addItems(["text", "key_combination"])
        self.keyboard_type_row = layout.rowCount()
        layout.addRow("Keyboard Input Type:", self.keyboard_type_combo)
        
        # Clipboard action type (only visible when clipboard type is selected)
        self.clipboard_action_combo = QComboBox()
        self.clipboard_action_combo.addItems(["copy", "paste"])
        self.clipboard_action_combo.currentTextChanged.connect(self.on_clipboard_action_changed)
        self.clipboard_action_row = layout.rowCount()
        layout.addRow("Clipboard Action:", self.clipboard_action_combo)
        
        # Value input
        self.value_input = QLineEdit()
        layout.addRow("Value:", self.value_input)
        
        # Delay input
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0, 10)
        self.delay_spin.setSingleStep(0.1)
        self.delay_spin.setDecimals(1)
        self.delay_spin.setValue(0)
        layout.addRow("Delay (seconds):", self.delay_spin)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)
        
        self.setLayout(layout)
        
        # Initialize visibility based on current type
        self.on_type_changed(self.type_combo.currentText())
    
    def on_type_changed(self, text):
        # Show/hide keyboard type option based on selected type
        keyboard_type_label = self.layout().itemAt(self.keyboard_type_row, QFormLayout.ItemRole.LabelRole).widget()
        keyboard_type_field = self.layout().itemAt(self.keyboard_type_row, QFormLayout.ItemRole.FieldRole).widget()
        
        # Show/hide clipboard action option based on selected type
        clipboard_action_label = self.layout().itemAt(self.clipboard_action_row, QFormLayout.ItemRole.LabelRole).widget()
        clipboard_action_field = self.layout().itemAt(self.clipboard_action_row, QFormLayout.ItemRole.FieldRole).widget()
        
        # Hide both by default
        keyboard_type_label.setVisible(False)
        keyboard_type_field.setVisible(False)
        clipboard_action_label.setVisible(False)
        clipboard_action_field.setVisible(False)
        
        # Always re-enable the value input when changing types
        self.value_input.setEnabled(True)
        
        if text == "keyboard":
            keyboard_type_label.setVisible(True)
            keyboard_type_field.setVisible(True)
            
            # Update value field placeholder based on keyboard type
            if self.keyboard_type_combo.currentText() == "text":
                self.value_input.setPlaceholderText("Enter text to type")
            else:
                self.value_input.setPlaceholderText("Enter key combination (e.g. cmd+c)")
        elif text == "clipboard":
            clipboard_action_label.setVisible(True)
            clipboard_action_field.setVisible(True)
            
            # Update value field placeholder based on clipboard action
            self.on_clipboard_action_changed(self.clipboard_action_combo.currentText())
        else:
            # Update placeholder based on action type
            if text == "open_app":
                self.value_input.setPlaceholderText("Enter application name")
            elif text == "open_url":
                self.value_input.setPlaceholderText("Enter URL (e.g. https://example.com)")
    
    def on_clipboard_action_changed(self, action):
        if action == "copy":
            self.value_input.setEnabled(True)
            self.value_input.setPlaceholderText("Enter text to copy (leave empty to copy selected text)")
        else:  # paste
            self.value_input.setEnabled(False)
            self.value_input.setPlaceholderText("No input needed for paste action")
            self.value_input.clear()
    
    def get_step_data(self):
        data = {
            "type": self.type_combo.currentText(),
            "value": self.value_input.text(),
            "delay": self.delay_spin.value()
        }
        
        # Add keyboard_input_type if the type is keyboard
        if self.type_combo.currentText() == "keyboard":
            data["keyboard_input_type"] = self.keyboard_type_combo.currentText()
        
        # Add clipboard_action if the type is clipboard
        elif self.type_combo.currentText() == "clipboard":
            data["clipboard_action"] = self.clipboard_action_combo.currentText()
            
        return data

class SmartActionsUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Actions Manager")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize process controller
        self.process = QProcess()
        self.process.finished.connect(self.on_process_finished)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        
        # Add control buttons at the top
        control_layout = QHBoxLayout()
        self.run_button = QPushButton("Run Smart Actions")
        self.stop_button = QPushButton("Stop Smart Actions")
        self.stop_button.setEnabled(False)
        
        self.run_button.clicked.connect(self.start_smart_actions)
        self.stop_button.clicked.connect(self.stop_smart_actions)
        
        control_layout.addWidget(self.run_button)
        control_layout.addWidget(self.stop_button)
        main_layout.addLayout(control_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create "Your Actions" tab
        self.your_actions_tab = QWidget()
        self.setup_your_actions_tab()
        self.tab_widget.addTab(self.your_actions_tab, "Your Actions")
        
        # Create "Templates" tab
        self.templates_tab = QWidget()
        self.setup_templates_tab()
        self.tab_widget.addTab(self.templates_tab, "Templates")
        
        main_layout.addWidget(self.tab_widget)
        main_widget.setLayout(main_layout)
        
        self.load_actions()
        self.load_templates()
        
        # Auto-start Smart Actions when app launches
        self.start_smart_actions()
    
    def setup_your_actions_tab(self):
        layout = QHBoxLayout()
        
        # Left side - Action List
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        self.action_list = QListWidget()
        self.action_list.currentItemChanged.connect(self.on_action_selected)
        
        action_buttons = QHBoxLayout()
        add_action_btn = QPushButton("Add Action")
        delete_action_btn = QPushButton("Delete Action")
        add_action_btn.clicked.connect(self.add_action)
        delete_action_btn.clicked.connect(self.delete_action)
        
        action_buttons.addWidget(add_action_btn)
        action_buttons.addWidget(delete_action_btn)
        
        left_layout.addWidget(QLabel("Actions:"))
        left_layout.addWidget(self.action_list)
        left_layout.addLayout(action_buttons)
        left_panel.setLayout(left_layout)
        
        # Right side - Action Details
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Action details form
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.shortcut_input = QLineEdit()
        self.description_input = QLineEdit()
        
        # Set minimum width for input fields
        self.name_input.setMinimumWidth(300)
        self.shortcut_input.setMinimumWidth(300)
        self.description_input.setMinimumWidth(300)
        
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Shortcut:", self.shortcut_input)
        form_layout.addRow("Description:", self.description_input)
        
        # Steps list
        self.steps_list = QListWidget()
        self.steps_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.steps_list.itemDoubleClicked.connect(self.edit_step)
        
        # Step buttons
        step_buttons = QHBoxLayout()
        add_step_btn = QPushButton("Add Step")
        edit_step_btn = QPushButton("Edit Step")
        delete_step_btn = QPushButton("Delete Step")
        add_step_btn.clicked.connect(self.add_step)
        edit_step_btn.clicked.connect(self.edit_step)
        delete_step_btn.clicked.connect(self.delete_step)
        
        step_buttons.addWidget(add_step_btn)
        step_buttons.addWidget(edit_step_btn)
        step_buttons.addWidget(delete_step_btn)
        
        # Save button
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        
        right_layout.addLayout(form_layout)
        right_layout.addWidget(QLabel("Steps:"))
        right_layout.addWidget(self.steps_list)
        right_layout.addLayout(step_buttons)
        right_layout.addWidget(save_btn)
        right_panel.setLayout(right_layout)
        
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        self.your_actions_tab.setLayout(layout)
    
    def setup_templates_tab(self):
        layout = QVBoxLayout()
        
        self.templates_list = QListWidget()
        # Set item height to accommodate two lines of text
        self.templates_list.setSpacing(5)
        self.templates_list.setWordWrap(True)
        
        # Add template actions with "Add" buttons
        template_controls = QHBoxLayout()
        add_template_btn = QPushButton("Add Selected Template")
        add_template_btn.clicked.connect(self.add_template)
        
        template_controls.addWidget(add_template_btn)
        
        layout.addWidget(QLabel("Available Templates:"))
        layout.addWidget(self.templates_list)
        layout.addLayout(template_controls)
        
        self.templates_tab.setLayout(layout)
    
    def load_actions(self):
        try:
            with open("smart_actions.json", "r") as f:
                data = json.load(f)
                self.actions = data.get("actions", [])
                
            self.action_list.clear()
            for action in self.actions:
                self.action_list.addItem(action["name"])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading actions: {str(e)}")
            self.actions = []
    
    def save_actions(self):
        try:
            with open("smart_actions.json", "w") as f:
                json.dump({"actions": self.actions}, f, indent=2)
            
            # Restart Smart Actions after saving changes
            if self.process.state() == QProcess.ProcessState.Running:
                self.stop_smart_actions(show_message=False)
            self.start_smart_actions()
            
            QMessageBox.information(self, "Success", "Actions saved and restarted successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving actions: {str(e)}")
    
    def on_action_selected(self, current, previous):
        if current is None:
            return
        
        action = next((a for a in self.actions if a["name"] == current.text()), None)
        if action:
            self.name_input.setText(action["name"])
            self.shortcut_input.setText(action["shortcut"])
            self.description_input.setText(action.get("description", ""))
            
            self.steps_list.clear()
            for step in action["steps"]:
                if step['type'] == "keyboard" and "keyboard_input_type" in step:
                    self.steps_list.addItem(
                        f"{step['type']} ({step['keyboard_input_type']}): {step['value']} (delay: {step['delay']}s)"
                    )
                elif step['type'] == "clipboard" and "clipboard_action" in step:
                    self.steps_list.addItem(
                        f"{step['type']} ({step['clipboard_action']}): {step['value']} (delay: {step['delay']}s)"
                    )
                else:
                    self.steps_list.addItem(f"{step['type']}: {step['value']} (delay: {step['delay']}s)")
    
    def add_action(self):
        new_action = {
            "name": "New Action",
            "shortcut": "ctrl+x",
            "description": "",
            "steps": []
        }
        self.actions.append(new_action)
        self.action_list.addItem(new_action["name"])
    
    def delete_action(self):
        current = self.action_list.currentItem()
        if current:
            row = self.action_list.row(current)
            self.action_list.takeItem(row)
            self.actions.pop(row)
            self.save_actions()
    
    def add_step(self):
        dialog = ActionStepDialog(self)
        if dialog.exec():
            step_data = dialog.get_step_data()
            current = self.action_list.currentItem()
            if current:
                action = next((a for a in self.actions if a["name"] == current.text()), None)
                if action:
                    action["steps"].append(step_data)
                    
                    # Display with keyboard input type if applicable
                    if step_data['type'] == "keyboard" and "keyboard_input_type" in step_data:
                        self.steps_list.addItem(
                            f"{step_data['type']} ({step_data['keyboard_input_type']}): {step_data['value']} (delay: {step_data['delay']}s)"
                        )
                    elif step_data['type'] == "clipboard" and "clipboard_action" in step_data:
                        self.steps_list.addItem(
                            f"{step_data['type']} ({step_data['clipboard_action']}): {step_data['value']} (delay: {step_data['delay']}s)"
                        )
                    else:
                        self.steps_list.addItem(
                            f"{step_data['type']}: {step_data['value']} (delay: {step_data['delay']}s)"
                        )
    
    def delete_step(self):
        current_action = self.action_list.currentItem()
        current_step = self.steps_list.currentRow()
        
        if current_action and current_step >= 0:
            action = next((a for a in self.actions if a["name"] == current_action.text()), None)
            if action:
                action["steps"].pop(current_step)
                self.steps_list.takeItem(current_step)
    
    def edit_step(self):
        current_action = self.action_list.currentItem()
        current_step = self.steps_list.currentRow()
        
        if current_action and current_step >= 0:
            action = next((a for a in self.actions if a["name"] == current_action.text()), None)
            if action and current_step < len(action["steps"]):
                step_data = action["steps"][current_step]
                
                dialog = ActionStepDialog(self)
                
                # Set dialog fields to match the current step data
                dialog.type_combo.setCurrentText(step_data["type"])
                dialog.value_input.setText(step_data["value"])
                dialog.delay_spin.setValue(step_data["delay"])
                
                # Set additional fields if they exist
                if step_data["type"] == "keyboard" and "keyboard_input_type" in step_data:
                    dialog.keyboard_type_combo.setCurrentText(step_data["keyboard_input_type"])
                elif step_data["type"] == "clipboard" and "clipboard_action" in step_data:
                    dialog.clipboard_action_combo.setCurrentText(step_data["clipboard_action"])
                
                if dialog.exec():
                    # Update the step with new data
                    action["steps"][current_step] = dialog.get_step_data()
                    
                    # Update the display
                    updated_step = action["steps"][current_step]
                    if updated_step['type'] == "keyboard" and "keyboard_input_type" in updated_step:
                        self.steps_list.item(current_step).setText(
                            f"{updated_step['type']} ({updated_step['keyboard_input_type']}): {updated_step['value']} (delay: {updated_step['delay']}s)"
                        )
                    elif updated_step['type'] == "clipboard" and "clipboard_action" in updated_step:
                        self.steps_list.item(current_step).setText(
                            f"{updated_step['type']} ({updated_step['clipboard_action']}): {updated_step['value']} (delay: {updated_step['delay']}s)"
                        )
                    else:
                        self.steps_list.item(current_step).setText(
                            f"{updated_step['type']}: {updated_step['value']} (delay: {updated_step['delay']}s)"
                        )
    
    def save_changes(self):
        current = self.action_list.currentItem()
        if current:
            action = next((a for a in self.actions if a["name"] == current.text()), None)
            if action:
                action["name"] = self.name_input.text()
                action["shortcut"] = self.shortcut_input.text()
                action["description"] = self.description_input.text()
                current.setText(action["name"])
                self.save_actions()
    
    def load_templates(self):
        try:
            with open("template_actions.json", "r") as f:
                data = json.load(f)
                self.templates = data.get("actions", [])
                
            self.templates_list.clear()
            for template in self.templates:
                # Create a formatted item with name and description
                name = template["name"]
                description = template.get("description", "No description available")
                display_text = f"{name}\n{description}"
                
                self.templates_list.addItem(display_text)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading templates: {str(e)}")
            self.templates = []
    
    def add_template(self):
        current = self.templates_list.currentItem()
        if current:
            # Extract the template name from the first line of the display text
            display_text = current.text()
            template_name = display_text.split('\n')[0]
            
            template = next((t for t in self.templates if t["name"] == template_name), None)
            if template:
                # Create a copy of the template
                new_action = template.copy()
                new_action["name"] = f"{template['name']} (Copy)"
                # Make sure description is included (if it exists in the template)
                if "description" not in new_action:
                    new_action["description"] = ""
                
                # Add to actions list
                self.actions.append(new_action)
                self.action_list.addItem(new_action["name"])
                self.save_actions()  # This will also restart Smart Actions
                
                QMessageBox.information(self, "Success", "Template added to your actions!")
    
    def start_smart_actions(self):
        try:
            # Don't show message box on auto-start
            if self.process.state() == QProcess.ProcessState.Running:
                return

            self.process.start("python3", ["main.py"])
            self.run_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to start Smart Actions: {str(e)}")
    
    def stop_smart_actions(self, show_message=False):
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.terminate()
            self.process.waitForFinished(3000)  # Wait up to 3 seconds
            if self.process.state() == QProcess.ProcessState.Running:
                self.process.kill()  # Force kill if not terminated
        
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        if show_message:
            QMessageBox.information(self, "Success", "Smart Actions has been stopped!")
    
    def on_process_finished(self):
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def closeEvent(self, event):
        # Ensure process is stopped when closing the application
        if self.process.state() == QProcess.ProcessState.Running:
            self.stop_smart_actions()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = SmartActionsUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 