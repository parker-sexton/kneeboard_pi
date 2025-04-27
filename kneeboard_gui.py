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

        # Button layout (more columns, dynamic height)
        self.button_layout = GridLayout(
            cols=3,
            spacing=8,
            size_hint_y=None  # let us set the height dynamically based on content
        )
        self.button_layout.bind(minimum_height=self.button_layout.setter('height'))

        # ScrollView to make button layout scrollable if needed
        self.button_scroll = ScrollView(
            size_hint=(1, None),
            height=150,  # Controls how much space the button area takes vertically
            do_scroll_x=False
        )
        self.button_scroll.add_widget(self.button_layout)

        # Content area (fills remaining space cleanly)
        self.content_area = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1)
        )

        # Assemble layout
        self.add_widget(self.button_scroll)
        self.add_widget(self.content_area)

        # State tracking
        self.current_button = None
        self.current_content = None

        # Populate
        self.add_checklist_sections()

    def add_checklist_sections(self):
        # Dynamically find all get_*_items methods
        section_methods = [
            (name, getattr(self, name))
            for name in dir(self)
            if name.startswith('get_') and name.endswith('_items') and callable(getattr(self, name))
        ]
        # Sort for consistent order (optional: could use a custom order if needed)
        section_methods.sort()
        sections = [(self._format_section_name(name), method()) for name, method in section_methods]

        self.button_layout.clear_widgets()
        for title, items in sections:
            button = ChecklistButton(text=title, size_hint_y=None, height=50)
            button.bind(on_press=lambda btn=button, t=title, i=items: self.on_section_selected(btn, t, i))
            self.button_layout.add_widget(button)

        # Properly select the first button
        if self.button_layout.children:
            first_button = self.button_layout.children[-1]  # GridLayout stores in reverse
            self.on_section_selected(first_button, sections[0][0], sections[0][1])

    def _format_section_name(self, method_name):
        # Convert get_engine_start_items -> Engine Start
        base = method_name[len('get_'):-len('_items')]
        return base.replace('_', ' ').title()

    def on_section_selected(self, button, title, items):
        if self.current_button:
            self.current_button.is_selected = False
        button.is_selected = True
        self.current_button = button

        if self.current_content:
            self.content_area.remove_widget(self.current_content)

        self.current_content = ChecklistContent(title, items)
        self.content_area.add_widget(self.current_content)


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
