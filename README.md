# DreamLab

DreamLab is a full-stack clinical dream tracking web application built with Flask and MariaDB. Designed as a structured journaling platform for patients experiencing sleep difficulties, it provides a guided dream recording interface, mood and sleep quality tracking, and a role-based access system that separates patient and clinician accounts.

**GitHub:** [github.com/Mervellious/DreamLab](https://github.com/Mervellious/DreamLab)

---

## Overview

The application allows patients to log dreams and nightmares through a multi-step questionnaire, review their entries over time, and visualise mood and sleep quality trends through interactive charts. Clinicians can access a dedicated dashboard, review assigned patient records, and generate written reports linked to individual patients.

DreamLab was developed as a school project at SAE Institute London, demonstrating full-stack web development using Python, a relational database, session-based authentication, and a data visualisation API.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| Database | MariaDB (via XAMPP) |
| DB connector | PyMySQL |
| Templating | Jinja2 |
| Data visualisation | Chart.js |
| Icons | Lucide Icons |
| Auth / security | Werkzeug (password hashing) |
| Dev environment | XAMPP, VS Code |

---

## Features

- **Role-based authentication** — separate signup, login, and dashboard flows for patients and clinicians
- **Session management** — secure session handling with server-side validation
- **Dream logging** — multi-step questionnaire (Q1–Q8) capturing description, mood tags, symbol annotations, sleep quality, and contextual details
- **Nightmare tracking** — separate entry flow and dedicated page, stored independently in the database
- **Full CRUD** — create, read, update, and delete dream and nightmare entries directly through the interface
- **Sleep Overview** — line chart visualising sleep quality trends across all recorded entries
- **Mood Tracker** — horizontal bar chart showing the frequency of each recorded emotion
- **Reports** — clinicians can write and assign reports to individual patients; patients can view reports from their dashboard
- **Custom tags** — users can create personal mood and symbol tags stored per account
- **Password validation** — regex-based validation on all auth forms
- **Password visibility toggle** — show/hide password on all login and signup pages

---

## Demo Accounts

Pre-loaded accounts are available for testing. You are also welcome to create new accounts from the signup page to experience the full registration and onboarding flow.

### Demo Patient accounts

| Name | Email | Password |

| Merve Uzuner | uzunermerveee@gmail.com | asd123@ |
| John Smith | johnsmith@gmail.com | asd123! |

### Demo Clinician accounts

| Name | Email | Password |

| Nora Seed | noraseed@myclinic.com | qwe123@ |
| Mariana Luton | marianaluton@researchers.org | zxc123@ |

---

## Database Schema

The application uses a MySQL database named `dream lab`, managed locally via XAMPP and phpMyAdmin. The schema consists of five tables.

| Table | Description |
|---|---|
| `users` | Stores account credentials and role assignments (`patient` / `clinician`) |
| `dreams` | Complete dream records including mood, sleep quality, symbols, and questionnaire responses |
| `nightmares` | Follows the same structure as `dreams`; stored independently for separate display |
| `reports` | Clinician-authored assessments linked to patients via foreign key |
| `user_tags` | Custom mood and symbol tags created by individual users |

### Table Reference

#### users
| Column | Type | Notes |
|---|---|---|
| id | INT | PK, AUTO_INCREMENT |
| name | VARCHAR | — |
| surname | VARCHAR | — |
| email | VARCHAR | — |
| password | VARCHAR | Hashed via Werkzeug |
| role | VARCHAR | `patient` or `clinician` |

#### dreams / nightmares
| Column | Type | Notes |
|---|---|---|
| id | INT | PK, AUTO_INCREMENT |
| title | VARCHAR | — |
| date | DATE | — |
| description | TEXT | — |
| mood | VARCHAR | — |
| sleep_qualitiy | INT | Note: intentional typo preserved for DB consistency |
| symbols | VARCHAR | — |
| user_id | INT | FK → users.id |

#### reports
| Column | Type | Notes |
|---|---|---|
| id | INT | PK |
| patient_id | INT | FK → users.id |
| clinician_id | INT | FK → users.id |
| title | VARCHAR | — |
| content | TEXT | — |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

#### user_tags
| Column | Type | Notes |
|---|---|---|
| id | INT | PK |
| user_id | INT | FK → users.id |
| tag_type | VARCHAR | e.g. `mood`, `symbol` |
| tag_name | VARCHAR | — |

---

## Getting Started

### Prerequisites

- Python 3.x
- XAMPP (for MariaDB and phpMyAdmin)
- pip

### Installation

1. **Download and extract** the project zip file into a folder of your choice.

2. **Start XAMPP** and ensure Apache and MySQL services are running.

3. **Import the database** — open phpMyAdmin (`http://localhost/phpmyadmin`), create a database named `dream lab`, and import the provided `.sql` file.

4. **Open a terminal** inside the project folder and activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the application:**
   ```bash
   python3 app.py
   ```

7. Open your browser and go to `http://127.0.0.1:5000`

---

## Project Structure

```
DreamLab/
├── app.py                      # Main Flask application, all routes
├── requirements.txt
├── static/
│   ├── bg_video.mp4            # Index page background video
│   ├── index.css
│   ├── dashboard.css
│   ├── clinician-dashboard.css
│   ├── my_dreams.css
│   ├── nightmares.css
│   ├── sleep_overview.css
│   ├── mood_tracker.css
│   ├── reports.css
│   ├── settings.css
│   └── ...                     # Additional page stylesheets
└── templates/
    ├── index.html              # Landing page
    ├── dashboard.html          # Patient dashboard
    ├── clinician-dashboard.html
    ├── my_dreams.html
    ├── nightmares.html
    ├── dream_detail.html
    ├── nightmare_detail.html
    ├── sleep_overview.html
    ├── mood_tracker.html
    ├── reports.html
    ├── report_detail.html
    ├── settings.html
    ├── q1.html – q8.html       # Dream questionnaire steps
    └── ...                     # Additional templates
```

---

## Authentication

Authentication is handled via Flask's session mechanism. Passwords are hashed on registration using Werkzeug's built-in security utilities and verified on login. Role assignment (`patient` / `clinician`) is stored in the `users` table and checked at the route level to enforce access control — clinician routes are not accessible to patient accounts, and vice versa.

---

## Data Visualisation

DreamLab uses **Chart.js** as its data visualisation API, loaded via CDN. Chart data is retrieved live from the MariaDB database through Flask backend routes, processed server-side, and passed to the frontend via Jinja2 for rendering. Two chart types are implemented: a line chart for sleep quality trends and a horizontal bar chart for mood frequency.

---

## Further Development

Several areas are identified for future iteration:

- **Full clinician dashboard** — patient record browsing, annotation, and report generation workflows
- **Search and filtering** — filter dream and nightmare entries by date, mood, or symbol tag
- **Clinician–patient messaging** — in-platform communication linked to individual entries
- **Dream export** — PDF export of a patient's full journal history including chart summaries
- **Mobile responsiveness** — optimised layout for late-night mobile journaling use

---

## Notes

- The `sleep_qualitiy` column name contains a typo that was preserved intentionally throughout the codebase for database consistency.
- The database name `dream lab` includes a space; queries must wrap it in backticks.
- The application is configured for local development only and is not production-ready as-is.

---

*Developed by Merve Uzuner — SAE Institute London.*
