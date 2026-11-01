# Cyber Malancy Academy — Course Portal Starter

A beginner-friendly Flask starter project for a course portal featuring:
- Responsive landing page and course catalogue
- Web Development, Python Programming, and Full-Stack Python starter courses
- Lesson pages with explanations, examples, and exercises
- Student registration and login
- Password hashing
- SQLite-backed lesson completion tracking
- Student dashboard with progress indicators

## Requirements
- Python 3.10 or newer
- Internet access for the first install (to install Flask). Google Fonts are optional and only affect typography.

## Run locally on Windows
1. Extract the ZIP file.
2. Open the extracted `cyber_malancy_course_portal` folder in VS Code.
3. Open Terminal in VS Code.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run:
   ```bat
   .venv\Scripts\activate.bat
   ```

5. Install the requirements:
   ```bash
   python -m pip install -r requirements.txt
   ```
6. Start the website:
   ```bash
   python app.py
   ```
7. Open `http://127.0.0.1:5000` in your browser.

## Run on Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Then visit `http://127.0.0.1:5000`.

## Important before public deployment
This is a learning starter, not a production-audited platform.

- Change `app.secret_key` in `app.py` to a long random secret and load it from an environment variable.
- Turn off Flask debug mode in production.
- Use HTTPS and secure cookie settings.
- Add CSRF protection to forms.
- Add rate limiting, email verification, password reset, privacy/terms pages, backups, and logging.
- Review every lesson and expand the starter curriculum before treating it as a complete paid course.
- The sample contact page is a placeholder; it does not send messages.
- There is no admin content editor yet; lessons are currently defined in `COURSES` inside `app.py`.
- Quizzes, certificates, payments, video uploads, and admin roles are not implemented in this starter.

## Project structure
```text
cyber_malancy_course_portal/
├── app.py
├── requirements.txt
├── README.md
├── portal.db              # created automatically on first run
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── courses.html
│   ├── course_detail.html
│   ├── lesson.html
│   ├── auth.html
│   ├── dashboard.html
│   ├── about.html
│   ├── contact.html
│   └── 404.html
└── static/
    ├── style.css
    └── main.js
```

## Adding a lesson
Open `app.py` and find the `COURSES` list. Each course contains modules, and each module contains lesson tuples with:
1. Title
2. Short summary
3. Lesson text
4. HTML example content
5. Practical exercise

Keep the tuple format consistent when adding new lessons.
