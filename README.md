## ▶️ How to run
To start tests, you need:
- Run the run_tests.sh file next way: ```source run_tests.sh MODULE_NAME PATH_TO_THE_PROJECT```
  (where MODULE_NAME can be one of (api, web,), PATH_TO_THE_PROJECT: excluding the project folder name)

---

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

---

Useful options:
- `--device`: Chrome device name for emulation (e.g., `Pixel 5`, `iPhone 12 Pro`)
- `--headless`: run headless Chrome (`true`/`false`, defaults to 'false')
- `--base-url`: override base URL (defaults to `https://m.twitch.tv`)
- `--window-size`: the web browser window size (defaults to 300,1000)

> Tip: Selenium Manager auto-downloads the matching ChromeDriver. Make sure Google Chrome is installed.

---

## 🧪 Test case table

| ID | Title | Steps | Expected result | Notes |
|----|-------|-------|-----------------|-------|
| WEB-001 | Search and open streamer | Open home → tap search → type `StarCraft II` → scroll 2× → open a streamer | Streamer page loads; screenshot saved | Handles modals/popups if present |

---

# API Tests – Cat Facts (Pytest + Requests)

This project contains example automated API tests using the public, no‑auth **Cat Facts API** (`https://catfact.ninja`). It demonstrates parametrization, schema checks, and negative testing.

## ✅ What the tests do (api module)
1. Make request
2. Retrieve data from response
3. Compare to expected result

---

## 🧪 Test case table

| ID | Title | Endpoint | Validation | Why |
|----|-------|----------|------------|-----|
| API-001 | Get facts (200, schema) | `GET /facts` | Status 200; JSON has `data`, `current_page`, `per_page` | Basic availability + shape |
| API-002 | Pagination works | `GET /facts?page=N&limit=L` | Returns requested page + item count ≤ `limit` | Functional pagination |
| API-003 | Breeds schema | `GET /breeds` | Items contain `breed`, `country`, `origin`, `coat`, `pattern` | Data contract |
| API-004 | Invalid limit handled | `GET /facts?limit=-1` | Either 422 or defaulted behavior without crash | Robust error handling |

---

## ⚙️ Tech stack
- Python 3.9+
- Selenium 4.x
- Pytest
- Chrome with mobile emulation (Pixel 5 by default)

---

## 📸 Artifacts
- Test run log file, *.html test run report, screenshots are saved in ```$HOST_ARTIFACTS```
  (it should be set in setup.sh) 

---

## 🔧 Extending
- Add more page objects under `src/pages`
- Add markers and parametrization in `tests/`

---

![Demo animation](https://github.com/inartov555/python-automation-home-test/blob/main/demo/DEMO%20Sep-12-2025.gif)
