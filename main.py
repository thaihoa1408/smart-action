import json
import os
import subprocess
import platform
from typing import Dict, List
import time
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

class SmartActionManager:
    def __init__(self):
        self.actions: Dict[str, List[dict]] = {}
        self.current_keys = set()
        self.load_actions()
        self.listener = None
        self.action_executed = False

    def load_actions(self):
        try:
          
               with open("smart_actions.json", "r") as f:
                    config_data = json.load(f)
                    print(config_data)
                    # Convert the JSON structure to the format expected by the application
                    self.actions = {}
                    for action in config_data.get("actions", []):
                        shortcut = action.get("shortcut")
                        steps = action.get("steps", [])
                        if shortcut and steps:
                            self.actions[shortcut] = steps
        
        except Exception as e:
            print(f"Error loading actions: {e}")
            self.actions = {}

    def on_press(self, key):
        try:
            if self.action_executed:
                return

            # Normalize the key before adding to set
            if isinstance(key, KeyCode):
                self.current_keys.add(key.char.lower())
            else:
                self.current_keys.add(key)

            print(f"Current keys held: {self.current_keys}")
            
            # Check for any registered key combinations
            for key_combo in self.actions.keys():
                # Split and normalize the key combination
                parts = key_combo.lower().split('+')
                
                # Check modifiers and regular keys separately
                modifiers_required = set(part for part in parts if part in {'ctrl', 'cmd', 'alt', 'shift'})
                regular_keys_required = set(part for part in parts if part not in {'ctrl', 'cmd', 'alt', 'shift'})
                
                # Get currently pressed modifiers
                current_modifiers = set()
                if Key.ctrl_l in self.current_keys or Key.ctrl_r in self.current_keys:
                    current_modifiers.add('ctrl')
                if Key.cmd_l in self.current_keys or Key.cmd_r in self.current_keys:
                    current_modifiers.add('cmd')
                if Key.alt_l in self.current_keys or Key.alt_r in self.current_keys:
                    current_modifiers.add('alt')
                if Key.shift_l in self.current_keys or Key.shift_r in self.current_keys:
                    current_modifiers.add('shift')
                
                # Get currently pressed regular keys
                current_regular_keys = {k.char.lower() if isinstance(k, KeyCode) else k 
                                     for k in self.current_keys 
                                     if isinstance(k, KeyCode) or k not in {Key.ctrl_l, Key.ctrl_r, 
                                                                          Key.cmd_l, Key.cmd_r,
                                                                          Key.alt_l, Key.alt_r,
                                                                          Key.shift_l, Key.shift_r}}

                # Check if both modifiers and regular keys match exactly
                if (modifiers_required == current_modifiers and 
                    regular_keys_required == current_regular_keys):
                    print(f"Detected {key_combo} combination!")
                    self.action_executed = True
                    self.execute_action(key_combo)
                    break

        except Exception as e:
            print(f"Error in on_press: {e}")

    def on_release(self, key):
        try:
            if hasattr(key, 'char'):
                self.current_keys.discard(key.char)
            else:
                self.current_keys.discard(key)
            
            if not self.current_keys:
                self.action_executed = False
        except Exception as e:
            print(f"Error in on_release: {e}")

    def start_listening(self):
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()

    def execute_action(self, key_combo: str):
        if key_combo not in self.actions:
            return
        
        for action in self.actions[key_combo]:
            action_type = action.get("type")
            value = action.get("value")
            
            # We no longer need to check for delay here since we have a dedicated delay action type
            # The delay field is kept for backward compatibility but not used

            if action_type == "open_app":
                if platform.system() == "Darwin":  # macOS
                    # Simple open command that either opens the app or brings it to front
                    subprocess.run(["open", "-a", value])
                    # Wait for the app to fully launch
                    app_name = value.split("/")[-1].split(".app")[0] if ".app" in value else value
                    self._wait_for_app_launch(app_name)
                elif platform.system() == "Windows":
                    # For Windows, you might want to add similar logic using tasklist
                    process = subprocess.Popen([value])
                    # Wait for the process to initialize
                    self._wait_for_process(process.pid)
            elif action_type == "open_url":
                # Open URL in default web browser
                if platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", value])
                elif platform.system() == "Windows":
                    import webbrowser
                    webbrowser.open(value)
                else:  # Linux and other platforms
                    import webbrowser
                    webbrowser.open(value)
            elif action_type == "delay":
                # Simply wait for the specified number of seconds
                try:
                    delay_seconds = float(value)
                    print(f"Delaying for {delay_seconds} seconds...")
                    time.sleep(delay_seconds)
                    print(f"Delay complete")
                except ValueError:
                    print(f"Invalid delay value: {value}")
            elif action_type == "keyboard":
                kb = keyboard.Controller()
                keyboard_input_type = action.get("keyboard_input_type", "text")  # Default to text for backward compatibility
                value = action.get("value", "")
                
                if keyboard_input_type == "text":
                    # Use clipboard for instant text input instead of typing
                    import pyperclip
                    # Save current clipboard content
                    previous_clipboard = pyperclip.paste()
                    # Copy new text to clipboard
                    pyperclip.copy(value)
                    # Paste the text
                    if platform.system() == "Darwin":  # macOS
                        with kb.pressed(Key.cmd):
                            kb.press('v')
                            kb.release('v')
                    else:  # Windows/Linux
                        with kb.pressed(Key.ctrl):
                            kb.press('v')
                            kb.release('v')
                    # Optional: restore previous clipboard content
                    time.sleep(0.1)  # Small delay to ensure paste completes
                    pyperclip.copy(previous_clipboard)
                else:  # key_combination
                    # Handle various key combinations
                    if value == "enter":
                        kb.press(Key.enter)
                        kb.release(Key.enter)
                    elif value == "tab":
                        kb.press(Key.tab)
                        kb.release(Key.tab)
                    elif value == "space":
                        kb.press(Key.space)
                        kb.release(Key.space)
                    elif value == "backspace":
                        kb.press(Key.backspace)
                        kb.release(Key.backspace)
                    elif value == "esc" or value == "escape":
                        kb.press(Key.esc)
                        kb.release(Key.esc)
                    elif "+" in value:
                        # Handle combinations like ctrl+c, cmd+v, alt+tab, etc.
                        parts = value.lower().split("+")
                        modifiers = []
                        
                        # Map modifier names to Key objects
                        for part in parts[:-1]:  # All parts except the last one are modifiers
                            if part == "ctrl":
                                modifiers.append(Key.ctrl)
                            elif part == "cmd" or part == "command":
                                modifiers.append(Key.cmd)
                            elif part == "alt":
                                modifiers.append(Key.alt)
                            elif part == "shift":
                                modifiers.append(Key.shift)
                            elif part == "option":  # macOS alternative name for alt
                                modifiers.append(Key.alt)
                        
                        # The last part is the key to press with modifiers
                        key = parts[-1]
                        
                        # Handle function keys
                        if key.startswith("f") and key[1:].isdigit():
                            # Handle F1-F12 keys
                            f_num = int(key[1:])
                            if 1 <= f_num <= 12:
                                key_obj = getattr(Key, f"f{f_num}")
                            else:
                                key_obj = key
                        # Handle special keys
                        elif key in ["up", "down", "left", "right", "home", "end", "page_up", "page_down", "insert", "delete", 
                                    "enter", "tab", "space", "backspace", "esc", "escape"]:
                            key_obj = getattr(Key, key)
                        # Regular character key
                        else:
                            key_obj = key
                        
                        # Press all modifiers, then the key
                        pressed_keys = []
                        try:
                            for modifier in modifiers:
                                kb.press(modifier)
                                pressed_keys.append(modifier)
                            
                            if isinstance(key_obj, str) and len(key_obj) == 1:
                                kb.press(key_obj)
                                kb.release(key_obj)
                            else:
                                kb.press(key_obj)
                                kb.release(key_obj)
                        finally:
                            # Always release modifiers in reverse order
                            for modifier in reversed(pressed_keys):
                                kb.release(modifier)
                    else:
                        # Single key press for special keys
                        try:
                            # Try to find the key as a special key
                            key_obj = getattr(Key, value.lower(), None)
                            if key_obj:
                                kb.press(key_obj)
                                kb.release(key_obj)
                            else:
                                # If not a special key, just type it
                                kb.type(value)
                        except (AttributeError, TypeError):
                            # Fallback to typing the value as is
                            kb.type(value)
            elif action_type == "clipboard":
                clipboard_action = action.get("clipboard_action", "copy")
                value = action.get("value", "")
                
                if clipboard_action == "copy":
                    # Copy the provided text to clipboard
                    import pyperclip
                    
                    if value:
                        # If value is provided, copy it directly
                        pyperclip.copy(value)
                        print(f"Copied to clipboard: {value}")
                    else:
                        # If no value is provided, try to copy currently selected text
                        kb = keyboard.Controller()
                        
                        # Simulate Ctrl+C or Cmd+C to copy selected text
                        if platform.system() == "Darwin":  # macOS
                            with kb.pressed(Key.cmd):
                                kb.press('c')
                                kb.release('c')
                                print("Copied to clipboard")
                        else:  # Windows/Linux
                            with kb.pressed(Key.ctrl):
                                kb.press('c')
                                kb.release('c')
                        
                        # Give a small delay for the copy operation to complete
                        time.sleep(0.1)
                        print("Copied selected text to clipboard")
                        
                elif clipboard_action == "paste":
                    # Paste from clipboard
                    kb = keyboard.Controller()
                    if platform.system() == "Darwin":  # macOS
                        with kb.pressed(Key.cmd):
                            kb.press('v')
                            kb.release('v')
                    else:  # Windows/Linux
                        with kb.pressed(Key.ctrl):
                            kb.press('v')
                            kb.release('v')

    def _wait_for_app_launch(self, app_name, timeout=10):
        """Wait for an application to fully launch on macOS."""
        print(f"Waiting for {app_name} to launch...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check if the app is running and responding
                if platform.system() == "Darwin":  # macOS
                    result = subprocess.run(
                        ["osascript", "-e", f'tell application "System Events" to (name of processes) contains "{app_name}"'],
                        capture_output=True, text=True
                    )
                    if "true" in result.stdout.lower():
                        # Give the app a moment to fully initialize its UI
                        time.sleep(0.5)
                        print(f"{app_name} is now running")
                        return True
                else:  # Linux
                    result = subprocess.run(
                        ["pgrep", "-f", app_name],
                        capture_output=True, text=True
                    )
                    if result.stdout.strip():
                        time.sleep(0.5)
                        print(f"{app_name} is now running")
                        return True
                
                time.sleep(0.2)  # Short delay between checks
            except Exception as e:
                print(f"Error checking app status: {e}")
        
        print(f"Timed out waiting for {app_name} to launch")
        return False

    def _wait_for_process(self, pid, timeout=10):
        """Wait for a process to fully initialize on Windows."""
        print(f"Waiting for process {pid} to initialize...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if platform.system() == "Windows":
                    # Check if the process is responding
                    result = subprocess.run(
                        ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                        capture_output=True, text=True
                    )
                    if str(pid) in result.stdout:
                        # Give the app a moment to fully initialize its UI
                        time.sleep(1.0)
                        print(f"Process {pid} is now running")
                        return True
                
                time.sleep(0.2)  # Short delay between checks
            except Exception as e:
                print(f"Error checking process status: {e}")
        
        print(f"Timed out waiting for process {pid} to initialize")
        return False

def main():
    if os.geteuid() != 0 and platform.system() == "Darwin":
        print("Warning: This script may require sudo privileges on macOS for keyboard events.")
        print("Try running with: sudo python main.py")
    
    manager = SmartActionManager()

    # No need to define actions here anymore, they're loaded from the JSON file

    print("Smart Actions is running... Press Ctrl+C to exit")
    manager.start_listening()
    
    # Keep the program running
    try:
        keyboard.Listener.join(manager.listener)
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
