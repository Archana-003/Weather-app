import sys
print(sys.path)

import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk

import requests
import pyttsx3
from tkinter import ttk
import speech_recognition as sr

# Define global variables
listening = False
recognizing = False
accept_button = None  # Define the accept_button variable

class EntryWithPlaceholder(ttk.Entry):
    def __init__(self, master=None, placeholder="", font=None, placeholder_font=None, accept_button=None, **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_font = placeholder_font
        self.accept_button = accept_button  # Assign the accept_button
        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)
        self.config(font=font)
        self.update_placeholder()

    def focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete("0", "end")
            self.config(foreground='black')  # Change text color when focused

    def focus_out(self, event):
        if not self.get():
            self.insert("0", self.placeholder)
            self.config(foreground='grey', font=self.placeholder_font)  # Change font to placeholder font
        else:
            self.config(font=self.placeholder_font)  # Restore original font if text is entered

    def update_placeholder(self):
        self.configure(font=self.placeholder_font, foreground='grey')

    def get_assets_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller creates a temporary directory and stores path in _MEIPASS
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            # In regular Python execution, use the relative path
            return os.path.join(os.path.abspath("."), relative_path)

def configure_style():
    style = ttk.Style()
    style.configure('TButton', font=('Times New Roman', 12, 'italic'), foreground='black', background='#4CAF50')  # Black text color
    style.configure('TLabel', font=('Times New Roman', 12, 'italic'), foreground='black')
    style.configure('TEntry', font=('Times New Roman', 12, 'italic'), foreground='grey')  # Set initial color to grey
    style.configure('TText', font=('Times New Roman', 12, 'italic'), foreground='black', slant='italic')


def toggle_listen():
    global listening, accept_button  # Declare accept_button as a global variable
    if not listening:
        listening = True
        entry.config(state=tk.NORMAL)
        listen_button.config(text="", image=mic_icon_photo)
        if accept_button:  # Check if accept_button is defined
            accept_button.config(state=tk.DISABLED)
        get_weather_info()
    else:
        listening = False
        entry.config(state=tk.DISABLED)
        if accept_button:
            accept_button.config(state=tk.NORMAL)
        if recognizing:
            listen_button.config(text="", image=mic_icon_photo)
        else:
            listen_button.config(text="", image=mic_icon_photo)


def accept_manual_input():
    get_weather_info()

def get_weather(api_key, city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
    
    params = {"q": city, "appid": api_key, "units": "metric"}
    
    # Get current weather
    current_response = requests.get(base_url, params=params)
    current_data = current_response.json()
    
    # Get forecast
    forecast_params = {"q": city, "appid": api_key, "units": "metric"}
    forecast_response = requests.get(forecast_url, params=forecast_params)
    forecast_data = forecast_response.json()

    try:
        # Extract current weather
        current_temperature = current_data["main"]["temp"]
        current_description = current_data["weather"][0]["description"]
        
        # Extract future forecast
        forecast = forecast_data["list"][:5]  # Get the forecast for the next 5 periods (adjust as needed)
        
        # Build result string
        result = f"Current weather in {city}:\n"
        result += f"Temperature: {current_temperature}°C\n"
        result += f"Description: {current_description}\n\n"
        
        result += f"Future weather forecast for {city}:\n"
        
        for entry in forecast:
            time = entry["dt_txt"]
            temperature = entry["main"]["temp"]
            description = entry["weather"][0]["description"]
            result += f"{time}: {temperature}°C with {description}\n"

        update_text_widget(result)  # Update the text widget with weather details

    except Exception as e:
        update_text_widget(f"Please Enter the correct city name")

def update_text_widget(result):
    # Display the result in the text widget
    text_widget.delete("1.0", tk.END)  # Clear previous content
    text_widget.insert(tk.END, result)

def speak_weather_details():
    # Speak the weather details
    engine = pyttsx3.init()
    engine.say(text_widget.get("1.0", tk.END))
    engine.runAndWait()

def get_weather_info():
    city_name = entry.get() if not listening else listen_to_city()
    if city_name:
        result = get_weather(api_key, city_name)
        # Schedule speaking function after a short delay
        app.after(100, speak_weather_details)

def listen_to_city():
    global recognizing
    recognizing = True
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for city name...")
        r.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio = r.listen(source)

    try:
        city_name = r.recognize_google(audio)
        print(f"Recognized city: {city_name}")

        # Set the recognized city to the entry widget
        entry.delete(0, tk.END)
        entry.insert(0, city_name)

        return city_name
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    finally:
        recognizing = False

    return ""

def accept_manual_input():
    get_weather_info(manual_input=True)

# ...

def get_weather_info(manual_input=False):
    city_name = entry.get() if not listening or manual_input else listen_to_city()
    if city_name:
        result = get_weather(api_key, city_name)
        # Schedule speaking function after a short delay
        app.after(100, speak_weather_details)


# Main code
api_key = "44631e2c01f34c56ca9693c52d1de2e3"
app = tk.Tk()
app.title("Skysense")

# Configure style
configure_style()

# Load background image
bg_image = Image.open("assets\\background.jpg")
bg_width, bg_height = bg_image.size

app.geometry(f"{bg_width}x{bg_height}")
app.resizable(False, False)

# Set the default window icon
window_icon = tk.PhotoImage(file=r"assets\icon.gif")
app.iconphoto(False, window_icon)

bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(app, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

font_style = ("Helvetica", 12)
placeholder_font_style = ("Times New Roman", 12, "italic")

# ...

# ...

entry = EntryWithPlaceholder(app, placeholder="Enter city name", font=font_style, placeholder_font=placeholder_font_style, accept_button=accept_button)
entry.pack(pady=10)

# ...



# Load mic icon image and resize
mic_icon = Image.open(r"assets\mic.gif")
#mic_icon = mic_icon.resize((30, 30), Image.ANTIALIAS)
mic_icon = mic_icon.resize((70, 70), resample=Image.NEAREST)

mic_icon_photo = ImageTk.PhotoImage(mic_icon)

# Create a label to display the mic icon
listen_button = ttk.Button(app, image=mic_icon_photo, command=toggle_listen)
listen_button.pack(pady=20)

submit_button = ttk.Button(app, text="Get Weather", command=lambda: get_weather_info(manual_input=True))
submit_button.pack(pady=20)

text_widget = scrolledtext.ScrolledText(app, width=50, height=20, wrap=tk.WORD, font=('Times New Roman', 12, 'italic'))
text_widget.pack(pady=20)




listening = False
recognizing = False

app.mainloop()
