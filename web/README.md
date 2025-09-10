# Web Tests – Twitch Mobile (Selenium + Pytest)

This project implements an example, scalable Selenium test (with Page Object Model) for the mobile Twitch site using Chrome mobile emulation.

## ✅ What the test does
1. Open `https://m.twitch.tv/`
2. Tap the search icon
3. Type **"StarCraft II"**
4. Scroll down twice
5. Open one streamer from the results
6. Wait until the stream page is loaded and take a screenshot (saved to `artifacts/`)

Pop‑ups/modals are handled when present.

---

## ⚙️ Tech stack
- Python 3.9+
- Selenium 4.x
- Pytest
- Chrome with mobile emulation (Pixel 5 by default)

---

## ▶️ How to run
```bash
python -m venv .venv && . .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pytest -v --headless=true --device="Pixel 5" --screenshot-dir=artifacts
```

Useful options:
- `--device`: Chrome device name for emulation (e.g., `Pixel 5`, `iPhone 12 Pro`)
- `--headless`: run headless Chrome (`true`/`false`)
- `--base-url`: override base URL (defaults to `https://m.twitch.tv`)
- `--screenshot-dir`: where to save screenshots

> Tip: Selenium Manager auto-downloads the matching ChromeDriver. Make sure Google Chrome is installed.

---

## 🧱 Project structure
```
web-tests/
├─ src/
│  └─ pages/
│     ├─ base_page.py
│     ├─ home_page.py
│     ├─ search_page.py
│     └─ streamer_page.py
├─ tests/
│  └─ test_twitch_mobile.py
├─ conftest.py
├─ requirements.txt
├─ pytest.ini
└─ README.md
```

---

## 🧪 Test case table

| ID | Title | Steps | Expected result | Notes |
|----|-------|-------|-----------------|-------|
| WEB-001 | Search and open streamer | Open home → tap search → type `StarCraft II` → scroll 2× → open a streamer | Streamer page loads; screenshot saved | Handles modals/popups if present |

---

## 📸 Artifacts
- Screenshots are saved under `artifacts/` with timestamped filenames.

---

## 🔧 Extending
- Add more page objects under `src/pages`
- Add markers and parametrization in `tests/`