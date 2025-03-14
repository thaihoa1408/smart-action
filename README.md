# Smart Actions

Smart Actions is a productivity tool that allows you to create custom keyboard shortcuts for automating repetitive tasks. With a user-friendly GUI, you can define sequences of actions that can be triggered with a simple keyboard shortcut.

## Features

- **Custom Keyboard Shortcuts**: Create personalized keyboard combinations to trigger your automated workflows
- **Multiple Action Types**:
  - Open applications
  - Open URLs in your default browser
  - Simulate keyboard input (text or key combinations)
  - Clipboard operations (copy/paste)
- **Action Templates**: Pre-configured templates for common tasks like:
  - AI Translation with ChatGPT
  - Code explanation with ChatGPT
- **User-Friendly Interface**: Easily create, edit, and manage your smart actions
- **Cross-Platform Support**: Works on macOS, Windows, and Linux

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Setup

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/smart-actions-project.git
   cd smart-actions-project
   ```

2. Create and activate a virtual environment (recommended):

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

Run the Smart Actions UI:

```
python smart_actions_ui.py
```

### Creating a Smart Action

1. Click the "Add Action" button
2. Enter a name for your action
3. Define a keyboard shortcut (e.g., `ctrl+shift+t`)
4. Add steps to your action sequence:
   - Select a step type (open app, open URL, keyboard input, clipboard)
   - Configure the step parameters
   - Set delay between steps if needed
5. Click "Save Changes"

### Using Smart Actions

1. Click "Start Smart Actions" in the UI
2. Use your defined keyboard shortcuts to trigger your automated workflows
3. Click "Stop Smart Actions" when you're done

### Using Templates

1. Go to the "Templates" tab
2. Select a template from the list
3. Click "Add to My Actions" to add it to your personal actions
4. Customize as needed

## Action Types

- **Open App**: Launch applications on your system
- **Open URL**: Open websites in your default browser
- **Keyboard**:
  - Type text
  - Send key combinations (e.g., `ctrl+c`, `alt+tab`)
- **Clipboard**:
  - Copy selected text
  - Paste from clipboard

## Configuration Files

- **smart_actions.json**: Stores your personal actions
- **template_actions.json**: Contains pre-configured action templates

## Example Workflows

### AI Translation

1. Select text in any application
2. Press `ctrl+shift+t`
3. The text is copied, ChatGPT is opened, and the text is sent with a translation prompt

### Code Explanation

1. Select code in your editor
2. Press `ctrl+shift+e`
3. The code is copied, ChatGPT is opened, and the code is sent with an explanation prompt

## Troubleshooting

- **Keyboard shortcuts not working**: Ensure the Smart Actions service is running by clicking "Start Smart Actions"
- **Applications not opening**: Verify the application name/path is correct
- **Delays too short/long**: Adjust the delay values in your action steps
