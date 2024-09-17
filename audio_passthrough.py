import pyaudio
import tkinter as tk
from tkinter import ttk, messagebox

# Constants
CHUNK = 1024
FORMAT = pyaudio.paInt16  # 16-bit resolution
INPUT_CHANNELS = 1        # Mono input
OUTPUT_CHANNELS = 1       # Mono output
RATE = 44100              # Standard sample rate for audio

class VoicePassthroughApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Passthrough")
        self.root.geometry("400x300")

        self.p = pyaudio.PyAudio()

        self.input_device_index = None
        self.output_device_index = None

        self.create_widgets()
        self.populate_devices()

    def create_widgets(self):
        # Start Button
        self.start_button = tk.Button(self.root, text="Start", command=self.start_audio)
        self.start_button.pack(pady=10)

        # Stop Button
        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_audio)
        self.stop_button.pack(pady=10)

        # Device selection dropdowns
        self.input_device_label = tk.Label(self.root, text="Input Device:")
        self.input_device_label.pack(pady=5)
        self.input_device_combo = ttk.Combobox(self.root, state="readonly")
        self.input_device_combo.pack(pady=5)

        self.output_device_label = tk.Label(self.root, text="Output Device:")
        self.output_device_label.pack(pady=5)
        self.output_device_combo = ttk.Combobox(self.root, state="readonly")
        self.output_device_combo.pack(pady=5)

    def populate_devices(self):
        # Get device info
        input_devices = []
        output_devices = []

        for i in range(self.p.get_device_count()):
            dev_info = self.p.get_device_info_by_index(i)
            if dev_info['maxInputChannels'] > 0:
                input_devices.append((i, dev_info['name']))
            if dev_info['maxOutputChannels'] > 0:
                output_devices.append((i, dev_info['name']))

        self.input_device_combo['values'] = [dev[1] for dev in input_devices]
        self.output_device_combo['values'] = [dev[1] for dev in output_devices]

        # Default to first available device
        if input_devices:
            self.input_device_index = input_devices[0][0]
            self.input_device_combo.current(0)
        if output_devices:
            self.output_device_index = output_devices[0][0]
            self.output_device_combo.current(0)

        self.input_device_combo.bind("<<ComboboxSelected>>", self.update_input_device)
        self.output_device_combo.bind("<<ComboboxSelected>>", self.update_output_device)

    def update_input_device(self, event):
        selected_index = self.input_device_combo.get()
        self.input_device_index = self.find_device_index_by_name(selected_index)

    def update_output_device(self, event):
        selected_index = self.output_device_combo.get()
        self.output_device_index = self.find_device_index_by_name(selected_index)

    def find_device_index_by_name(self, name):
        for i in range(self.p.get_device_count()):
            dev_info = self.p.get_device_info_by_index(i)
            if dev_info['name'] == name:
                return i
        return None

    def setup_stream(self):
        # Ensure the devices are correctly selected and supported
        if self.input_device_index is None or self.output_device_index is None:
            raise ValueError("Input or output device not selected properly.")

        input_device_info = self.p.get_device_info_by_index(self.input_device_index)
        output_device_info = self.p.get_device_info_by_index(self.output_device_index)

        print(f"Using Input Device: {input_device_info['name']}")
        print(f"Using Output Device: {output_device_info['name']}")

        # Open a stream for input and output
        try:
            self.stream = self.p.open(
                format=FORMAT,
                channels=INPUT_CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                input_device_index=self.input_device_index,
                output_device_index=self.output_device_index,
                frames_per_buffer=CHUNK,
                stream_callback=self.audio_callback
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error setting up audio stream: {e}")
            print(f"Error setting up audio stream: {e}")

    def audio_callback(self, in_data, frame_count, time_info, status):
        # Pass the audio input directly to the output
        return (in_data, pyaudio.paContinue)

    def start_audio(self):
        try:
            self.setup_stream()
            self.stream.start_stream()
            print("Audio stream started.")
        except Exception as e:
            messagebox.showerror("Error", f"Error starting audio stream: {e}")

    def stop_audio(self):
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            print("Audio stream stopped.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoicePassthroughApp(root)
    root.mainloop()
