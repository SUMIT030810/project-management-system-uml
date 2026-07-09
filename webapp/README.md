# PMS Web Interface (Flask + HTML/CSS/JS)

A browser-based front end for the Project Management System. Wraps the
OOP classes in `../src/pms.py` behind a small REST API and a single-page
dashboard — no React, no build step, just Python + HTML/CSS/JS.

## Run it locally
```bash
pip install -r requirements.txt
python3 app.py
```
Then open **http://127.0.0.1:5000** in your browser.

## Folder structure
```
webapp/
├── app.py              # Flask backend + REST API
├── requirements.txt
├── Procfile             # for deployment (gunicorn)
├── templates/
│   └── index.html       # single-page app shell
└── static/
    ├── style.css         # design system
    └── app.js            # all frontend logic (fetch calls, rendering)
```

## Notes
- Data is stored **in memory** — restarting the server clears everything.
  See the Web Interface Guide (docx) for how to add SQLite persistence.
- All ports/hosts can be changed at the bottom of `app.py`.
