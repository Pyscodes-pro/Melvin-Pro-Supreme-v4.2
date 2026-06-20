import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

# FIX UNTUK PYTHON 3.13+
try:
    import audioop
except ImportError:
    try:
        import audioop_lts as audioop
        sys.modules["audioop"] = audioop
    except ImportError:
        print("Install dulu: pip install audioop-lts")
        sys.exit()

from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter
from pedalboard import Pedalboard, Reverb, Chorus, Delay, Compressor, LowShelfFilter, Gain
from pedalboard.io import AudioFile

# Setup FFmpeg
curr_dir = os.path.dirname(os.path.realpath(__file__))
AudioSegment.converter = os.path.join(curr_dir, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(curr_dir, "ffprobe.exe")

class MelvinBypasser:
    def __init__(self, root):
        self.root = root
        self.root.title("MELVIN PRO SUPREME - V4.2 SIDE-BY-SIDE")
        self.root.geometry("800x480") # Ukuran Baru: Melebar ke samping
        self.root.configure(bg="#050505") 

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Blue.Horizontal.TProgressbar", background="#00aaff", troughcolor="#111", bordercolor="#00aaff")

        # Header
        tk.Label(root, text="MELVIN PRO", font=("Arial", 28, "bold"), bg="#050505", fg="#00aaff").pack(pady=(10,0))
        tk.Label(root, text="SUPREME AUDIO BYPASSER", font=("Arial", 8, "italic"), bg="#050505", fg="#006699").pack()

        # CONTAINER UTAMA (Horizontal)
        self.content_frame = tk.Frame(root, bg="#050505")
        self.content_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # --- KOLOM KIRI (SLIDERS) ---
        self.left_frame = tk.LabelFrame(self.content_frame, text=" AUDIO CONTROLS ", bg="#0a0a0a", fg="#00aaff", font=("Arial", 9, "bold"), bd=1)
        self.left_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        self.create_slider(self.left_frame, "PITCH SHIFT", 0.1, 2.0, 0.8)
        self.create_slider(self.left_frame, "SPEED MULTIPLIER", 0.8, 1.4, 1.05)
        self.create_slider(self.left_frame, "BASS BOOST", 0, 20, 6)
        self.create_slider(self.left_frame, "REVERB", 0, 100, 15)

        # --- KOLOM KANAN (OPTIONS) ---
        self.right_frame = tk.LabelFrame(self.content_frame, text=" BYPASS FEATURES ", bg="#0a0a0a", fg="#00aaff", font=("Arial", 9, "bold"), bd=1)
        self.right_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)

        self.check_vars = {}
        features = [
            ("Nightcore Mod", "nightcore"),
            ("Safe Start (Reverse)", "rev_start"),
            ("Anti-Scan Noise", "noise"),
            ("Echo Delay", "echo"),
            ("Loudness Punch", "comp"),
            ("Frequency Cut", "hpf"),
            ("Gain Boost", "gain"),
            ("Extra Wide", "wide")
        ]

        for text, var_name in features:
            var = tk.BooleanVar()
            self.check_vars[var_name] = var
            cb = tk.Checkbutton(self.right_frame, text=text, variable=var, bg="#0a0a0a", fg="#00aaff", 
                               selectcolor="#050505", activebackground="#0a0a0a", font=("Arial", 10))
            cb.pack(anchor="w", padx=20, pady=6)

        # --- FOOTER (PROGRESS & BUTTON) ---
        self.footer_frame = tk.Frame(root, bg="#050505")
        self.footer_frame.pack(side="bottom", fill="x", padx=30, pady=10)

        self.progress_label = tk.Label(self.footer_frame, text="Status: IDLE", bg="#050505", fg="#00aaff", font=("Arial", 9))
        self.progress_label.pack()
        
        self.progress = ttk.Progressbar(self.footer_frame, orient="horizontal", length=700, mode="determinate", style="Blue.Horizontal.TProgressbar")
        self.progress.pack(pady=5)

        self.btn_process = tk.Button(self.footer_frame, text="START PROCESS", command=self.start_thread, 
                                   bg="#00aaff", fg="#000", font=("Arial", 11, "bold"), 
                                   padx=50, pady=8, relief="flat", cursor="hand2")
        self.btn_process.pack(pady=5)

        tk.Label(root, text="© MELVIN PRO BYPASSER", font=("Arial", 7, "bold"), bg="#050505", fg="#003355").pack(side="bottom")

    def create_slider(self, parent, label, min_val, max_val, default):
        tk.Label(parent, text=label, bg="#0a0a0a", fg="#00aaff", font=("Arial", 8, "bold")).pack(pady=(5,0))
        slider = tk.Scale(parent, from_=min_val, to=max_val, resolution=0.05, orient="horizontal",
                         bg="#0a0a0a", fg="white", highlightthickness=0, troughcolor="#111", length=300)
        slider.set(default)
        slider.pack(pady=2, padx=10)
        setattr(self, label.lower().replace(" ","_"), slider)

    def start_thread(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.ogg")])
        if file_path:
            threading.Thread(target=self.process, args=(file_path,), daemon=True).start()

    def process(self, input_path):
        try:
            self.btn_process.config(state="disabled")
            self.progress['value'] = 0
            self.progress_label.config(text="Status: Loading Audio...")
            
            audio = AudioSegment.from_file(input_path)
            pitch = self.pitch_shift.get()
            speed = self.speed_multiplier.get()
            
            if self.check_vars["nightcore"].get(): pitch, speed = 1.3, 1.25

            new_sample_rate = int(audio.frame_rate * (2.0 ** (pitch / 12.0)))
            audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
            audio = audio.set_frame_rate(44100)
            audio = audio.speedup(playback_speed=speed)

            if self.check_vars["rev_start"].get(): audio = audio[:500].reverse() + audio[500:]

            temp_wav = "temp_render.wav"
            audio.export(temp_wav, format="wav")

            output_path = os.path.join(os.path.dirname(input_path), "MELVIN_BYPASS_" + os.path.basename(input_path).replace(".mp3", "") + ".mp3")
            
            with AudioFile(temp_wav) as f:
                with AudioFile(output_path, 'w', f.samplerate, f.num_channels) as o:
                    effects = []
                    effects.append(LowShelfFilter(cutoff_frequency_hz=250, gain_db=self.bass_boost.get()))
                    rev_wet = self.reverb.get() / 100
                    effects.append(Reverb(room_size=0.3, wet_level=rev_wet, dry_level=1.0))
                    
                    if self.check_vars["echo"].get(): effects.append(Delay(delay_seconds=0.2, feedback=0.3))
                    if self.check_vars["comp"].get(): effects.append(Compressor(threshold_db=-15))
                    if self.check_vars["gain"].get(): effects.append(Gain(gain_db=3))
                    
                    board = Pedalboard(effects)
                    total_frames = f.frames
                    
                    while f.tell() < f.frames:
                        chunk = f.read(f.samplerate)
                        o.write(board(chunk, f.samplerate))
                        prog = (f.tell() / total_frames) * 100
                        self.progress['value'] = prog
                        self.progress_label.config(text=f"Status: Rendering {int(prog)}%")

            if os.path.exists(temp_wav): os.remove(temp_wav)
            self.progress_label.config(text="Status: FINISHED!")
            messagebox.showinfo("Melvin Pro", "BERHASIL BYPASS!")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.btn_process.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = MelvinBypasser(root)
    root.mainloop()
