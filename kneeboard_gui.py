#!/usr/bin/env python3
"""
Pilot Kneeboard Application
A touchscreen application for pilots to use as a digital kneeboard.
Designed for Raspberry Pi Zero W 2 with touchscreen.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import Canvas, Label, Button, Frame, Scrollbar
from datetime import datetime
import time
from PIL import Image, ImageTk, ImageDraw

# Set default window size for the Raspberry Pi touchscreen
DEFAULT_WIDTH = 480
DEFAULT_HEIGHT = 854

class SquawkCodeInput(Frame):
    """Widget for entering a 4-digit squawk code using a pinpad."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(padx=10, pady=10)
        
        # Display for the squawk code
        self.display_frame = Frame(self)
        self.display_frame.pack(fill=tk.X, pady=5)
        
        self.squawk_display = Label(
            self.display_frame,
            text="1200",  # Default VFR squawk code
            font=("Arial", 40),
            width=4,
            anchor=tk.CENTER
        )
        self.squawk_display.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # Clear button
        self.clear_btn = Button(
            self.display_frame,
            text="Clear",
            font=("Arial", 14),
            bg="#ffaaaa",
            command=self.clear_squawk
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Pinpad layout
        self.pinpad = Frame(self)
        self.pinpad.pack(fill=tk.BOTH, expand=True)
        
        # Add number buttons (1-9)
        for i in range(3):
            for j in range(3):
                num = i * 3 + j + 1
                btn = Button(
                    self.pinpad,
                    text=str(num),
                    font=("Arial", 24),
                    width=3,
                    height=1,
                    command=lambda n=num: self.update_squawk(str(n))
                )
                btn.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
        
        # Add 0 button
        zero_btn = Button(
            self.pinpad,
            text="0",
            font=("Arial", 24),
            width=3,
            height=1,
            command=lambda: self.update_squawk("0")
        )
        zero_btn.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        
        # Add common squawk codes
        vfr_btn = Button(
            self.pinpad,
            text="VFR\n1200",
            font=("Arial", 16),
            width=3,
            height=2,
            command=lambda: self.set_squawk("1200")
        )
        vfr_btn.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")
        
        emergency_btn = Button(
            self.pinpad,
            text="EMER\n7700",
            font=("Arial", 16),
            width=3,
            height=2,
            bg="#ff0000",
            fg="white",
            command=lambda: self.set_squawk("7700")
        )
        emergency_btn.grid(row=3, column=2, padx=5, pady=5, sticky="nsew")
        
        # Configure grid weights
        for i in range(4):
            self.pinpad.grid_rowconfigure(i, weight=1)
        for i in range(3):
            self.pinpad.grid_columnconfigure(i, weight=1)
        
        # Current position in the squawk code (0-3)
        self.current_pos = 0
        self.squawk_code = "1200"
    
    def update_squawk(self, digit):
        """Update the squawk code with the pressed digit."""
        if self.current_pos < 4:
            # Replace the digit at the current position
            self.squawk_code = self.squawk_code[:self.current_pos] + digit + self.squawk_code[self.current_pos+1:]
            self.current_pos = (self.current_pos + 1) % 4
            self.squawk_display.config(text=self.squawk_code)
    
    def set_squawk(self, code):
        """Set a predefined squawk code."""
        self.squawk_code = code
        self.current_pos = 0
        self.squawk_display.config(text=self.squawk_code)
    
    def clear_squawk(self):
        """Clear the squawk code to 0000."""
        self.squawk_code = "0000"
        self.current_pos = 0
        self.squawk_display.config(text=self.squawk_code)


class DrawingCanvas(Canvas):
    """Canvas widget for drawing/taking notes with touch."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="black", highlightthickness=0)
        
        self.lines = []
        self.current_line = None
        
        # Bind mouse events for drawing
        self.bind("<Button-1>", self.on_touch_down)
        self.bind("<B1-Motion>", self.on_touch_move)
        self.bind("<ButtonRelease-1>", self.on_touch_up)
    
    def on_touch_down(self, event):
        """Handle touch down event to start a new line."""
        self.current_line = [event.x, event.y]
        self.start_x = event.x
        self.start_y = event.y
    
    def on_touch_move(self, event):
        """Handle touch move event to continue the current line."""
        if self.current_line:
            x, y = event.x, event.y
            # Draw line segment
            line_id = self.create_line(
                self.start_x, self.start_y, x, y,
                fill="white", width=2, smooth=True
            )
            self.current_line.extend([x, y])
            self.start_x = x
            self.start_y = y
    
    def on_touch_up(self, event):
        """Handle touch up event to complete the current line."""
        if self.current_line:
            self.lines.append(self.current_line)
            self.current_line = None
    
    def clear_canvas(self):
        """Clear all drawings from the canvas."""
        self.delete("all")
        self.lines = []
        self.current_line = None


class NotepadTab(Frame):
    """Tab for the notepad functionality."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(padx=10, pady=10)
        
        # Controls for the notepad
        self.controls = Frame(self)
        self.controls.pack(fill=tk.X, pady=5)
        
        self.clear_btn = Button(
            self.controls,
            text="Clear Notepad",
            font=("Arial", 14),
            command=self.clear_notepad
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Drawing canvas
        self.drawing_canvas = DrawingCanvas(
            self,
            width=DEFAULT_WIDTH - 20,
            height=DEFAULT_HEIGHT - 100
        )
        self.drawing_canvas.pack(fill=tk.BOTH, expand=True)
    
    def clear_notepad(self):
        """Clear the notepad canvas."""
        self.drawing_canvas.clear_canvas()


class ChecklistContent(Frame):
    """Container for displaying the items of a specific checklist."""
    
    def __init__(self, parent, title, items, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create a canvas with scrollbar
        self.canvas = Canvas(self, bg="#222222", highlightthickness=0)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg="#222222")
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack widgets
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Add the checklist items
        self.add_items(title, items)
    
    def add_items(self, title, items):
        """Add checklist items to the content area."""
        # Title
        title_label = Label(
            self.scrollable_frame,
            text=title,
            font=("Arial", 18, "bold"),
            bg="#222222",
            fg="white",
            pady=5
        )
        title_label.pack(fill=tk.X)
        
        # Items
        for item in items:
            item_label = Label(
                self.scrollable_frame,
                text=item,
                font=("Arial", 14),
                bg="#222222",
                fg="white",
                justify=tk.LEFT,
                wraplength=DEFAULT_WIDTH - 40,
                pady=2
            )
            item_label.pack(fill=tk.X, anchor="w")


class ChecklistTab(Frame):
    """Tab for displaying all checklists with button-based navigation."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(padx=10, pady=10)
        
        # Create the button layout
        self.button_frame = Frame(self)
        self.button_frame.pack(fill=tk.X, pady=5)
        
        # Create the content area
        self.content_frame = Frame(self, bg="#222222")
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Track the currently selected button and content
        self.current_button = None
        self.current_content = None
        
        # Add the checklist sections
        self.add_checklist_sections()
    
    def add_checklist_sections(self):
        """Add all checklist sections with their buttons and content."""
        # Define the checklist sections
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
        
        # Create buttons for each section
        for i, (title, items) in enumerate(sections):
            # Create the button
            button = Button(
                self.button_frame,
                text=title,
                font=("Arial", 12),
                bg="#555555",
                fg="white",
                height=2,
                command=lambda t=title, i=items: self.on_section_selected(t, i)
            )
            button.grid(row=i//4, column=i%4, padx=2, pady=2, sticky="nsew")
            
            # Store the button reference
            if i == 0:
                self.first_button = button
        
        # Configure grid weights
        for i in range(2):
            self.button_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.button_frame.grid_columnconfigure(i, weight=1)
        
        # Select the first section by default
        if sections:
            self.on_section_selected(sections[0][0], sections[0][1])
    
    def on_section_selected(self, title, items):
        """Handle selection of a checklist section."""
        # Remove the current content if there is any
        if self.current_content:
            self.current_content.destroy()
        
        # Create and add the new content
        self.current_content = ChecklistContent(self.content_frame, title, items)
        self.current_content.pack(fill=tk.BOTH, expand=True)
    
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


class PiperArcherReference(Frame):
    """Reference information for the Piper Archer aircraft."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create a canvas with scrollbar
        self.canvas = Canvas(self, bg="#222222", highlightthickness=0)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg="#222222")
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack widgets
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
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
    
    def add_section(self, title, items):
        """Add a section of reference information."""
        # Section title
        title_label = Label(
            self.scrollable_frame,
            text=title,
            font=("Arial", 18, "bold"),
            bg="#222222",
            fg="white",
            pady=10
        )
        title_label.pack(fill=tk.X)
        
        # Section content
        for item in items:
            item_label = Label(
                self.scrollable_frame,
                text=item,
                font=("Arial", 14),
                bg="#222222",
                fg="white",
                justify=tk.LEFT,
                wraplength=DEFAULT_WIDTH - 40,
                pady=2
            )
            item_label.pack(fill=tk.X, anchor="w")
        
        # Add some space between sections
        spacer = Frame(self.scrollable_frame, height=20, bg="#222222")
        spacer.pack(fill=tk.X)


class KneeboardApp:
    """Main application class for the pilot kneeboard."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Pilot Kneeboard")
        self.root.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
        
        # Set dark theme
        self.root.configure(bg="#111111")
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use the 'clam' theme as a base
        self.style.configure("TNotebook", background="#111111", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#333333", foreground="white", 
                            padding=[10, 5], font=('Arial', 14))
        self.style.map("TNotebook.Tab", background=[("selected", "#555555")])
        
        # Main layout
        self.main_frame = Frame(root, bg="#111111")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with title
        self.header = Frame(self.main_frame, bg="#222222", height=50)
        self.header.pack(fill=tk.X)
        
        self.title_label = Label(
            self.header,
            text="Pilot Kneeboard",
            font=("Arial", 24, "bold"),
            bg="#222222",
            fg="white"
        )
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # Add a clock display
        self.clock_label = Label(
            self.header,
            text="00:00:00",
            font=("Arial", 24),
            bg="#222222",
            fg="white"
        )
        self.clock_label.pack(side=tk.RIGHT, padx=10)
        self.update_clock()
        
        # Tabbed panel for different sections
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.reference_tab = Frame(self.notebook, bg="#222222")
        self.notepad_tab = Frame(self.notebook, bg="#222222")
        self.checklist_tab = Frame(self.notebook, bg="#222222")
        
        # Add tabs to notebook
        self.notebook.add(self.reference_tab, text="Reference")
        self.notebook.add(self.notepad_tab, text="Notepad")
        self.notebook.add(self.checklist_tab, text="Checklists")
        
        # Initialize tab contents
        self.reference_content = PiperArcherReference(self.reference_tab)
        self.reference_content.pack(fill=tk.BOTH, expand=True)
        
        self.notepad = NotepadTab(self.notepad_tab)
        self.notepad.pack(fill=tk.BOTH, expand=True)
        
        self.checklist_content = ChecklistTab(self.checklist_tab)
        self.checklist_content.pack(fill=tk.BOTH, expand=True)
    
    def update_clock(self):
        """Update the clock display."""
        now = datetime.now()
        self.clock_label.config(text=now.strftime("%H:%M:%S"))
        self.root.after(1000, self.update_clock)  # Update every second


def check_headless():
    """Check if running in headless mode and configure accordingly."""
    # Check if we're in headless mode
    headless = False
    vdisplay = None
    
    # On Linux/Unix systems
    if os.name == 'posix':
        headless = 'DISPLAY' not in os.environ or 'HEADLESS' in os.environ
        
        if headless:
            print("Running in headless mode on Linux/Unix...")
            try:
                # Try to import Xvfb for virtual display
                from xvfbwrapper import Xvfb
                print("Setting up virtual display with Xvfb...")
                vdisplay = Xvfb(width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT)
                vdisplay.start()
                # Set the DISPLAY environment variable
                if 'DISPLAY' not in os.environ:
                    os.environ['DISPLAY'] = ':1'
            except ImportError:
                print("Xvfbwrapper not found. Installing...")
                try:
                    import subprocess
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "xvfbwrapper"])
                    from xvfbwrapper import Xvfb
                    print("Setting up virtual display with Xvfb...")
                    vdisplay = Xvfb(width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT)
                    vdisplay.start()
                    # Set the DISPLAY environment variable
                    if 'DISPLAY' not in os.environ:
                        os.environ['DISPLAY'] = ':1'
                except:
                    print("Failed to set up virtual display. Falling back to dummy driver.")
                    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    # On Windows systems
    elif os.name == 'nt':
        headless = 'HEADLESS' in os.environ
        if headless:
            print("Running in headless mode on Windows...")
            # Windows doesn't need Xvfb, but we'll set a flag for headless operation
            # This will be used to avoid operations that require a display
    
    return headless, vdisplay


if __name__ == "__main__":
    # Check if running in headless mode
    headless, vdisplay = check_headless()
    
    try:
        # Create the root window
        root = tk.Tk()
        
        # Set window properties
        if not headless:
            # For non-headless mode, ensure window size is set correctly
            root.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
            
            # Force the window to update its size and position
            root.update_idletasks()
            
            # Center the window on screen
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            x = (screen_width - DEFAULT_WIDTH) // 2
            y = (screen_height - DEFAULT_HEIGHT) // 2
            root.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}+{x}+{y}")
        
        # Create and run the application
        app = KneeboardApp(root)
        root.mainloop()
    finally:
        # Clean up the virtual display if it was created
        if headless and vdisplay is not None:
            vdisplay.stop()
