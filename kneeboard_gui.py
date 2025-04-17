#!/usr/bin/env python3
"""
Pilot Kneeboard Application
A touchscreen application for pilots to use as a digital kneeboard.
Designed for Raspberry Pi Zero W 2 with touchscreen.
"""

import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Line
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import ListProperty
from kivy.clock import Clock
from functools import partial

# Set window size for development (can be adjusted for the actual device)
Window.size = (800, 480)  # Common resolution for 7" touchscreens

class SquawkCodeInput(BoxLayout):
    """Widget for entering a 4-digit squawk code using a pinpad."""
    
    def __init__(self, **kwargs):
        super(SquawkCodeInput, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 10
        
        # Display for the squawk code
        self.display_layout = BoxLayout(size_hint=(1, 0.2))
        self.squawk_display = Label(
            text="1200",  # Default VFR squawk code
            font_size=40,
            size_hint=(0.8, 1),
            halign='center',
            valign='middle'
        )
        self.display_layout.add_widget(self.squawk_display)
        
        # Clear button
        self.clear_btn = Button(
            text="Clear",
            size_hint=(0.2, 1),
            background_color=(1, 0.5, 0.5, 1)
        )
        self.clear_btn.bind(on_press=self.clear_squawk)
        self.display_layout.add_widget(self.clear_btn)
        
        self.add_widget(self.display_layout)
        
        # Pinpad layout
        self.pinpad = GridLayout(cols=3, spacing=5, size_hint=(1, 0.8))
        
        # Add number buttons (0-9)
        for i in range(1, 10):
            btn = Button(text=str(i), font_size=30)
            btn.bind(on_press=partial(self.update_squawk, str(i)))
            self.pinpad.add_widget(btn)
        
        # Add 0 button
        zero_btn = Button(text="0", font_size=30)
        zero_btn.bind(on_press=partial(self.update_squawk, "0"))
        self.pinpad.add_widget(zero_btn)
        
        # Add common squawk codes
        vfr_btn = Button(text="VFR\n1200", font_size=20)
        vfr_btn.bind(on_press=partial(self.set_squawk, "1200"))
        self.pinpad.add_widget(vfr_btn)
        
        emergency_btn = Button(text="EMER\n7700", font_size=20, background_color=(1, 0, 0, 1))
        emergency_btn.bind(on_press=partial(self.set_squawk, "7700"))
        self.pinpad.add_widget(emergency_btn)
        
        self.add_widget(self.pinpad)
        
        # Current position in the squawk code (0-3)
        self.current_pos = 0
        self.squawk_code = "1200"
    
    def update_squawk(self, digit, instance):
        """Update the squawk code with the pressed digit."""
        if self.current_pos < 4:
            # Replace the digit at the current position
            self.squawk_code = self.squawk_code[:self.current_pos] + digit + self.squawk_code[self.current_pos+1:]
            self.current_pos = (self.current_pos + 1) % 4
            self.squawk_display.text = self.squawk_code
    
    def set_squawk(self, code, instance):
        """Set a predefined squawk code."""
        self.squawk_code = code
        self.current_pos = 0
        self.squawk_display.text = self.squawk_code
    
    def clear_squawk(self, instance):
        """Clear the squawk code to 0000."""
        self.squawk_code = "0000"
        self.current_pos = 0
        self.squawk_display.text = self.squawk_code


class DrawingCanvas(Widget):
    """Canvas widget for drawing/taking notes with touch."""
    
    line_points = ListProperty([])
    
    def __init__(self, **kwargs):
        super(DrawingCanvas, self).__init__(**kwargs)
        self.lines = []
        self.current_line = None
    
    def on_touch_down(self, touch):
        """Handle touch down event to start a new line."""
        if self.collide_point(touch.x, touch.y):
            touch.grab(self)
            self.current_line = []
            self.current_line.extend([touch.x, touch.y])
            with self.canvas:
                Color(0, 0, 0)  # Black color for drawing
                self.line = Line(points=[touch.x, touch.y, touch.x + 1, touch.y + 1], width=2)
            return True
        return super(DrawingCanvas, self).on_touch_down(touch)
    
    def on_touch_move(self, touch):
        """Handle touch move event to continue the current line."""
        if touch.grab_current is self:
            self.current_line.extend([touch.x, touch.y])
            self.line.points = self.current_line
            return True
        return super(DrawingCanvas, self).on_touch_move(touch)
    
    def on_touch_up(self, touch):
        """Handle touch up event to complete the current line."""
        if touch.grab_current is self:
            touch.ungrab(self)
            self.lines.append(self.current_line)
            return True
        return super(DrawingCanvas, self).on_touch_up(touch)
    
    def clear_canvas(self):
        """Clear all drawings from the canvas."""
        self.canvas.clear()
        self.lines = []
        self.current_line = None


class NotepadTab(BoxLayout):
    """Tab for the notepad functionality."""
    
    def __init__(self, **kwargs):
        super(NotepadTab, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        
        # Controls for the notepad
        self.controls = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        self.clear_btn = Button(text="Clear Notepad", size_hint=(0.3, 1))
        self.clear_btn.bind(on_press=self.clear_notepad)
        self.controls.add_widget(self.clear_btn)
        
        self.add_widget(self.controls)
        
        # Drawing canvas
        self.drawing_canvas = DrawingCanvas(size_hint=(1, 0.9))
        self.add_widget(self.drawing_canvas)
    
    def clear_notepad(self, instance):
        """Clear the notepad canvas."""
        self.drawing_canvas.clear_canvas()


class PiperArcherReference(ScrollView):
    """Reference information for the Piper Archer aircraft."""
    
    def __init__(self, **kwargs):
        super(PiperArcherReference, self).__init__(**kwargs)
        
        # Main layout for the reference content
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        
        # Add reference sections
        self.add_section("Piper Archer (PA-28-181) Specifications", [
            "Engine: Lycoming O-360-A4M, 180 HP",
            "Fuel Capacity: 48 gallons (usable)",
            "Empty Weight: ~1,550 lbs (varies)",
            "Max Takeoff Weight: 2,550 lbs",
            "Useful Load: ~1,000 lbs (varies)",
            "Cruise Speed: 128 KTAS @ 75% power",
            "Range: ~440 nm with 45 min reserve",
            "Service Ceiling: 14,100 ft",
            "Stall Speed (flaps down): 55 KIAS",
            "Stall Speed (flaps up): 64 KIAS"
        ])
        
        self.add_section("V-Speeds", [
            "Vne (Never Exceed): 154 KIAS",
            "Vno (Max Structural Cruising): 125 KIAS",
            "Va (Maneuvering, at 2,550 lbs): 113 KIAS",
            "Vfe (Max Flap Extended): 102 KIAS",
            "Vx (Best Angle of Climb): 64 KIAS",
            "Vy (Best Rate of Climb): 76 KIAS",
            "Vso (Stall, Landing Config): 55 KIAS",
            "Vs1 (Stall, Clean): 64 KIAS"
        ])
        
        self.add_section("Normal Procedures - Takeoff", [
            "1. Flaps - Set (0° to 25°)",
            "2. Throttle - Full forward",
            "3. Rotate - 60-65 KIAS",
            "4. Climb - 76 KIAS (best rate)"
        ])
        
        self.add_section("Normal Procedures - Landing", [
            "1. Airspeed - 75-85 KIAS on final",
            "2. Flaps - As required (0° to 40°)",
            "3. Throttle - As required",
            "4. Touchdown - Main wheels first"
        ])
        
        self.add_section("Emergency Procedures", [
            "Engine Failure During Takeoff (before rotation):",
            "1. Throttle - Idle",
            "2. Brakes - Apply",
            "3. Mixture - Idle cut-off",
            "4. Ignition - OFF",
            "5. Master Switch - OFF",
            "",
            "Engine Failure During Flight:",
            "1. Airspeed - 76 KIAS (best glide)",
            "2. Landing Site - Select",
            "3. Mixture - Rich",
            "4. Fuel Pump - ON",
            "5. Fuel Selector - Switch tanks",
            "6. Ignition - Check ON",
            "7. Primer - Check locked"
        ])
        
        self.add_section("Radio Frequencies", [
            "Emergency: 121.5 MHz",
            "ATIS: 108.0 - 117.95 MHz",
            "Ground: 121.6 - 121.9 MHz",
            "Tower: 118.0 - 121.3 MHz",
            "Approach/Departure: 118.0 - 124.0 MHz",
            "CTAF: 122.7, 122.8, 122.9, 123.0 MHz"
        ])
        
        self.add_widget(self.layout)
    
    def add_section(self, title, items):
        """Add a section of reference information."""
        # Section title
        title_label = Label(
            text=title,
            font_size=20,
            bold=True,
            halign='left',
            size_hint_y=None,
            height=40,
            text_size=(self.width, None)
        )
        self.layout.add_widget(title_label)
        
        # Section content
        content = "\n".join(items)
        content_label = Label(
            text=content,
            font_size=16,
            halign='left',
            valign='top',
            size_hint_y=None,
            text_size=(self.width, None)
        )
        content_label.bind(texture_size=lambda instance, size: setattr(instance, 'height', size[1]))
        self.layout.add_widget(content_label)


class KneeboardApp(App):
    """Main application class for the pilot kneeboard."""
    
    def build(self):
        """Build the application UI."""
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical')
        
        # Header with title
        self.header = BoxLayout(size_hint=(1, 0.1), padding=10)
        self.title_label = Label(
            text="Pilot Kneeboard",
            font_size=24,
            bold=True,
            size_hint=(0.7, 1)
        )
        self.header.add_widget(self.title_label)
        
        # Add a clock display
        self.clock_label = Label(
            text="00:00:00",
            font_size=24,
            size_hint=(0.3, 1)
        )
        self.header.add_widget(self.clock_label)
        Clock.schedule_interval(self.update_clock, 1)
        
        self.main_layout.add_widget(self.header)
        
        # Tabbed panel for different sections
        self.tabs = TabbedPanel(do_default_tab=False, size_hint=(1, 0.9))
        
        # Squawk code tab
        self.squawk_tab = TabbedPanelItem(text="Squawk")
        self.squawk_input = SquawkCodeInput()
        self.squawk_tab.add_widget(self.squawk_input)
        self.tabs.add_widget(self.squawk_tab)
        
        # Reference tab
        self.reference_tab = TabbedPanelItem(text="Reference")
        self.reference_content = PiperArcherReference()
        self.reference_tab.add_widget(self.reference_content)
        self.tabs.add_widget(self.reference_tab)
        
        # Notepad tab
        self.notepad_tab = TabbedPanelItem(text="Notepad")
        self.notepad = NotepadTab()
        self.notepad_tab.add_widget(self.notepad)
        self.tabs.add_widget(self.notepad_tab)
        
        # Set default tab
        self.tabs.default_tab = self.squawk_tab
        
        self.main_layout.add_widget(self.tabs)
        
        return self.main_layout
    
    def update_clock(self, dt):
        """Update the clock display."""
        from datetime import datetime
        now = datetime.now()
        self.clock_label.text = now.strftime("%H:%M:%S")


if __name__ == "__main__":
    KneeboardApp().run()
