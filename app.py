import customtkinter as ctk
import threading
from model import ToxicityClassifier
import time

# Theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg": "#0D0D0F",
    "surface": "#16161A",
    "surface2": "#1E1E24",
    "border": "#2A2A35",
    "accent": "#6C63FF",
    "accent2": "#FF6584",
    "toxic": "#FF4C4C",
    "warning": "#FFA94D",
    "safe": "#51CF66",
    "text": "#E8E8F0",
    "subtext": "#8888A0",
}

CATEGORIES = [
    ("toxic",        "Toxic",         "#FF4C4C"),
    ("severe_toxic", "Severe Toxic",  "#CC0000"),
    ("obscene",      "Obscene",       "#FF6B35"),
    ("threat",       "Threat",        "#FF4C4C"),
    ("insult",       "Insult",        "#FFA94D"),
    ("identity_hate","Identity Hate", "#FF6584"),
]


class SafeChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SafeChat — AI Content Moderation")
        self.geometry("900x750")
        self.minsize(800, 650)
        self.configure(fg_color=COLORS["bg"])

        self.classifier = None
        self.is_loading = True
        self.history = []

        self._build_ui()
        threading.Thread(target=self._load_model, daemon=True).start()

    # ─── UI BUILD ────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="both", expand=True, padx=24, pady=12)

        title_frame = ctk.CTkFrame(header_inner, fg_color="transparent")
        title_frame.pack(side="left", fill="y")

        ctk.CTkLabel(
            title_frame, text="🛡️  SafeChat",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=COLORS["text"]
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            title_frame, text="AI-Powered Content Moderation",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["subtext"]
        ).pack(side="left", pady=(6, 0))

        self.status_label = ctk.CTkLabel(
            header_inner, text="⏳  Loading model...",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["warning"]
        )
        self.status_label.pack(side="right")

        # Main content
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=16)

        # Left column
        left = ctk.CTkFrame(main, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._build_input_panel(left)
        self._build_result_panel(left)

        # Right column
        right = ctk.CTkFrame(main, fg_color="transparent", width=280)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)

        self._build_category_panel(right)
        self._build_history_panel(right)

    def _build_input_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=12)
        panel.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            panel, text="Message to Analyze",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["subtext"]
        ).pack(anchor="w", padx=16, pady=(14, 6))

        self.input_box = ctk.CTkTextbox(
            panel,
            height=120,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["surface2"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text"],
            corner_radius=8,
            wrap="word"
        )
        self.input_box.pack(fill="x", padx=16, pady=(0, 12))
        self.input_box.insert("0.0", "Type or paste a message here...")
        self.input_box.bind("<FocusIn>", self._clear_placeholder)
        self.input_box.bind("<FocusOut>", self._restore_placeholder)
        self.input_box.bind("<Return>", lambda e: self._analyze())

        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 14))

        self.analyze_btn = ctk.CTkButton(
            btn_row,
            text="Analyze Message",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color="#5A52D5",
            height=42,
            corner_radius=8,
            command=self._analyze,
            state="disabled"
        )
        self.analyze_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            btn_row,
            text="Clear",
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["surface2"],
            hover_color=COLORS["border"],
            text_color=COLORS["subtext"],
            height=42,
            corner_radius=8,
            command=self._clear_all
        ).pack(side="right", width=80)

    def _build_result_panel(self, parent):
        self.result_panel = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=12)
        self.result_panel.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.result_panel, text="Analysis Result",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["subtext"]
        ).pack(anchor="w", padx=16, pady=(14, 8))

        # Verdict badge
        self.verdict_frame = ctk.CTkFrame(self.result_panel, fg_color=COLORS["surface2"], corner_radius=10)
        self.verdict_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.verdict_icon = ctk.CTkLabel(
            self.verdict_frame, text="🔍",
            font=ctk.CTkFont(size=28),
            text_color=COLORS["subtext"]
        )
        self.verdict_icon.pack(side="left", padx=16, pady=14)

        verdict_text_frame = ctk.CTkFrame(self.verdict_frame, fg_color="transparent")
        verdict_text_frame.pack(side="left", fill="y", pady=14)

        self.verdict_label = ctk.CTkLabel(
            verdict_text_frame, text="Awaiting input...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["subtext"]
        )
        self.verdict_label.pack(anchor="w")

        self.confidence_label = ctk.CTkLabel(
            verdict_text_frame, text="Submit a message to begin analysis",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["subtext"]
        )
        self.confidence_label.pack(anchor="w")

        # Confidence bar
        bar_frame = ctk.CTkFrame(self.result_panel, fg_color="transparent")
        bar_frame.pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(
            bar_frame, text="Toxicity Score",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["subtext"]
        ).pack(anchor="w")

        self.progress_bar = ctk.CTkProgressBar(
            bar_frame,
            height=12,
            corner_radius=6,
            fg_color=COLORS["surface2"],
            progress_color=COLORS["safe"]
        )
        self.progress_bar.pack(fill="x", pady=(4, 0))
        self.progress_bar.set(0)

        self.score_label = ctk.CTkLabel(
            bar_frame, text="0%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["subtext"]
        )
        self.score_label.pack(anchor="e")

    def _build_category_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=12)
        panel.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            panel, text="Category Breakdown",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["subtext"]
        ).pack(anchor="w", padx=14, pady=(14, 8))

        self.cat_bars = {}
        for key, label, color in CATEGORIES:
            row = ctk.CTkFrame(panel, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=3)

            ctk.CTkLabel(
                row, text=label,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["subtext"],
                width=90,
                anchor="w"
            ).pack(side="left")

            bar = ctk.CTkProgressBar(
                row, height=8, corner_radius=4,
                fg_color=COLORS["surface2"],
                progress_color=color
            )
            bar.pack(side="left", fill="x", expand=True, padx=(6, 6))
            bar.set(0)

            pct = ctk.CTkLabel(
                row, text="0%",
                font=ctk.CTkFont(size=10),
                text_color=COLORS["subtext"],
                width=32
            )
            pct.pack(side="right")

            self.cat_bars[key] = (bar, pct)

        ctk.CTkFrame(panel, fg_color="transparent", height=10).pack()

    def _build_history_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=12)
        panel.pack(fill="both", expand=True)

        header_row = ctk.CTkFrame(panel, fg_color="transparent")
        header_row.pack(fill="x", padx=14, pady=(14, 6))

        ctk.CTkLabel(
            header_row, text="Recent History",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["subtext"]
        ).pack(side="left")

        ctk.CTkButton(
            header_row, text="Clear",
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            hover_color=COLORS["surface2"],
            text_color=COLORS["subtext"],
            height=22, width=40,
            command=self._clear_history
        ).pack(side="right")

        self.history_scroll = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"]
        )
        self.history_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ─── MODEL ───────────────────────────────────────────────────────────────

    def _load_model(self):
        self.classifier = ToxicityClassifier()
        self.after(0, self._on_model_ready)

    def _on_model_ready(self):
        self.is_loading = False
        self.status_label.configure(text="✅  Model ready", text_color=COLORS["safe"])
        self.analyze_btn.configure(state="normal")

    # ─── ACTIONS ─────────────────────────────────────────────────────────────

    def _analyze(self, event=None):
        text = self.input_box.get("0.0", "end").strip()
        if not text or text == "Type or paste a message here...":
            return
        if self.is_loading:
            return

        self.analyze_btn.configure(state="disabled", text="Analyzing...")
        self.status_label.configure(text="🔄  Analyzing...", text_color=COLORS["warning"])

        threading.Thread(target=self._run_analysis, args=(text,), daemon=True).start()

    def _run_analysis(self, text):
        result = self.classifier.classify(text)
        self.after(0, lambda: self._display_result(text, result))

    def _display_result(self, text, result):
        scores = result["scores"]
        is_toxic = result["is_toxic"]
        top_score = result["top_score"]

        # Verdict
        if is_toxic:
            icon = "⚠️"
            verdict = "TOXIC CONTENT DETECTED"
            color = COLORS["toxic"]
        else:
            icon = "✅"
            verdict = "CONTENT IS SAFE"
            color = COLORS["safe"]

        self.verdict_icon.configure(text=icon)
        self.verdict_label.configure(text=verdict, text_color=color)
        self.confidence_label.configure(
            text=f"Confidence: {top_score:.1%}  |  Processed in <1s",
            text_color=COLORS["subtext"]
        )

        # Progress bar
        bar_color = COLORS["toxic"] if top_score > 0.7 else COLORS["warning"] if top_score > 0.4 else COLORS["safe"]
        self.progress_bar.configure(progress_color=bar_color)
        self.progress_bar.set(top_score)
        self.score_label.configure(text=f"{top_score:.0%}", text_color=bar_color)

        # Category bars
        for key, (bar, pct_label) in self.cat_bars.items():
            val = scores.get(key, 0.0)
            bar.set(val)
            pct_label.configure(text=f"{val:.0%}")

        # History
        self._add_history(text, verdict, color, top_score)

        # Reset
        self.analyze_btn.configure(state="normal", text="Analyze Message")
        self.status_label.configure(text="✅  Model ready", text_color=COLORS["safe"])

    def _add_history(self, text, verdict, color, score):
        preview = text[:40] + "..." if len(text) > 40 else text
        self.history.insert(0, (preview, verdict, color, score))

        # Clear and rebuild
        for w in self.history_scroll.winfo_children():
            w.destroy()

        for prev, verd, col, sc in self.history[:10]:
            item = ctk.CTkFrame(
                self.history_scroll,
                fg_color=COLORS["surface2"],
                corner_radius=8
            )
            item.pack(fill="x", pady=3)

            indicator = ctk.CTkFrame(item, fg_color=col, width=4, corner_radius=2)
            indicator.pack(side="left", fill="y", padx=(0, 8))

            text_frame = ctk.CTkFrame(item, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, pady=6)

            ctk.CTkLabel(
                text_frame, text=prev,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text"],
                anchor="w",
                wraplength=180
            ).pack(anchor="w")

            ctk.CTkLabel(
                text_frame,
                text=f"{sc:.0%} · {'Toxic' if col == COLORS['toxic'] else 'Safe'}",
                font=ctk.CTkFont(size=10),
                text_color=COLORS["subtext"],
                anchor="w"
            ).pack(anchor="w")

    def _clear_history(self):
        self.history.clear()
        for w in self.history_scroll.winfo_children():
            w.destroy()

    def _clear_all(self):
        self.input_box.delete("0.0", "end")
        self.input_box.insert("0.0", "Type or paste a message here...")
        self.input_box.configure(text_color=COLORS["subtext"])
        self.verdict_label.configure(text="Awaiting input...", text_color=COLORS["subtext"])
        self.confidence_label.configure(text="Submit a message to begin analysis")
        self.verdict_icon.configure(text="🔍")
        self.progress_bar.set(0)
        self.score_label.configure(text="0%", text_color=COLORS["subtext"])
        for key, (bar, pct) in self.cat_bars.items():
            bar.set(0)
            pct.configure(text="0%")

    def _clear_placeholder(self, event):
        if self.input_box.get("0.0", "end").strip() == "Type or paste a message here...":
            self.input_box.delete("0.0", "end")
            self.input_box.configure(text_color=COLORS["text"])

    def _restore_placeholder(self, event):
        if not self.input_box.get("0.0", "end").strip():
            self.input_box.insert("0.0", "Type or paste a message here...")
            self.input_box.configure(text_color=COLORS["subtext"])


if __name__ == "__main__":
    app = SafeChatApp()
    app.mainloop()
