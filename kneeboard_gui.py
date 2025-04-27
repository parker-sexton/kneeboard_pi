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
from kivy.graphics import Color, Line, Rectangle
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from functools import partial
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

# Set window properties for the Raspberry Pi
from kivy.config import Config

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

# Set fixed aspect ratio (3:5 for portrait mode)
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', '0')

# Window size will be determined by the display when in fullscreen mode

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
                Color(1, 1, 1)  # White color for drawing
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


class ChecklistButton(Button):
    """Button representing a checklist section that can be toggled."""
    
    is_selected = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(ChecklistButton, self).__init__(**kwargs)
        self.size_hint_y = None
        self.height = 45  # Increased height for better visibility
        self.font_size = 16  # Increased font size for better visibility
        self.background_normal = ''
        self.background_color = (0.5, 0.5, 0.5, 1)
        self.bind(is_selected=self.update_appearance)
    
    def update_appearance(self, instance, value):
        """Update the button appearance based on selection state."""
        if value:  # Selected
            self.background_color = (0.2, 0.5, 1.0, 1)  # Brighter blue for better contrast
        else:  # Not selected
            self.background_color = (0.5, 0.5, 0.5, 1)


class ChecklistContent(ScrollView):
    """Container for displaying the items of a specific checklist."""
    
    def __init__(self, title, items, **kwargs):
        super(ChecklistContent, self).__init__(**kwargs)
        self.size_hint_y = 1  # Always fill available vertical space
        self.do_scroll_x = False
        self.do_scroll_y = True
        # Main layout for the content
        self.layout = BoxLayout(orientation='vertical', spacing=2, padding=5, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        # Add the checklist items
        self.add_items(title, items)
        self.add_widget(self.layout)
    def add_items(self, title, items):
        # Title
        title_label = Label(
            text=title,
            font_size=18,
            bold=True,
            halign='center',
            size_hint_y=None,
            height=30,
            text_size=(Window.width - 20, None)
        )
        self.layout.add_widget(title_label)
        # Items
        for item in items:
            item_label = Label(
                text=item,
                font_size=16,
                halign='center',
                valign='middle',
                size_hint_y=None,
                text_size=(Window.width - 10, None)
            )
            item_label.bind(texture_size=lambda instance, size: setattr(instance, 'height', size[1]))
            self.layout.add_widget(item_label)


class ChecklistTab(BoxLayout):
    """Tab for displaying all checklists with button-based navigation."""
    def __init__(self, **kwargs):
        super(ChecklistTab, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 10

        # Button layout (fixed height)
        self.button_layout = GridLayout(
            cols=2,
            spacing=8,
            size_hint_y=None,  # IMPORTANT: only fix height in Y axis
            height=100
        )

        # Content area (fills remaining space)
        self.content_area = BoxLayout(
            orientation='vertical',
            size_hint_y=1  # Fill remaining space vertically
        )

        # Add widgets
        self.add_widget(self.button_layout)
        self.add_widget(self.content_area)

        # Initialize state
        self.current_button = None
        self.current_content = None

        # Populate buttons
        self.add_checklist_sections()

    def add_checklist_sections(self):
        sections = [
            ("Preflight", self.get_preflight_items()),
            ("Engine Start", self.get_engine_start_items()),
            ("Ground Ops", self.get_ground_ops_items()),
            ("Takeoff", self.get_takeoff_items()),
            ("Cruise", self.get_cruise_items()),
            ("Landing", self.get_landing_items()),
            ("Securing", self.get_securing_items()),
            ("V-Speeds", self.get_vspeeds_items())
        ]
        for title, items in sections:
            button = ChecklistButton(text=title)
            button.bind(on_press=lambda btn=button, t=title, i=items: self.on_section_selected(btn, t, i))
            self.button_layout.add_widget(button)
        if sections:
            first_button = self.button_layout.children[-1]
            self.on_section_selected(first_button, sections[0][0], sections[0][1])
    def on_section_selected(self, button, title, items):
        if self.current_button:
            self.current_button.is_selected = False
        button.is_selected = True
        self.current_button = button
        if self.current_content:
            self.content_area.remove_widget(self.current_content)
        self.current_content = ChecklistContent(title, items)
        self.content_area.add_widget(self.current_content)
    
    def get_preflight_items(self):
        """Get the preflight checklist items."""
        return [
            "FUEL/OIL",
            "1. FUEL TANKS - CHECK/SECURE",
            "2. FUEL SUMPS - DRAIN",
            "3. ENGINE OIL - CHECK/SECURE/MIN. 4 QTS",
            "",
            "CABIN",
            "1. PAPERWORK - ARROW",
            "2. FIRE EXTINGUISHER - CHECK/SECURE",
            "3. PITOT/STATIC SYSTEM - DRAIN",
            "4. ALTERNATE STATIC SOURCE - OFF/FWD",
            "5. MAGNETOS AND ALL SWITCHES - OFF",
            "6. STABILATOR/RUDDER TRIM - NEUTRAL",
            "7. TACH/HOBBS - CONFIRM/RECORD",
            "8. BATTERY MASTER SWITCH - ON",
            "9. EXTERIOR LIGHTING SWITCHES - ON",
            "10. PITOT HEAT SWITCH - ON",
            "11. FUEL GAUGES - QUANTITY CHECK",
            "12. EXTERIOR LIGHTS - CHECK",
            "13. PITOT HEAT - CHECK",
            "14. STALL WARNING HORN - CHECK",
            "15. EXTERIOR LIGHTING SWITCHES - OFF",
            "16. PITOT HEAT SWITCH - OFF",
            "17. BATTERY MASTER SWITCH - OFF",
            "18. FLAPS - EXTEND (40º)"
        ]
    
    def get_engine_start_items(self):
        """Get the engine start checklist items."""
        return [
            "BEFORE STARTING ENGINE",
            "1. AIRCRAFT - DISPATCH IN FLIGHT CIRCLE",
            "2. PAX BRIEFING - S.A.F.E.",
            "3. BELTS/BRAKE/SEATS - LOCKED/FASTENED",
            "4. FUEL SELECTOR - DESIRED TANK",
            "5. OVERHEAD SWITCHES - OFF",
            "6. EMERGENCY BATTERY - ARM",
            "7. E VOLTS - > 23.3 VOLTS",
            "*IF < 23.3 VOLTS, CHECK AGAIN AFTER RUN UP*",
            "8. ANNUNCIATORS - CHECK",
            "9. BATTERY MASTER - ON",
            "10. ALTERNATOR SWITCH - ON",
            "11. FIN STROBE - ON/DOWN",
            "12. CIRCUIT BREAKERS - CHECK",
            "13. ALT-AIR - CLOSED",
            "14. L/R MAGNETO SWITCHES - ON"
        ]
    
    def get_ground_ops_items(self):
        """Get the ground operations checklist items."""
        return [
            "RUN UP CHECK",
            "1. NAV/COM - SET",
            "2. CIRCUIT BREAKERS - CHECK",
            "3. ALTIMETERS - SET",
            "4. FLIGHT INSTRUMENTS - CHECK",
            "5. FLIGHT CONTROLS - FREE AND CORRECT",
            "6. AUTOPILOT - CHECK",
            "7. STABILATOR/RUDDER TRIM - SET",
            "8. FUEL PUMP - ON",
            "9. FUEL SELECTOR - SWITCH TANKS",
            "10. MIXTURE - RICH",
            "11. THROTTLE - 2000 RPM"
        ]
    
    def get_takeoff_items(self):
        """Get the takeoff checklist items."""
        return [
            "NORMAL TAKEOFF",
            "1. FLAPS - 0º",
            "2. THROTTLE - FULL",
            "3. ENGINE INSTRUMENTS - CHECK",
            "4. ROTATE - 60 KIAS",
            "5. CLIMB - 76 KIAS"
        ]
    
    def get_cruise_items(self):
        """Get the cruise checklist items."""
        return [
            "CRUISE",
            "1. POWER - SET PER TABLE",
            "2. MIXTURE - LEAN AS REQUIRED",
            "3. FUEL SELECTOR - ALTERNATE PER SCHEDULE"
        ]
    
    def get_landing_items(self):
        """Get the landing checklist items."""
        return [
            "APPROACH",
            "1. SEATS/SEAT BELTS - SET/FASTENED",
            "2. LIGHTS - SET AS REQUIRED",
            "3. FUEL PUMP - ON",
            "4. FUEL SELECTOR - FULLEST TANK",
            "5. MIXTURE - SET AS REQUIRED",
            "6. AIR CONDITIONER - OFF"
        ]
    
    def get_securing_items(self):
        """Get the securing checklist items."""
        return [
            "SECURING",
            "1. SQUAWK - 1200",
            "2. LIGHTS/DIM SWITCHES - OFF",
            "3. AVIONICS MASTER - OFF",
            "4. EMERGENCY BATTERY - OFF",
            "5. AIR CONDITIONER - OFF",
            "6. ELECTRICAL SWITCHES - OFF",
            "7. THROTTLE - IDLE",
            "8. MIXTURE - CUT-OFF",
            "9. L/R MAGNETO SWITCHES - OFF"
        ]
    
    def get_vspeeds_items(self):
        """Get the V-speeds checklist items."""
        return [
            "V-SPEEDS @ MAX GROSS WEIGHT",
            "Vso - 45 KIAS",
            "Vs - 50 KIAS",
            "Vr - 60 KIAS",
            "Vx - 64 KIAS",
            "Vy - 76 KIAS",
            "Vg - 76 KIAS",
            "Vfe - 102 KIAS",
            "Vno - 125 KIAS",
            "Vne - 154 KIAS",
            "Vo (2550 lbs.) - 113 KIAS",
            "Vo (1917 lbs.) - 98 KIAS",
            "",
            "MAX DEMONSTRATED CROSSWIND - 17 KTS"
        ]


class PiperArcherReference(ScrollView):
    """Reference information for the Piper Archer aircraft."""
    
    def __init__(self, **kwargs):
        super(PiperArcherReference, self).__init__(**kwargs)
        
        # Main layout for the reference content
        self.layout = BoxLayout(orientation='vertical', spacing=5, padding=5, size_hint_y=None)
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
            halign='center',  # Center align the title
            size_hint_y=None,
            height=40,
            text_size=(Window.width - 10, None)  # Use almost full width
        )
        self.layout.add_widget(title_label)
        
        # Section content
        content = "\n".join(items)
        content_label = Label(
            text=content,
            font_size=16,
            halign='center',  # Center align the content
            valign='middle',  # Middle vertical alignment
            size_hint_y=None,
            text_size=(Window.width - 10, None)  # Use almost full width
        )
        content_label.bind(texture_size=lambda instance, size: setattr(instance, 'height', size[1]))
        self.layout.add_widget(content_label)


class KneeboardApp(App):
    """Main application class for the pilot kneeboard."""
    
    def build(self):
        # Main vertical layout
        self.main_layout = BoxLayout(orientation='vertical')

        # Header (title + clock)
        self.header = BoxLayout(size_hint=(1, 0.1), padding=5)
        with self.header.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.header_bg = Rectangle(pos=self.header.pos, size=self.header.size)
        self.header.bind(pos=self._update_header_bg, size=self._update_header_bg)
        self.title_label = Label(
            text="Pilot Kneeboard",
            font_size=24,
            bold=True,
            size_hint=(0.7, 1),
            color=(1, 1, 1, 1),
            markup=True
        )
        self.clock_label = Label(
            text="00:00:00",
            font_size=24,
            size_hint=(0.3, 1),
            color=(1, 1, 1, 1),
            markup=True
        )
        self.header.add_widget(self.title_label)
        self.header.add_widget(self.clock_label)
        Clock.schedule_interval(self.update_clock, 1)
        self.main_layout.add_widget(self.header)

        # Custom tab bar
        self.tab_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), padding=2, spacing=2)
        self.tabs = [
            ("Reference", self.show_reference),
            ("Notepad", self.show_notepad),
            ("Checklists", self.show_checklists)
        ]
        self.tab_buttons = []
        for tab_name, callback in self.tabs:
            btn = Button(text=tab_name, font_size=18, background_color=(0.3, 0.3, 0.3, 1), color=(1, 1, 1, 1))
            btn.bind(on_press=callback)
            self.tab_bar.add_widget(btn)
            self.tab_buttons.append(btn)
        self.main_layout.add_widget(self.tab_bar)

        # ScreenManager for tab content
        self.screen_manager = ScreenManager(transition=NoTransition())
        self.reference_screen = Screen(name="reference")
        self.reference_screen.add_widget(PiperArcherReference())
        self.notepad_screen = Screen(name="notepad")
        self.notepad_screen.add_widget(NotepadTab())
        self.checklists_screen = Screen(name="checklists")
        self.checklists_screen.add_widget(ChecklistTab())
        self.screen_manager.add_widget(self.reference_screen)
        self.screen_manager.add_widget(self.notepad_screen)
        self.screen_manager.add_widget(self.checklists_screen)
        self.main_layout.add_widget(self.screen_manager)

        # Set default tab
        self.select_tab(1)  # Notepad by default
        return self.main_layout

    def select_tab(self, idx):
        # Update button appearance
        for i, btn in enumerate(self.tab_buttons):
            if i == idx:
                btn.background_color = (0.2, 0.5, 1.0, 1)
            else:
                btn.background_color = (0.3, 0.3, 0.3, 1)
        # Switch screen
        if idx == 0:
            self.screen_manager.current = "reference"
        elif idx == 1:
            self.screen_manager.current = "notepad"
        elif idx == 2:
            self.screen_manager.current = "checklists"

    def show_reference(self, instance):
        self.select_tab(0)
    def show_notepad(self, instance):
        self.select_tab(1)
    def show_checklists(self, instance):
        self.select_tab(2)

    def _update_header_bg(self, instance, value):
        self.header_bg.pos = instance.pos
        self.header_bg.size = instance.size

    def update_clock(self, dt):
        from datetime import datetime
        now = datetime.now()
        self.clock_label.text = now.strftime("%H:%M:%S")

    def on_start(self):
        Clock.schedule_once(self._force_redraw, 0.1)
    def _force_redraw(self, dt):
        self.main_layout.do_layout()
        self._update_header_bg(self.header, None)
        self.header.canvas.ask_update()
        Window.canvas.ask_update()


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
            # Set portrait mode with 3:5 aspect ratio
            Window.size = (480, 800)
        except Exception as e:
            print(f"Warning: Headless setup encountered an issue: {e}")
            print("Attempting to continue with default configuration...")
    else:
        # For non-headless mode, ensure window size is set correctly
        # Set portrait mode with 3:5 aspect ratio
        Window.size = (480, 800)
    
    # Force the window to update its size and position
    Window.top = 0
    Window.left = 0
    
    KneeboardApp().run()
