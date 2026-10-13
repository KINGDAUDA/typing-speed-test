# Typing Speed Test Application (GUI)

A clean, modern desktop typing speed test application built with Python and **Tkinter**. It measures typing speed (Words Per Minute — WPM) and accuracy against dynamic, natural English text with real-time feedback, non-cascading error handling, and line-by-line smooth navigation.

---

## Features

- **Dynamic Passage Fetching & Offline Fallback**:
  - Automatically fetches meaningful quotes from a live API (`dummyjson.com/quotes`) on every session launch.
  - Features an offline procedural sentence generator that respects proper sentence casing and capitalization following every period (`.`).
- **Cascade-Proof Word Alignment**:
  - Unlike naive index-matching algorithms where an omitted word breaks every following word, this app uses a dynamic lookahead matching algorithm. If you skip a word or insert a typo, the test syncs back up automatically.
- **Controlled Line-by-Line Auto-Scroll**:
  - Prevents erratic jumps or premature screen shifts while typing. The reference text window remains steady and only scrolls down to the next line when you complete a word and hit the **Spacebar**.
- **Anti-Cheat Measures**:
  - Disables clipboard actions (`Ctrl+C`, `Ctrl+V`, `Ctrl+X`, and corresponding context events) to ensure fair, authentic typing assessments.
- **Live Performance Metrics**:
  - First-keystroke timer start.
  - Real-time word highlight (green for correct, red/underlined for errors).
  - Running live WPM calculation.
  - Detailed summary screen reporting WPM, Accuracy (%), correct words, incorrect words, and total words typed.
- **Customizable Test Durations**:
  - Choose between 1, 2, or 3-minute timed assessments.

---

## Project Structure

```text
typing_speed_test/
├── passage_generator.py   # Handles web fetching, fallback generator, and text normalization
├── main.py                # Tkinter GUI, event bindings, alignment engine, and stats
└── README.md              # Project documentation
```

---

## Requirements

- **Python 3.8+**
- Standard Python libraries (no external `pip` dependencies needed):
  - `tkinter` (included with standard Python installations on Windows and macOS)
  - `urllib.request`
  - `json`
  - `random`
  - `re`

> **Note for Linux users:** If `tkinter` is missing, install it via your distribution's package manager:
> ```bash
> sudo apt-get install python3-tk
> ```

---

## Getting Started

1. **Clone or Download the Repository:**
   ```bash
   git clone https://github.com/your-username/typing-speed-test.git
   cd typing-speed-test
   ```

2. **Verify File Placement:**
   Make sure both `main.py` and `passage_generator.py` are located in the same directory.

3. **Run the Application:**
   ```bash
   python main.py
   ```

---

## How It Works

1. **Setup Screen**: Select your preferred duration (1 min, 2 min, or 3 min) and click **Start Test**.
2. **First Keystroke Start**: The timer does not count down while you read the passage; it initiates immediately upon typing your first character.
3. **Typing & Scrolling**:
   - Correct words turn green; mistakes are highlighted in red.
   - The passage holds steady until you reach the end of the line. Tapping **Space** to advance into the next line triggers the text viewer to slide down.
4. **Completion**: When the clock hits `00:00`, input freezes automatically and your breakdown report is calculated and displayed.
