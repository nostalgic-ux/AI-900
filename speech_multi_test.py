"""
Azure Speech Services - Multi-Language Application
Features: Speech to Text and Text to Speech with 5 languages
Tabbed interface with scrollable design
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import azure.cognitiveservices.speech as speechsdk
import threading

class MultiLanguageSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Language Speech Services")
        self.root.geometry("900x750")
        self.root.configure(bg="#2e3440")
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Azure credentials
        self.speech_key = ""
        self.service_region = ""
        self.speech_config = None
        
        # Recognition status
        self.is_recognizing = False
        
        # Language configurations
        self.languages = {
            "English": {"code": "en-US", "voice": "en-US-JennyNeural"},
            "Hindi": {"code": "hi-IN", "voice": "hi-IN-SwaraNeural"},
            "German": {"code": "de-DE", "voice": "de-DE-KatjaNeural"},
            "French": {"code": "fr-FR", "voice": "fr-FR-DeniseNeural"},
            "Punjabi": {"code": "pa-IN", "voice": "pa-IN-GaganNeural"}
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        # Top Banner
        banner = tk.Frame(self.root, bg="#5e81ac", height=70)
        banner.pack(fill=tk.X)
        banner.pack_propagate(False)
        
        tk.Label(banner, text="🌍 Multi-Language Speech Services", 
                font=("Arial", 22, "bold"), bg="#5e81ac", fg="white").pack(pady=18)
        
        # Create scrollable canvas
        main_canvas = tk.Canvas(self.root, bg="#2e3440", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg="#2e3440")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        canvas_window = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Bind canvas width to scrollable frame width
        def configure_canvas_width(event):
            main_canvas.itemconfig(canvas_window, width=event.width)
        main_canvas.bind('<Configure>', configure_canvas_width)
        
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(event):
            main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def unbind_mousewheel(event):
            main_canvas.unbind_all("<MouseWheel>")
        
        main_canvas.bind('<Enter>', bind_mousewheel)
        main_canvas.bind('<Leave>', unbind_mousewheel)
        
        # Content inside scrollable frame
        content = tk.Frame(scrollable_frame, bg="#2e3440")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # ==================== CREDENTIALS ====================
        cred_frame = tk.LabelFrame(content, text="  Azure Configuration  ", 
                                   font=("Arial", 11, "bold"), bg="#3b4252", 
                                   fg="#eceff4", bd=2, relief=tk.GROOVE)
        cred_frame.pack(fill=tk.X, pady=(0, 20))
        
        cred_inner = tk.Frame(cred_frame, bg="#3b4252")
        cred_inner.pack(fill=tk.X, padx=20, pady=15)
        
        # Key
        tk.Label(cred_inner, text="Speech Key:", bg="#3b4252", fg="#d8dee9", 
                font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=8)
        self.key_entry = tk.Entry(cred_inner, show="*", font=("Arial", 10), 
                                 width=60, bg="#4c566a", fg="white", 
                                 insertbackground="white", relief=tk.FLAT)
        self.key_entry.grid(row=0, column=1, pady=8, padx=10, ipady=6)
        
        # Region
        tk.Label(cred_inner, text="Region:", bg="#3b4252", fg="#d8dee9", 
                font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.region_entry = tk.Entry(cred_inner, font=("Arial", 10), width=60,
                                     bg="#4c566a", fg="white", 
                                     insertbackground="white", relief=tk.FLAT)
        self.region_entry.insert(0, "eastus")
        self.region_entry.grid(row=1, column=1, pady=8, padx=10, ipady=6)
        
        # ==================== LANGUAGE SELECTION ====================
        lang_frame = tk.LabelFrame(content, text="  Select Language  ", 
                                  font=("Arial", 11, "bold"), bg="#3b4252", 
                                  fg="#eceff4", bd=2, relief=tk.GROOVE)
        lang_frame.pack(fill=tk.X, pady=(0, 20))
        
        lang_inner = tk.Frame(lang_frame, bg="#3b4252")
        lang_inner.pack(fill=tk.X, padx=20, pady=15)
        
        self.selected_language = tk.StringVar(value="English")
        
        lang_buttons = tk.Frame(lang_inner, bg="#3b4252")
        lang_buttons.pack()
        
        for idx, lang in enumerate(self.languages.keys()):
            btn = tk.Radiobutton(lang_buttons, text=lang, variable=self.selected_language,
                                value=lang, bg="#3b4252", fg="#eceff4", 
                                selectcolor="#5e81ac", font=("Arial", 10),
                                activebackground="#3b4252", activeforeground="white",
                                cursor="hand2")
            btn.pack(side=tk.LEFT, padx=15, pady=5)
        
        # ==================== TABBED INTERFACE ====================
        notebook_style = ttk.Style()
        notebook_style.theme_use('default')
        notebook_style.configure('TNotebook', background="#2e3440", borderwidth=0)
        notebook_style.configure('TNotebook.Tab', background="#4c566a", foreground="white",
                                padding=[20, 10], font=("Arial", 11, "bold"))
        notebook_style.map('TNotebook.Tab', background=[('selected', '#5e81ac')],
                          foreground=[('selected', 'white')])
        
        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # ==================== SPEECH TO TEXT TAB ====================
        stt_tab = tk.Frame(self.notebook, bg="#3b4252")
        self.notebook.add(stt_tab, text="🎤 Speech to Text")
        
        stt_content = tk.Frame(stt_tab, bg="#3b4252")
        stt_content.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Info
        info_frame = tk.Frame(stt_content, bg="#4c566a", relief=tk.FLAT, bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(info_frame, text="💡 Click 'Start Recording' and speak in your selected language", 
                bg="#4c566a", fg="#88c0d0", font=("Arial", 10, "italic")).pack(pady=12, padx=15)
        
        # Control buttons
        btn_container = tk.Frame(stt_content, bg="#3b4252")
        btn_container.pack(pady=15)
        
        self.start_btn = tk.Button(btn_container, text="▶ Start Recording",
                                   command=self.start_recognition,
                                   bg="#a3be8c", fg="white", font=("Arial", 12, "bold"),
                                   padx=30, pady=15, cursor="hand2", relief=tk.FLAT,
                                   activebackground="#8fbf7f")
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(btn_container, text="⏹ Stop Recording",
                                  command=self.stop_recognition,
                                  bg="#bf616a", fg="white", font=("Arial", 12, "bold"),
                                  padx=30, pady=15, cursor="hand2", relief=tk.FLAT,
                                  state=tk.DISABLED, activebackground="#a54f58")
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        self.clear_stt_btn = tk.Button(btn_container, text="🗑 Clear",
                                       command=self.clear_stt,
                                       bg="#5e81ac", fg="white", font=("Arial", 12, "bold"),
                                       padx=30, pady=15, cursor="hand2", relief=tk.FLAT,
                                       activebackground="#4c6a94")
        self.clear_stt_btn.pack(side=tk.LEFT, padx=10)
        
        # Status
        self.stt_status_label = tk.Label(stt_content, text="Status: Ready to record", 
                                         bg="#3b4252", fg="#d8dee9", font=("Arial", 11))
        self.stt_status_label.pack(pady=15)
        
        # Output area
        tk.Label(stt_content, text="Transcribed Text:", bg="#3b4252", 
                fg="#eceff4", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(10,5))
        
        self.stt_text = scrolledtext.ScrolledText(stt_content, wrap=tk.WORD, height=10,
                                                  font=("Arial", 11), bg="#4c566a", 
                                                  fg="white", insertbackground="white",
                                                  relief=tk.FLAT, padx=15, pady=15)
        self.stt_text.pack(fill=tk.BOTH, expand=True)
        
        # ==================== TEXT TO SPEECH TAB ====================
        tts_tab = tk.Frame(self.notebook, bg="#3b4252")
        self.notebook.add(tts_tab, text="🔊 Text to Speech")
        
        tts_content = tk.Frame(tts_tab, bg="#3b4252")
        tts_content.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Info
        info_frame2 = tk.Frame(tts_content, bg="#4c566a", relief=tk.FLAT, bd=1)
        info_frame2.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(info_frame2, text="💡 Type your text below and click 'Speak' to hear it in your selected language", 
                bg="#4c566a", fg="#88c0d0", font=("Arial", 10, "italic")).pack(pady=12, padx=15)
        
        # Input area
        tk.Label(tts_content, text="Enter Text to Speak:", bg="#3b4252", 
                fg="#eceff4", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(0,5))
        
        self.tts_text = scrolledtext.ScrolledText(tts_content, wrap=tk.WORD, height=8,
                                                  font=("Arial", 11), bg="#4c566a", 
                                                  fg="white", insertbackground="white",
                                                  relief=tk.FLAT, padx=15, pady=15)
        self.tts_text.pack(fill=tk.BOTH, expand=True, pady=(0,20))
        self.tts_text.insert(1.0, "Hello! Welcome to Multi-Language Speech Services.")
        
        # Control buttons
        tts_btn_container = tk.Frame(tts_content, bg="#3b4252")
        tts_btn_container.pack(pady=15)
        
        self.speak_btn = tk.Button(tts_btn_container, text="🔊 Speak Text",
                                   command=self.speak_text,
                                   bg="#ebcb8b", fg="#2e3440", font=("Arial", 12, "bold"),
                                   padx=35, pady=15, cursor="hand2", relief=tk.FLAT,
                                   activebackground="#d9b974")
        self.speak_btn.pack(side=tk.LEFT, padx=10)
        
        self.clear_tts_btn = tk.Button(tts_btn_container, text="🗑 Clear Text",
                                       command=self.clear_tts,
                                       bg="#5e81ac", fg="white", font=("Arial", 12, "bold"),
                                       padx=35, pady=15, cursor="hand2", relief=tk.FLAT,
                                       activebackground="#4c6a94")
        self.clear_tts_btn.pack(side=tk.LEFT, padx=10)
        
        # Status
        self.tts_status_label = tk.Label(tts_content, text="Status: Ready to speak", 
                                         bg="#3b4252", fg="#d8dee9", font=("Arial", 11))
        self.tts_status_label.pack(pady=15)
        
        # Footer
        footer = tk.Frame(self.root, bg="#3b4252", height=40)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        footer.pack_propagate(False)
        
        self.footer_label = tk.Label(footer, text="Ready | Select a language and tab to begin", 
                                     bg="#3b4252", fg="#d8dee9", font=("Arial", 9))
        self.footer_label.pack(pady=10)
    
    def initialize_config(self):
        """Initialize Azure Speech Configuration"""
        self.speech_key = self.key_entry.get().strip()
        self.service_region = self.region_entry.get().strip()
        
        if not self.speech_key or not self.service_region:
            messagebox.showwarning("Missing Configuration", 
                                 "Please enter your Azure Speech Key and Region")
            return False
        
        try:
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.speech_key,
                region=self.service_region
            )
            return True
        except Exception as e:
            messagebox.showerror("Configuration Error", f"Failed to initialize: {str(e)}")
            return False
    
    # ==================== SPEECH TO TEXT METHODS ====================
    
    def start_recognition(self):
        """Start speech recognition"""
        if not self.initialize_config():
            return
        
        selected_lang = self.selected_language.get()
        lang_code = self.languages[selected_lang]["code"]
        
        self.is_recognizing = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.stt_status_label.config(text=f"Status: Listening in {selected_lang}...", fg="#a3be8c")
        self.footer_label.config(text=f"🎤 Recording in {selected_lang}...")
        
        # Set language
        self.speech_config.speech_recognition_language = lang_code
        
        threading.Thread(target=self.recognize_continuous, daemon=True).start()
    
    def recognize_continuous(self):
        """Continuous speech recognition"""
        try:
            audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            recognizer.recognizing.connect(self.on_recognizing)
            recognizer.recognized.connect(self.on_recognized)
            recognizer.canceled.connect(self.on_canceled)
            
            recognizer.start_continuous_recognition()
            
            while self.is_recognizing:
                pass
            
            recognizer.stop_continuous_recognition()
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Recognition failed: {str(e)}"))
            self.root.after(0, self.stop_recognition)
    
    def on_recognizing(self, evt):
        """Interim results"""
        self.root.after(0, lambda: self.stt_status_label.config(
            text=f"Recognizing: {evt.result.text[:40]}...", fg="#88c0d0"))
    
    def on_recognized(self, evt):
        """Final results"""
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = evt.result.text
            self.root.after(0, lambda: self.stt_text.insert(tk.END, text + " "))
            self.root.after(0, lambda: self.stt_text.see(tk.END))
    
    def on_canceled(self, evt):
        """Handle errors"""
        if evt.reason == speechsdk.CancellationReason.Error:
            self.root.after(0, lambda: messagebox.showerror("Error", 
                f"Recognition error: {evt.error_details}"))
    
    def stop_recognition(self):
        """Stop recognition"""
        self.is_recognizing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.stt_status_label.config(text="Status: Stopped", fg="#bf616a")
        self.footer_label.config(text="Recording stopped")
    
    def clear_stt(self):
        """Clear STT text"""
        self.stt_text.delete(1.0, tk.END)
        self.stt_status_label.config(text="Status: Ready to record", fg="#d8dee9")
    
    # ==================== TEXT TO SPEECH METHODS ====================
    
    def speak_text(self):
        """Text to speech"""
        if not self.initialize_config():
            return
        
        text = self.tts_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Empty Text", "Please enter some text to speak")
            return
        
        selected_lang = self.selected_language.get()
        voice_name = self.languages[selected_lang]["voice"]
        
        self.speak_btn.config(state=tk.DISABLED)
        self.tts_status_label.config(text=f"Status: Speaking in {selected_lang}...", fg="#ebcb8b")
        self.footer_label.config(text=f"🔊 Speaking in {selected_lang}...")
        
        self.speech_config.speech_synthesis_voice_name = voice_name
        
        threading.Thread(target=self.synthesize, args=(text,), daemon=True).start()
    
    def synthesize(self, text):
        """Perform synthesis"""
        try:
            audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                self.root.after(0, lambda: self.tts_status_label.config(
                    text="Status: Completed ✓", fg="#a3be8c"))
                self.root.after(0, lambda: self.footer_label.config(
                    text="✓ Speech completed successfully"))
            elif result.reason == speechsdk.ResultReason.Canceled:
                details = result.cancellation_details
                self.root.after(0, lambda: messagebox.showerror("TTS Error",
                    f"Synthesis canceled: {details.reason}\n{details.error_details}"))
                self.root.after(0, lambda: self.tts_status_label.config(
                    text="Status: Error", fg="#bf616a"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"TTS failed: {str(e)}"))
            self.root.after(0, lambda: self.tts_status_label.config(
                text="Status: Error", fg="#bf616a"))
        
        finally:
            self.root.after(0, lambda: self.speak_btn.config(state=tk.NORMAL))
    
    def clear_tts(self):
        """Clear TTS text"""
        self.tts_text.delete(1.0, tk.END)
        self.tts_status_label.config(text="Status: Ready to speak", fg="#d8dee9")


def main():
    root = tk.Tk()
    app = MultiLanguageSpeechApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
