# Frontend – Desktop GUI

The frontend provides a simple, responsive GUI to interact with JARVIS: start/stop the mic, view responses, and observe system status.

---

## Components

- `GUI.py`
  - Main application window and event loop
  - Mic toggle, status indicators, output area

- `Graphics/`
  - Visual assets used by the GUI (icons, GIFs)
  - Example: `Jarvis.gif`, `Mic_on.png`, `Mic_off.png`, `Home.png`

- `Files/*.data`
  - Lightweight state and data projections for the UI layer
  - Examples: `Mic.data`, `Status.data`, `Responses.data`

---

## Running the GUI

- Start via:
  - `python run_jarvis.py`
  - Or `start_jarvis.bat` on Windows

- Controls
  - Microphone: toggle on/off
  - Status: watch indicators for recording, processing, speaking
  - Output: read assistant responses and actions

---

## Assets & Styling

- Icons and GIFs live in `Frontend/Graphics/`
- You can replace assets to customize branding
- Ensure file names remain consistent with `GUI.py`

---

## Data Handling

- Small `.data` files provide UI state hints
- Larger outputs (MP3, logs) live in `Data/` and are ignored by Git

---

## Troubleshooting

- If the GUI doesn’t start
  - Verify dependencies: `pip install -r Requirements.txt`
  - Run from the project root: `python run_jarvis.py`

- If icons don’t appear
  - Confirm `Frontend/Graphics/` paths match those in `GUI.py`

---

## Customization

- Add menu items or buttons in `GUI.py`
- Introduce preferences (e.g., TTS voice, volume)
- Consider keyboard shortcuts for power users