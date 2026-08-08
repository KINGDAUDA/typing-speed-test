import json
import os
import re
import textwrap
import tkinter as tk
from datetime import datetime
from tkinter import font as tkfont
from passage_generator import fetch_scraped_passage

# Number of passage lines visible at once. When the user finishes the
# bottom visible line and presses space, the window rolls forward by one
# line (top line drops off, the next line of the passage appears at the
# bottom) - the same conveyor-belt behavior typingtest.com uses.
VISIBLE_LINES = 3
HIGH_SCORES_PATH = os.path.join(os.path.dirname(__file__), "high_scores.json")


def load_high_scores(path=HIGH_SCORES_PATH):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            scores = json.load(handle)
        if isinstance(scores, list):
            return scores
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    return []


def save_high_scores(scores, path=HIGH_SCORES_PATH):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(scores, handle, indent=2)


def record_high_score(wpm, accuracy, correct_words, path=HIGH_SCORES_PATH, name="Player"):
    scores = load_high_scores(path)
    entry = {
        "name": name or "Player",
        "wpm": int(wpm),
        "accuracy": round(float(accuracy), 1),
        "correct_words": int(correct_words),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    scores.append(entry)
    scores.sort(key=lambda item: (item["wpm"], item["accuracy"], item["correct_words"]), reverse=True)
    save_high_scores(scores[:10], path)
    return scores[:10]


class TypingSpeedTest(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Typing Speed Test")
        self.geometry("850x600")
        self.configure(bg="#1e1e2e")

        self.duration_seconds = 60
        self.time_left = 0
        self.timer_running = False
        self.timer_started = False
        self.reference_words = []
        self.after_id = None
        self.training_mode = False
        self.player_name = tk.StringVar(value="Player")
        self.mode_var = tk.StringVar(value="timed")

        self.mono_font = tkfont.Font(family="Consolas", size=14)
        self.build_setup_screen()

    def build_setup_screen(self):
        self.clear_window()
        frame = tk.Frame(self, bg="#1e1e2e")
        frame.pack(expand=True)

        tk.Label(frame, text="Typing Speed Test", font=("Segoe UI", 28, "bold"),
                 bg="#1e1e2e", fg="#f5f5f5").pack(pady=(0, 20))

        player_row = tk.Frame(frame, bg="#1e1e2e")
        player_row.pack(pady=(0, 10))
        tk.Label(player_row, text="Player name:", font=("Segoe UI", 12),
                 bg="#1e1e2e", fg="#cfcfcf").pack(side="left", padx=(0, 10))
        tk.Entry(player_row, textvariable=self.player_name, width=18,
                 font=("Segoe UI", 12), bg="#313244", fg="#f5f5f5",
                 insertbackground="#f5f5f5").pack(side="left")

        tk.Label(frame, text="Choose mode:", font=("Segoe UI", 14),
                 bg="#1e1e2e", fg="#cfcfcf").pack(pady=(0, 10))

        mode_frame = tk.Frame(frame, bg="#1e1e2e")
        mode_frame.pack(pady=(0, 8))
        for mode, label in (("timed", "Timed Challenge"), ("training", "Training Mode")):
            tk.Radiobutton(mode_frame, text=label, variable=self.mode_var, value=mode,
                           font=("Segoe UI", 12), bg="#1e1e2e", fg="#f5f5f5",
                           selectcolor="#313244", activebackground="#1e1e2e",
                           activeforeground="#f5f5f5", indicatoron=True
                           ).pack(side="left", padx=10)

        tk.Label(frame, text="Choose test duration:", font=("Segoe UI", 14),
                 bg="#1e1e2e", fg="#cfcfcf").pack(pady=(0, 10))

        btn_frame = tk.Frame(frame, bg="#1e1e2e")
        btn_frame.pack()
        self.selected_minutes = tk.IntVar(value=1)
        for minutes in (1, 2, 3):
            tk.Radiobutton(btn_frame, text=f"{minutes} min", variable=self.selected_minutes,
                           value=minutes, font=("Segoe UI", 12), bg="#1e1e2e", fg="#f5f5f5",
                           selectcolor="#313244", activebackground="#1e1e2e",
                           activeforeground="#f5f5f5", indicatoron=True
                           ).pack(side="left", padx=10)

        button_row = tk.Frame(frame, bg="#1e1e2e")
        button_row.pack(pady=25)
        tk.Button(button_row, text="Start", font=("Segoe UI", 14, "bold"),
                  bg="#89b4fa", fg="#1e1e2e", activebackground="#74a8f9",
                  relief="flat", padx=20, pady=8, command=self.start_test
                  ).pack(side="left", padx=(0, 15))
        tk.Button(button_row, text="High Scores", font=("Segoe UI", 13, "bold"),
                  bg="#a6e3a1", fg="#1e1e2e", activebackground="#8acc91",
                  relief="flat", padx=18, pady=8, command=self.show_high_scores
                  ).pack(side="left")

    # ------------------------------------------------------------------
    # TEST SCREEN
    # ------------------------------------------------------------------
    def show_high_scores(self):
        self.clear_window()
        frame = tk.Frame(self, bg="#1e1e2e")
        frame.pack(expand=True, fill="both", padx=30, pady=30)

        tk.Label(frame, text="High Scores", font=("Segoe UI", 26, "bold"),
                 bg="#1e1e2e", fg="#f5f5f5").pack(pady=(0, 20))

        scores = load_high_scores()
        if not scores:
            tk.Label(frame, text="No scores recorded yet.", font=("Segoe UI", 14),
                     bg="#1e1e2e", fg="#cfcfcf").pack()
        else:
            score_frame = tk.Frame(frame, bg="#1e1e2e")
            score_frame.pack(fill="x")
            headers = ["Rank", "Name", "WPM", "Accuracy"]
            for col, title in enumerate(headers):
                tk.Label(score_frame, text=title, font=("Segoe UI", 11, "bold"),
                         bg="#1e1e2e", fg="#f5f5f5", width=14, anchor="w").grid(row=0, column=col, padx=10, pady=4)
            for index, score in enumerate(scores[:10], start=1):
                tk.Label(score_frame, text=str(index), font=("Segoe UI", 11),
                         bg="#1e1e2e", fg="#cfcfcf", width=14, anchor="w").grid(row=index, column=0, padx=10, pady=3)
                tk.Label(score_frame, text=score["name"], font=("Segoe UI", 11),
                         bg="#1e1e2e", fg="#f5f5f5", width=14, anchor="w").grid(row=index, column=1, padx=10, pady=3)
                tk.Label(score_frame, text=str(score["wpm"]), font=("Segoe UI", 11),
                         bg="#1e1e2e", fg="#a6e3a1", width=14, anchor="w").grid(row=index, column=2, padx=10, pady=3)
                tk.Label(score_frame, text=f"{score['accuracy']}%", font=("Segoe UI", 11),
                         bg="#1e1e2e", fg="#89b4fa", width=14, anchor="w").grid(row=index, column=3, padx=10, pady=3)

        tk.Button(frame, text="Back to Menu", font=("Segoe UI", 13, "bold"),
                  bg="#89b4fa", fg="#1e1e2e", relief="flat", padx=20, pady=8,
                  command=self.build_setup_screen).pack(pady=30)

    def start_test(self):
        self.training_mode = self.mode_var.get() == "training"
        self.duration_seconds = self.selected_minutes.get() * 60 if not self.training_mode else 60
        self.time_left = self.duration_seconds
        self.timer_running = False
        self.timer_started = False

        raw_passage = fetch_scraped_passage(word_target=max(120, self.duration_seconds * 2))
        raw_passage = self.format_passage_text(raw_passage)

        self.clear_window()
        outer = tk.Frame(self, bg="#1e1e2e")
        outer.pack(expand=True, fill="both", padx=30, pady=20)

        top_bar = tk.Frame(outer, bg="#1e1e2e")
        top_bar.pack(fill="x")
        self.timer_label = tk.Label(top_bar, text=self.format_time(self.time_left),
                                    font=("Segoe UI", 18, "bold"), bg="#1e1e2e", fg="#f9e2af")
        self.timer_label.pack(side="left")

        self.wpm_live_label = tk.Label(top_bar, text="WPM: 0", font=("Segoe UI", 14),
                                       bg="#1e1e2e", fg="#a6e3a1")
        self.wpm_live_label.pack(side="right")

        if self.training_mode:
            tk.Label(top_bar, text="Training mode", font=("Segoe UI", 11, "bold"),
                     bg="#1e1e2e", fg="#f5f5f5").pack(side="right", padx=(0, 12))

        # Create the passage box EMPTY first and pack it, so we can measure
        # its real rendered pixel width before deciding how to wrap the text.
        self.passage_display = tk.Text(outer, height=VISIBLE_LINES, wrap="none", font=self.mono_font,
                                       bg="#313244", fg="#cdd6f4", relief="flat", padx=12, pady=12)
        self.passage_display.pack(fill="x", pady=(15, 15))
        self.passage_display.tag_config("correct", foreground="#a6e3a1")
        self.passage_display.tag_config("incorrect", foreground="#f38ba8", underline=True)

        self.prepare_passage_layout(raw_passage)

        self.input_box = tk.Text(outer, height=4, wrap="word", font=self.mono_font,
                                 bg="#181825", fg="#f5f5f5", insertbackground="#f5f5f5",
                                 relief="flat", padx=12, pady=12)
        self.input_box.pack(fill="both", expand=True)
        self.input_box.focus_set()

        # Disable Copy / Paste / Cut shortcuts and context events
        for event_key in ("<Control-c>", "<Control-C>", "<Control-v>", "<Control-V>",
                          "<Control-x>", "<Control-X>", "<<Copy>>", "<<Paste>>", "<<Cut>>"):
            self.input_box.bind(event_key, lambda e: "break")

        self.input_box.bind("<KeyPress>", self.on_keypress)
        self.input_box.bind("<KeyRelease>", self.on_keyrelease)
        # Fires after the space character is already inserted, so we can
        # reliably tell which word was JUST completed.
        self.input_box.bind("<KeyRelease-space>", self.on_space_pressed)

    def prepare_passage_layout(self, raw_passage):
        """
        Pre-wraps the passage into REAL lines (actual '\\n' characters) sized
        to the widget's current pixel width, and builds a deterministic
        word -> line index map from that wrapping.

        This replaces relying on Tk's internal word-wrap (wrap="word") plus
        querying `Text.index(...)`, because Tk's line/column indices only
        count literal newline characters - a passage with no '\\n' in it is
        always "line 1" as far as indexing is concerned, even though it
        visually wraps into several lines. That mismatch was why the
        auto-scroll condition could never trigger before.
        """
        self.update_idletasks()
        char_width = self.mono_font.measure("0")  # monospace: any char is representative
        padding = 2 * int(self.passage_display.cget("padx")) + 6
        usable_px = max(self.passage_display.winfo_width() - padding, char_width * 20)
        chars_per_line = max(20, usable_px // char_width)

        self.reference_lines = textwrap.wrap(
            raw_passage, width=chars_per_line,
            break_long_words=False, break_on_hyphens=False,
        )
        if not self.reference_lines:
            self.reference_lines = [raw_passage]

        self.reference_words = raw_passage.split()
        self.total_lines = len(self.reference_lines)

        # word_line_map: global word index -> which wrapped line it's on
        # line_word_ranges: per line, list of (global_word_index, col_start, col_end)
        self.word_line_map = {}
        self.line_word_ranges = []
        word_counter = 0
        for line_idx, line_text in enumerate(self.reference_lines):
            ranges = []
            col = 0
            for word in line_text.split():
                ranges.append((word_counter, col, col + len(word)))
                self.word_line_map[word_counter] = line_idx
                col += len(word) + 1  # +1 for the single space textwrap re-joins with
                word_counter += 1
            self.line_word_ranges.append(ranges)

        self.visible_lines_count = min(VISIBLE_LINES, self.total_lines) or 1
        self.visible_start_line = 0  # 0-indexed: which wrapped line is at the top
        self.refresh_passage_window()

    def refresh_passage_window(self):
        """Shows only the current window of `visible_lines_count` wrapped lines."""
        end_line = min(self.visible_start_line + self.visible_lines_count, self.total_lines)
        window_text = "\n".join(self.reference_lines[self.visible_start_line:end_line])

        self.passage_display.config(state="normal")
        self.passage_display.delete("1.0", "end")
        self.passage_display.insert("1.0", window_text)
        self.passage_display.config(state="disabled")

    def on_keypress(self, event):
        if not self.timer_started:
            self.timer_started = True
            self.timer_running = True
            self.tick()

    def on_space_pressed(self, event):
        """Rolls the passage window forward by one line once the user
        finishes the last VISIBLE line and presses space - no manual
        scrolling required."""
        if not self.timer_running:
            return
        typed_text = self.input_box.get("1.0", "end-1c")
        typed_words = typed_text.split()
        if not typed_words:
            return

        active_idx = len(typed_words) - 1  # index of the word just completed
        if active_idx >= len(self.reference_words):
            return

        active_line = self.word_line_map.get(active_idx, 0)
        bottom_visible_line = self.visible_start_line + self.visible_lines_count - 1

        if active_line >= bottom_visible_line:
            max_start = max(0, self.total_lines - self.visible_lines_count)
            if self.visible_start_line < max_start:
                self.visible_start_line += 1
                self.refresh_passage_window()
                self.update_live_feedback()  # re-apply highlighting in the new window immediately

    def on_keyrelease(self, event):
        if not self.timer_running:
            return
        self.update_live_feedback()

    def tick(self):
        if not self.timer_running:
            return
        self.timer_label.config(text=self.format_time(self.time_left))
        if self.time_left <= 0:
            self.end_test()
            return
        self.time_left -= 1
        self.after_id = self.after(1000, self.tick)

    @staticmethod
    def format_time(seconds):
        m, s = divmod(max(seconds, 0), 60)
        return f"{m:02d}:{s:02d}"

    def format_passage_text(self, text: str) -> str:
        """Lowercase the passage except standalone 'I' and letters following a full stop."""
        if not text:
            return ""

        lowered = text.lower()

        def cap_after_period(match):
            prefix = match.group(1) or ""
            ch = match.group(3).upper()
            return f"{prefix}{ch}"

        formatted = re.sub(r'(^|(\.\s+))([a-z])', cap_after_period, lowered)
        formatted = re.sub(r'\bi\b', 'I', formatted)
        return formatted

    def align_words(self, ref_words, typed_words):
        aligned_status = {}
        t_idx = 0
        r_idx = 0

        while t_idx < len(typed_words) and r_idx < len(ref_words):
            if typed_words[t_idx] == ref_words[r_idx]:
                aligned_status[r_idx] = "correct"
                t_idx += 1
                r_idx += 1
            else:
                found_match = False
                for lookahead in range(1, 4):
                    if r_idx + lookahead < len(ref_words) and typed_words[t_idx] == ref_words[r_idx + lookahead]:
                        for skipped in range(r_idx, r_idx + lookahead):
                            aligned_status[skipped] = "incorrect"
                        r_idx += lookahead
                        aligned_status[r_idx] = "correct"
                        t_idx += 1
                        r_idx += 1
                        found_match = True
                        break
                if not found_match:
                    aligned_status[r_idx] = "incorrect"
                    t_idx += 1
                    r_idx += 1

        return aligned_status

    def update_live_feedback(self):
        typed_text = self.input_box.get("1.0", "end-1c")
        typed_words = typed_text.split()
        self.sync_input_to_reference(typed_text, typed_words)

        aligned_status = self.align_words(self.reference_words, typed_words)

        self.passage_display.config(state="normal")
        self.passage_display.tag_remove("correct", "1.0", "end")
        self.passage_display.tag_remove("incorrect", "1.0", "end")

        for rel_line_idx in range(self.visible_lines_count):
            abs_line_idx = self.visible_start_line + rel_line_idx
            if abs_line_idx >= self.total_lines:
                break
            tk_line_no = rel_line_idx + 1  # Tk Text lines are 1-indexed
            for word_idx, col_start, col_end in self.line_word_ranges[abs_line_idx]:
                if word_idx in aligned_status:
                    start = f"{tk_line_no}.{col_start}"
                    end = f"{tk_line_no}.{col_end}"
                    self.passage_display.tag_add(aligned_status[word_idx], start, end)

        self.passage_display.config(state="disabled")

        elapsed = self.duration_seconds - self.time_left
        elapsed_minutes = max(elapsed / 60, 1 / 60)
        correct_so_far = sum(1 for status in aligned_status.values() if status == "correct")
        live_wpm = round(correct_so_far / elapsed_minutes)
        self.wpm_live_label.config(text=f"WPM: {live_wpm}")

    def sync_input_to_reference(self, typed_text, typed_words):
        """Rebuilds the input box content so words align with the visual line
        breaks of the reference passage. Preserves a trailing space so spaces
        aren't dropped, and auto-scrolls to keep the cursor visible."""
        if not self.reference_words or not typed_words:
            return

        trailing_space = typed_text.endswith(" ")

        lines = []
        current_line_words = []
        prev_line = None

        for i, word in enumerate(typed_words):
            word_line = self.word_line_map.get(i, prev_line if prev_line is not None else 0)
            if prev_line is None:
                prev_line = word_line

            if word_line != prev_line:
                lines.append(" ".join(current_line_words))
                current_line_words = [word]
                prev_line = word_line
            else:
                current_line_words.append(word)

        if current_line_words:
            lines.append(" ".join(current_line_words))

        if trailing_space and lines:
            lines[-1] = lines[-1] + " "

        new_text = "\n".join(lines)

        self.input_box.config(state="normal")
        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", new_text)
        self.input_box.mark_set("insert", "end")
        self.input_box.see("insert")

    def end_test(self):
        self.timer_running = False
        if self.after_id:
            self.after_cancel(self.after_id)
        self.input_box.config(state="disabled")

        typed_text = self.input_box.get("1.0", "end-1c")
        typed_words = typed_text.split()
        aligned_status = self.align_words(self.reference_words, typed_words)

        total_typed = len(typed_words)
        correct = sum(1 for status in aligned_status.values() if status == "correct")
        incorrect = total_typed - correct
        accuracy = round((correct / total_typed) * 100, 1) if total_typed > 0 else 0.0

        minutes = self.duration_seconds / 60
        wpm = round(correct / minutes) if minutes > 0 else 0

        if not self.training_mode:
            record_high_score(wpm, accuracy, correct, name=self.player_name.get() or "Player")

        self.show_results(wpm, accuracy, correct, incorrect, total_typed)

    def show_results(self, wpm, accuracy, correct, incorrect, total_typed):
        self.clear_window()
        frame = tk.Frame(self, bg="#1e1e2e")
        frame.pack(expand=True)

        tk.Label(frame, text="Results", font=("Segoe UI", 26, "bold"),
                 bg="#1e1e2e", fg="#f5f5f5").pack(pady=(0, 20))

        stats = [
            ("Words per minute", wpm, "#a6e3a1"),
            ("Accuracy", f"{accuracy}%", "#89b4fa"),
            ("Correct words", correct, "#a6e3a1"),
            ("Incorrect words", incorrect, "#f38ba8"),
            ("Total words typed", total_typed, "#cdd6f4"),
        ]
        for label, value, color in stats:
            row = tk.Frame(frame, bg="#1e1e2e")
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=("Segoe UI", 14), bg="#1e1e2e",
                     fg="#cfcfcf", width=20, anchor="w").pack(side="left")
            tk.Label(row, text=str(value), font=("Segoe UI", 14, "bold"),
                     bg="#1e1e2e", fg=color, anchor="w").pack(side="left")

        if not self.training_mode:
            latest = load_high_scores()[:1]
            if latest:
                top = latest[0]
                tk.Label(frame, text=f"Leaderboard: {top['name']} - {top['wpm']} WPM",
                         font=("Segoe UI", 12), bg="#1e1e2e", fg="#f9e2af").pack(pady=(15, 0))

        button_row = tk.Frame(frame, bg="#1e1e2e")
        button_row.pack(pady=30)
        tk.Button(button_row, text="Try Again", font=("Segoe UI", 13, "bold"),
                  bg="#89b4fa", fg="#1e1e2e", relief="flat", padx=20, pady=8,
                  command=self.build_setup_screen).pack(side="left", padx=(0, 12))
        tk.Button(button_row, text="High Scores", font=("Segoe UI", 13, "bold"),
                  bg="#a6e3a1", fg="#1e1e2e", relief="flat", padx=18, pady=8,
                  command=self.show_high_scores).pack(side="left")

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = TypingSpeedTest()
    app.mainloop()