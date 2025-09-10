# API Tests – Cat Facts (Pytest + Requests)

This project contains example automated API tests using the public, no‑auth **Cat Facts API** (`https://catfact.ninja`). It demonstrates parametrization, schema checks, and negative testing.

---

## ▶️ How to run
```bash
python -m venv .venv && . .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pytest -v
```

---

## 🧪 Test case table

| ID | Title | Endpoint | Validation | Why |
|----|-------|----------|------------|-----|
| API-001 | Get facts (200, schema) | `GET /facts` | Status 200; JSON has `data`, `current_page`, `per_page` | Basic availability + shape |
| API-002 | Pagination works | `GET /facts?page=N&limit=L` | Returns requested page + item count ≤ `limit` | Functional pagination |
| API-003 | Breeds schema | `GET /breeds` | Items contain `breed`, `country`, `origin`, `coat`, `pattern` | Data contract |
| API-004 | Invalid limit handled | `GET /facts?limit=-1` | Either 422 or defaulted behavior without crash | Robust error handling |

---

## 📦 Stack
- Python 3.9+
- `pytest`
- `requests`
- optional: `pydantic`/`jsonschema` (not required here)