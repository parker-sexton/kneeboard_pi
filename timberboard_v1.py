#!/usr/bin/env python3
"""
Timber Kneeboard Application
A touchscreen application for pilots to use as a digital kneeboard.
Designed for Raspberry Pi Zero W 2 with touchscreen.
"""

import os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Line, Rectangle
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from functools import partial

# Set window properties for the Raspberry Pi
from kivy.config import Config
import os

# Check if running in headless mode
headless = os.environ.get('DISPLAY', '') == '' or 'HEADLESS' in os.environ

# Configure for headless operation if needed
if headless:
    os.environ['KIVY_WINDOW'] = 'egl_rpi'
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'multisamples', '0')
    Config.set('graphics', 'window_state', 'maximized')
    Config.set('graphics', 'allow_screensaver', '0')
else:
    Config.set('graphics', 'fullscreen', 'auto')  # Enable fullscreen mode
    Config.set('graphics', 'orientation', 'portrait')  # Set portrait orientation

# Set fixed aspect ratio (9:16 for portrait mode)
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '854')
Config.set('graphics', 'resizable', '0')

# Window size will be determined by the display when in fullscreen mode

class TimberBoard(FloatLayout):
    """Main layout for the Timber Kneeboard application."""
    
    def __init__(self, **kwargs):
        # Fix: Call super().__init__() with the kwargs
        # The old style super(TimberBoard, self).__init__(**kwargs) works in Python 2
        # but can cause issues in Python 3 if not used correctly
        super().__init__(**kwargs)  # Use the new style super() call
        
        # Add your TimberBoard initialization code here
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 5
        
        # Example: Add a label to the layout
        self.welcome_label = Label(
            text="Welcome to TimberBoard",
            font_size=24,
            pos_hint={'center_x': 0.5, 'center_y': 0.9},
            size_hint=(0.8, 0.1)
        )
        self.add_widget(self.welcome_label)


class TimberApp(App):
    """Main application class for the timber kneeboard."""
    
    def build(self):
        """Build the application UI."""
        # Create the main TimberBoard widget
        TimberScreen = TimberBoard()
        return TimberScreen


if __name__ == "__main__":
    # Import Window early to set properties before app starts
    from kivy.core.window import Window
    
    # Handle headless mode
    if headless:
        # Set environment variables for headless operation
        os.environ['KIVY_GL_BACKEND'] = 'gl'
        os.environ['KIVY_WINDOW'] = 'egl_rpi'
        
        # Import and use Kivy's headless provider if available
        try:
            from kivy.base import EventLoop
            EventLoop.ensure_window()
            # Set portrait mode with 9:16 aspect ratio
            Window.size = (480, 854)
        except Exception as e:
            print(f"Warning: Headless setup encountered an issue: {e}")
            print("Attempting to continue with default configuration...")
    else:
        # For non-headless mode, ensure window size is set correctly
        # Set portrait mode with 9:16 aspect ratio
        Window.size = (480, 854)
    
    # Force the window to update its size and position
    Window.top = 0
    Window.left = 0
    
    TimberApp().run()
