# Web Tests – Twitch Mobile (Selenium + Pytest)

This project implements an example, scalable Selenium test (with Page Object Model) for the mobile Twitch site using Chrome mobile emulation.

## ✅ What the test does (web module)
1. Open `https://m.twitch.tv/`
2. Tap the search icon
3. Type **"StarCraft II"**
4. Scroll down twice
5. Open one streamer from the results
6. Wait until the stream page is loaded and take a screenshot (saved to `artifacts/`)

Pop‑ups/modals are handled when present.

Useful options:
- `--device`: Chrome device name for emulation (e.g., `Pixel 5`, `iPhone 12 Pro`)
- `--headless`: run headless Chrome (`true`/`false`, defaults to 'false')
- `--base-url`: override base URL (defaults to `https://m.twitch.tv`)
- `--window-size`: the web browser window size (defaults to 300,1000)

> Tip: Selenium Manager auto-downloads the matching ChromeDriver. Make sure Google Chrome is installed.

---

## ✅ What the tests do (api module)
1. Make request
2. Retrieve data from response
3. Compare to expected result

---

## ⚙️ Tech stack
- Python 3.9+
- Selenium 4.x
- Pytest
- Chrome with mobile emulation (Pixel 5 by default)

---

## ▶️ How to run
```bash
To start tests, you need:
- 1. Update setup.sh, add the correct paths for your computer
- 2. Run the run_tests.sh file next way: source run_tests.sh MODULE_NAME
     (where module name can be one of (api, web,))
```

---

## 📸 Artifacts
- Screenshots are saved under `artifacts/` with timestamped filenames.

---

## 🔧 Extending
- Add more page objects under `src/pages`
- Add markers and parametrization in `tests/`
