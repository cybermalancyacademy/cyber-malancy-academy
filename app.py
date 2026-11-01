from turtle import done

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path
from datetime import datetime
import hashlib
from functools import wraps
import smtplib
from email.message import EmailMessage
import os

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "portal.db"
app = Flask(__name__)
@app.context_processor
def inject_unread_count():
    user = get_user()

    if not user:
        return {"unread_count": 0}

    with sqlite3.connect(DB_PATH) as con:
        count = con.execute("""
            SELECT COUNT(*)
            FROM notifications
            WHERE user_id = ? AND is_read = 0
        """, (user["id"],)).fetchone()[0]

    return {"unread_count": count}
app.secret_key = os.environ.get("SECRET_KEY","local-development-only")

COURSES = [
    
    {
        "slug": "introduction-cyber-security",
        "title": "Introduction to Cyber Security",
        "level": "Beginner",
        "description": "Learn the fundamentals of protecting computers, accounts, and digital information.",
        "color": "blue",
        "modules": [
            ("Module 1: Security Basics", [
                ("What Is Cyber Security?", "Understand the purpose of cyber security.", "Cyber security protects computers, networks, applications, and information from unauthorized access and attacks.", "<h3>Key areas</h3><ul><li>Confidentiality</li><li>Integrity</li><li>Availability</li></ul>", "Explain cyber security in your own words."),
                ("Common Cyber Threats", "Recognize common online threats.", "Phishing, malware, weak passwords, and social engineering are common threats. Learning to recognize them helps people stay safer online.", "<p>Think before clicking unfamiliar links or opening unexpected attachments.</p>", "List three common cyber threats."),
                ("Password and Account Safety", "Learn safe account protection practices.", "Use unique passwords, a password manager, and multi-factor authentication when available. Never share your passwords.", "<p>Protect your accounts with strong, unique passwords.</p>", "Write down three ways to protect an online account.")
            ])
        ]
    },
    {
        "slug": "networking-fundamentals",
        "title": "Networking Fundamentals",
        "level": "Beginner",
        "description": "Learn how computer networks, IP addresses, DNS, and routers work.",
        "color": "blue",
        "modules": [
            ("Module 1: Network Basics", [
                ("What Is a Computer Network?", "Understand how devices communicate.", "A computer network connects devices so they can exchange information and share resources.", "<p>Examples include home Wi-Fi networks and the internet.</p>", "Give two examples of computer networks."),
                ("IP Addresses", "Learn how IP addresses identify devices on networks.", "An IP address is a network address used to identify an interface for communication. IPv4 and IPv6 are two common versions.", "<p>Example IPv4 address: 192.168.1.10</p>", "Explain what an IP address is."),
                ("DNS and Routers", "Understand DNS and the role of routers.", "DNS helps translate domain names into IP addresses. Routers forward traffic between networks.", "<p>DNS helps your browser find the server for a domain name.</p>", "Describe one function of DNS and one function of a router.")
            ])
        ]
    },
    {
        "slug": "network-security",
        "title": "Network Security",
        "level": "Beginner to Intermediate",
        "description": "Learn defensive techniques for protecting computer networks.",
        "color": "blue",
        "modules": [
            ("Module 1: Defending Networks", [
                ("Network Security Basics", "Understand the purpose of network defense.", "Network security uses policies and technical controls to protect network devices, traffic, and services.", "<p>Security includes prevention, monitoring, and response.</p>", "Name three goals of network security."),
                ("Firewalls and Filtering", "Learn how firewalls help control traffic.", "A firewall applies rules to network traffic. Rules should allow necessary communication and restrict unauthorized access.", "<p>Firewall rules should be reviewed and maintained.</p>", "Explain what a firewall does."),
                ("Monitoring and Updates", "Learn why monitoring and updates matter.", "Monitoring helps identify unusual activity. Security updates fix known vulnerabilities and should be applied through trusted processes.", "<p>Keep systems updated and investigate unexpected alerts.</p>", "Give two practices that help secure a network.")
            ])
        ]
    },
    {
        "slug": "linux-fundamentals",
        "title": "Linux Fundamentals",
        "level": "Beginner",
        "description": "Learn Linux, the terminal, files, directories, and basic commands.",
        "color": "gold",
        "modules": [
            ("Module 1: Getting Started with Linux", [
                ("What Is Linux?", "Discover Linux and its common uses.", "Linux is an operating-system kernel used in many distributions for desktops, servers, and embedded devices.", "<p>Examples of Linux distributions include Ubuntu and Debian.</p>", "Name two Linux distributions."),
                ("Navigating the Terminal", "Learn basic directory navigation.", "The pwd command displays the current directory, ls lists directory contents, and cd changes directories.", "<pre><code>pwd\nls\ncd Documents</code></pre>", "Explain what pwd, ls, and cd do."),
                ("Managing Files", "Learn basic file and directory commands.", "Commands such as mkdir create directories and cp copies files. Check the target path before changing or deleting files.", "<pre><code>mkdir practice\nls</code></pre>", "Describe how to create a practice directory.")
            ])
        ]
    },
    {
        "slug": "database-fundamentals",
        "title": "Database Fundamentals",
        "level": "Beginner",
        "description": "Learn tables, SQL, queries, and basic database design.",
        "color": "purple",
        "modules": [
            ("Module 1: Database Basics", [
                ("What Is a Database?", "Understand how databases organize information.", "A database stores organized information so applications can retrieve and update it efficiently.", "<p>A student database might store names, courses, and scores.</p>", "Give two examples of information a database can store."),
                ("Tables and Keys", "Learn rows, columns, and primary keys.", "A table contains rows and columns. A primary key uniquely identifies each row.", "<p>A student ID can be a primary key in a student table.</p>", "Explain the purpose of a primary key."),
                ("Introduction to SQL", "Learn basic database queries.", "SQL is used to work with relational databases. SELECT retrieves data, INSERT adds rows, and UPDATE changes existing rows.", "<pre><code>SELECT name FROM students;</code></pre>", "Explain what a SELECT query does.")
            ])
        ]
    },
    {
        "slug": "git-github",
        "title": "Git and GitHub",
        "level": "Beginner",
        "description": "Learn version control and how to manage programming projects.",
        "color": "gold",
        "modules": [
            ("Module 1: Version Control", [
                ("What Is Git?", "Understand version control and project history.", "Git tracks changes to files and helps developers work with different versions of a project.", "<pre><code>git status</code></pre>", "Explain why version control is useful."),
                ("Commits and History", "Learn how to record changes.", "A commit records a snapshot of tracked project changes. Clear commit messages help explain what changed.", "<pre><code>git add .\ngit commit -m \"Add lesson page\"</code></pre>", "Describe the purpose of a commit."),
                ("Introduction to GitHub", "Understand remote repositories.", "GitHub hosts Git repositories online and supports collaboration, code review, and project sharing.", "<p>Never upload passwords, API keys, or other secrets to a repository.</p>", "Explain one difference between Git and GitHub.")
            ])
        ]
    },
    {
        "slug": "app-development",
        "title": "App Development",
        "level": "Beginner",
        "description": "Explore application design, programming logic, interfaces, and testing.",
        "color": "purple",
        "modules": [
            ("Module 1: App Basics", [
                ("What Is App Development?", "Understand how applications are planned and built.", "App development involves planning, designing, programming, testing, and maintaining applications for users.", "<p>Apps can run on phones, computers, or in a web browser.</p>", "Name two types of applications."),
                ("Designing an Interface", "Learn the basics of a clear user interface.", "A good interface uses readable text, consistent layouts, clear navigation, and helpful feedback.", "<p>Sketch a simple screen with a title, input, and button.</p>", "Draw or describe a simple app screen."),
                ("Testing an App", "Learn why testing is important.", "Testing checks whether an application behaves as expected. Test normal inputs, unusual inputs, and error conditions.", "<p>Check that forms show helpful messages when input is missing.</p>", "Give two cases you would test in a sign-up form.")
            ])
        ]
    },
    {
        "slug": "web-development",
        "title": "Web Development",
        "level": "Beginner to Intermediate",
        "description": "Learn HTML, CSS, JavaScript, responsive design, Git, and how to publish websites.",
        "color": "blue",
        "modules": [
            ("Module 1: Getting Started", [
                ("What Is Web Development?", "Understand how websites are planned, built, and delivered to a browser.", "Web development is the process of building and maintaining websites. Frontend development covers what people see and interact with. Backend development handles server-side logic and data. A website usually combines HTML for structure, CSS for presentation, and JavaScript for interactivity.", '<h3>Three core technologies</h3><ul><li><b>HTML</b> gives a page its structure.</li><li><b>CSS</b> controls layout, colors, and typography.</li><li><b>JavaScript</b> adds interaction and dynamic behavior.</li></ul>', "In your own words, explain the difference between frontend and backend development."),
                ("How Websites Work", "Learn the basic journey from a browser request to a website response.", "When you enter a web address, the browser requests resources from a server. The server responds with files or generated content, and the browser renders the page. A domain is a human-readable address; hosting is a service that makes a website available online.", '<h3>Remember</h3><p>A browser is the client. A web server receives requests and returns responses. HTTPS helps protect data while it travels between them.</p>', "Name the browser, server, and one resource a server might return."),
                ("Set Up Your Tools", "Prepare a code editor and a browser for practice.", "Use a code editor such as Visual Studio Code and a modern browser. Create a project folder, then make an index.html file inside it. Keep filenames simple and save your work often.", '<pre><code>my-first-site/\\n  index.html\\n  style.css\\n  script.js</code></pre>', "Create the folder structure shown above on your computer.")
            ]),
            ("Module 2: HTML", [
                ("HTML Document Structure", "Build the skeleton of an HTML page.", "HTML uses elements to describe content. Most pages include a doctype, html element, head section, and body section. The head stores page metadata; the body contains visible page content.", '<pre><code>&lt;!doctype html&gt;\\n&lt;html lang="en"&gt;\\n&lt;head&gt;\\n  &lt;meta charset="UTF-8"&gt;\\n  &lt;meta name="viewport" content="width=device-width, initial-scale=1"&gt;\\n  &lt;title&gt;My First Page&lt;/title&gt;\\n&lt;/head&gt;\\n&lt;body&gt;\\n  &lt;h1&gt;Hello, world!&lt;/h1&gt;\\n  &lt;p&gt;I am learning HTML.&lt;/p&gt;\\n&lt;/body&gt;\\n&lt;/html&gt;</code></pre>', "Create an HTML page with a title, one heading, and two paragraphs."),
                ("Headings, Paragraphs, and Lists", "Organize content clearly using common HTML elements.", "Use h1 through h6 for headings in a meaningful hierarchy. Use p for paragraphs, ul for unordered lists, ol for ordered lists, and li for each list item. Choose elements based on meaning, not just their default appearance.", '<pre><code>&lt;h1&gt;My Learning Goals&lt;/h1&gt;\\n&lt;ul&gt;\\n  &lt;li&gt;Learn HTML&lt;/li&gt;\\n  &lt;li&gt;Practice CSS&lt;/li&gt;\\n&lt;/ul&gt;</code></pre>', "Create a page listing five skills you want to learn."),
                ("Links and Images", "Add navigation links and images with accessible text.", "Use the anchor element to link to another page or website. Use img to display an image and provide useful alt text so people using assistive technology understand its purpose. Only use images you have permission to use.", '<pre><code>&lt;a href="about.html"&gt;About us&lt;/a&gt;\\n&lt;img src="images/classroom.jpg" alt="Students learning together"&gt;</code></pre>', "Add a link to an About page and an image with meaningful alt text.")
            ]),
            ("Module 3: CSS", [
                ("Connecting CSS to HTML", "Style a page using an external stylesheet.", "CSS rules select elements and apply declarations. An external stylesheet keeps presentation separate from page structure and can be reused across many pages.", '<pre><code>/* style.css */\\nbody {\\n  font-family: Arial, sans-serif;\\n  line-height: 1.6;\\n  margin: 2rem;\\n}\\nh1 { color: #2563eb; }</code></pre>', "Change the page font, background, and heading color."),
                ("Box Model, Spacing, and Layout", "Understand content, padding, borders, and margins.", "Every element is laid out as a box. Content is surrounded by padding, a border, and margin. Flexbox and Grid are common tools for building responsive layouts.", '<pre><code>.card {\\n  padding: 1rem;\\n  border: 1px solid #dbeafe;\\n  margin: 1rem 0;\\n  border-radius: 12px;\\n}</code></pre>', "Create a card with padding, a border, and rounded corners."),
                ("Responsive Design", "Make layouts work on phones, tablets, and computers.", "Responsive design adapts a layout to available screen space. Use flexible widths, sensible maximum widths, and media queries. Test your pages at multiple viewport sizes.", '<pre><code>.container { width: min(100% - 2rem, 1100px); margin: auto; }\\n@media (max-width: 600px) {\\n  .columns { display: block; }\\n}</code></pre>', "Make a two-column layout become one column on small screens.")
            ]),
            ("Module 4: JavaScript", [
                ("Variables and Data Types", "Store values and learn common JavaScript data types.", "Use const for values that should not be reassigned and let for values that will change. Common types include strings, numbers, booleans, arrays, objects, null, and undefined.", '<pre><code>const learnerName = "Amina";\\nlet lessonsCompleted = 0;\\nconst isEnrolled = true;\\nconsole.log(learnerName, lessonsCompleted, isEnrolled);</code></pre>', "Create variables for your name, course, and whether you enjoy coding."),
                ("Conditions and Functions", "Make decisions and reuse blocks of code.", "An if statement runs code when a condition is true. A function packages reusable behavior. Give functions clear names and keep each function focused on one task.", '<pre><code>function greet(name) {\\n  return `Welcome, ${name}!`;\\n}\\nif (name) { console.log(greet(name)); }</code></pre>', "Write a function that takes two numbers and returns their sum."),
                ("DOM and Events", "Respond to user actions on a webpage.", "The Document Object Model (DOM) represents a page as objects JavaScript can inspect and update. Event listeners let your code respond to actions such as clicks or form submissions.", '<pre><code>const button = document.querySelector("#helloBtn");\\nbutton.addEventListener("click", () => {\\n  document.querySelector("#message").textContent = "Hello, learner!";\\n});</code></pre>', "Add a button that changes a message when clicked.")
            ])
        ]
    },
    {
        "slug": "python-programming",
        "title": "Python Programming",
        "level": "Beginner to Intermediate",
        "description": "Learn Python fundamentals, data structures, functions, files, databases, and web applications.",
        "color": "gold",
        "modules": [
            ("Module 1: Python Basics", [
                ("What Is Python?", "Discover Python and the kinds of problems it can solve.", "Python is a general-purpose programming language known for readable syntax. It is used for automation, web applications, data analysis, scientific computing, and many other tasks. Start by learning to run a small program and read its output.", '<pre><code>print("Welcome to Cyber Malancy Academy!")</code></pre><p>Output: <code>Welcome to Cyber Malancy Academy!</code></p>', "Write a program that prints your name and the course you are studying."),
                ("Variables and Data Types", "Store information using strings, numbers, and booleans.", "A variable is a name that refers to a value. Common built-in types include str for text, int for whole numbers, float for decimal numbers, and bool for True or False. Python uses indentation to group code.", '<pre><code>'
                'name = "Kabir"\\n'
                'age = 18\\nscore = 87.5\\n'
                'is_student = True\\n'
                'print(name, age, score, is_student)</code></pre>', "Create four variables for a student's name, age, score, and enrollment status."),
                ("Input and Output", "Collect information from a user and display a response.", "The input() function reads text from the user. Convert input to int or float when you need to do numeric calculations. The print() function displays output.", '<pre><code>name = input("What is your name? ")\\n'
                'print(f"Welcome, {name}!")</code></pre>', "Ask the user for their name and favorite programming language, then display both.")
            ]),
            ("Module 2: Operators and Decisions", [
                ("Operators", "Use arithmetic, comparison, and logical operators.", "Arithmetic operators perform calculations. Comparison operators compare values and return booleans. Logical operators and, or, and not combine or reverse conditions.", '<pre><code>price = 1200\\nquantity = 3\\ntotal = price * quantity\\nprint(f"Total: {total}")\\nprint(total >= 3000)</code></pre>', "Write a program that calculates the total cost of three items."),
                ("if, elif, and else", "Choose which code runs based on a condition.", "Conditional statements let a program make decisions. Conditions evaluate to True or False. Indent each block consistently, usually with four spaces.", '<pre><code>score = int(input("Enter score: "))\\n'
                'if score >= 70:\\n  '
                '  print("Excellent")\\n'
                'elif score >= 50:\\n  '
                '  print("Pass")\\nelse:\\n  '
                '  print("Keep practicing")</code></pre>', "Create a grade checker with at least four score bands."),
                ("Loops", "Repeat actions using for and while loops.", "Use for when iterating over a sequence or range. Use while when repetition depends on a condition. Ensure while loops can eventually stop, and use break or continue only when they make the logic clearer.", '<pre><code>for number in range(1, 6):\\n    print(number)</code></pre>', "Print the numbers 1 through 20 and then calculate their sum.")
            ]),
            ("Module 3: Collections and Functions", [
                ("Lists and Tuples", "Store multiple values in an ordered collection.", "Lists are mutable collections, so you can add, remove, or replace items. Tuples are ordered and typically used for fixed collections. Indexes start at zero.", '<pre><code>courses = ["HTML", "CSS", "Python"]\\ncourses.append("JavaScript")\\nprint(courses[0])\\nprint(courses)</code></pre>', "Create a list of five courses, add one more, and print each course."),
                ("Dictionaries and Sets", "Use key-value pairs and unique-value collections.", "A dictionary maps keys to values, which is useful for named records. A set stores unique values and supports set operations such as union and intersection.", '<pre><code>student = {"name": "Amina", "course": "Python"}\\nprint(student["name"])\\nstudent["level"] = "Beginner"</code></pre>', "Represent a student using a dictionary with name, course, and score."),
                ("Functions", "Create reusable blocks of code with parameters and return values.", "Define a function with def. Parameters receive input, and return sends a result back to the caller. Prefer clear names and functions that do one job.", '<pre><code>def add(a, b):\\n    return a + b\\n\\nprint(add(4, 6))</code></pre>', "Write a function that converts Celsius to Fahrenheit.")
            ]),
            ("Module 4: Files, Errors, and Projects", [
                ("Files and JSON", "Read and write files and work with structured data.", "Use with open(...) so files close reliably. Choose an encoding such as UTF-8 for text. JSON can store structured values such as lists and dictionaries.", '<pre><code>with open("notes.txt", "w", encoding="utf-8") as file:\\n    file.write("Keep practicing Python!")</code></pre>', "Save a short learning note to a text file and read it back."),
                ("Error Handling", "Handle expected errors without crashing unexpectedly.", "try and except let a program respond to specific errors. Catch only exceptions you can handle, and provide a helpful message rather than hiding all problems.", '<pre><code>try:\\n  '
                '  age = int(input("Enter age: "))\\n'
                'except ValueError:\\n  '
                '  print("Please enter a whole number.")</code></pre>', "Handle invalid numeric input in a simple calculator."),
                ("Introduction to Flask", "Understand how Python can power a website.", "Flask is a lightweight Python web framework. It maps URLs to Python functions and can render HTML templates. Real applications also need secure configuration, input validation, and a database.", '<pre><code>from flask import Flask\\napp = Flask(__name__)\\n\\n@app.route("/")\\ndef home():\\n    return "Hello from Python!"\\n\\nif __name__ == "__main__":\\n    app.run(debug=True)</code></pre>', "Run a small local Flask app and add a second route.")
            ])
        ]
    },
    {
        "slug": "full-stack-python",
        "title": "Full-Stack Development with Python",
        "level": "Intermediate",
        "description": "Connect a frontend to a Python backend and database to build a complete learning application.",
        "color": "purple",
        "modules": [
            ("Module 1: Backend Foundations", [
                ("Frontend and Backend Together", "Understand how the browser, server, and database work together.", "The frontend presents the user interface. The backend validates requests, applies business rules, and communicates with the database. Never trust browser input alone; validate it on the server.", '<p>Typical flow: browser request → Python route → validation/business logic → database → response.</p>', "Draw the request flow for a student signing in to a course portal."),
                ("Routes and Templates in Flask", "Create routes and render reusable HTML templates.", "A route connects a URL to a Python function. Templates separate HTML presentation from Python logic. Pass only the data a template needs, and escape untrusted content by default.", '<pre><code>from flask import render_template\\n\\n@app.route("/about")\\ndef about():\\n    return render_template("about.html", title="About")</code></pre>', "Create an About page route that renders a template.")
            ]),
            ("Module 2: Data and Accounts", [
                ("Databases with SQLite", "Store users, courses, and lesson progress in a database.", "A relational database stores information in tables. Use primary keys to identify rows and parameterized SQL queries to prevent SQL injection. SQLite is useful for learning and small deployments.", '<pre><code>import sqlite3\\nconnection = sqlite3.connect("learning.db")\\nconnection.execute("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL)")\\nconnection.commit()\\nconnection.close()</code></pre>', "Create a table for courses and insert one course using a parameterized query."),
                ("Authentication and Password Safety", "Understand safe sign-up and sign-in patterns.", "Authentication checks who a user is. Store password hashes rather than plaintext passwords, use established security libraries, protect sessions, validate input, and never commit secret keys to a public repository.", '<p>Use password hashing from a trusted framework library. For a real deployment, enable HTTPS and configure secure cookie settings.</p>', "List three security steps a registration form should follow.")
            ]),
            ("Module 3: Capstone", [
                ("Build a Course Portal", "Plan a complete learning platform with courses, lessons, quizzes, and progress.", "Start with a clear data model: users, courses, modules, lessons, quiz questions, and progress. Build one feature at a time, test it, and keep administrative actions protected by authorization checks.", '<ul><li>Student dashboard</li><li>Course and lesson pages</li><li>Quiz scoring</li><li>Lesson completion tracking</li><li>Admin content management</li></ul>', "Sketch the tables and pages your own course portal needs.")
            ])
        ]
    }
]


def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        con.execute("""CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_key TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            UNIQUE(user_id, lesson_key),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        con.execute("""CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_key TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")
        
        con.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        columns = [
            row[1]
            for row in con.execute("PRAGMA table_info(users)").fetchall()
        ]

        
        if "is_admin" not in columns:
            con.execute(
                "ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0"
            )

        con.execute("""
            CREATE TABLE IF NOT EXISTS certificate_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                certificate_id TEXT NOT NULL UNIQUE,
                student_name TEXT NOT NULL,
                course_name TEXT NOT NULL,
                verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS course_completion_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_slug TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_slug)
            )
        """)
        con.commit()


def get_user():
    user_id = session.get("user_id")
    if not user_id:
        return None

    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT id, username, email, is_admin FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        return dict(row) if row else None

def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = get_user()

        if not user:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))

        if not user.get("is_admin"):
            abort(403)

        return view(*args, **kwargs)

    return wrapped_view

def get_all_users():
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        users = con.execute(
            "SELECT id, username, email FROM users"
        ).fetchall()

    return [dict(user) for user in users]

def flatten_lessons():
    rows = []
    for course in COURSES:
        for mi, (module_name, lessons) in enumerate(course["modules"], start=1):
            for li, lesson in enumerate(lessons, start=1):
                key = f'{course["slug"]}:{mi}:{li}'
                rows.append({
                    "key": key,
                    "slug": course["slug"],
                    "course": course,
                    "module": module_name,
                    "lesson": lesson,
                    "module_num": mi,
                    "lesson_num": li
                })
    return rows

@app.context_processor
def inject_globals():
    return {"current_user": get_user(), "academy_name": "Cyber Malancy Academy"}

@app.route("/")
def index():
    return render_template("index.html", courses=COURSES, lesson_count=len(flatten_lessons()))

@app.route("/courses")
def courses_page():
    return render_template("courses.html", courses=COURSES)


@app.route("/course/<slug>")
def course_detail(slug):
    course = next((c for c in COURSES if c["slug"] == slug), None)
    if not course:
        abort(404)

    completed = set()
    user = get_user()

    if user:
        with sqlite3.connect(DB_PATH) as con:
            completed = {
                r[0] for r in con.execute(
                    "SELECT lesson_key FROM progress WHERE user_id=? AND completed=1",
                    (user["id"],)
                )
            }

    total_lessons = sum(
        len(lessons) for _, lessons in course["modules"]
    )

    completed_lessons = sum(
        1
        for mi, (_, lessons) in enumerate(course["modules"], start=1)
        for li, lesson in enumerate(lessons, start=1)
        if f'{course["slug"]}:{mi}:{li}' in completed
    )

    progress_percent = (
        round((completed_lessons / total_lessons) * 100)
        if total_lessons > 0 else 0
    )

    modules = []

    for mi, (module_name, lessons) in enumerate(course["modules"], start=1):
        module_lessons = []

        for li, lesson in enumerate(lessons, start=1):
            key = f'{course["slug"]}:{mi}:{li}'

            module_lessons.append({
                "key": key,
                "title": lesson[0],
                "description": lesson[1],
                "completed": key in completed,
                "lesson_num": li
            })

        modules.append({
            "name": module_name,
            "lessons": module_lessons,
            "module_num": mi
        })

    return render_template(
        "course_detail.html",
        course=course,
        modules=modules,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        progress_percent=progress_percent
    )

@app.route("/lesson/<slug>/<int:module_num>/<int:lesson_num>")
def lesson_page(slug, module_num, lesson_num):
    course = next((c for c in COURSES if c["slug"] == slug), None)
    if not course or module_num < 1 or module_num > len(course["modules"]):
        abort(404)
    module_name, lessons = course["modules"][module_num - 1]
    if lesson_num < 1 or lesson_num > len(lessons):
        abort(404)
    title, summary, content, example, exercise = lessons[lesson_num - 1]
    key = f"{slug}:{module_num}:{lesson_num}"
    all_lessons = flatten_lessons()
    lesson_keys = [item["key"] for item in all_lessons]
    current_index = lesson_keys.index(key)

    next_lesson = None

    if current_index < len(all_lessons) - 1:
        next_lesson = all_lessons[current_index + 1]
    completed = False
    user = get_user()
    if user:
        with sqlite3.connect(DB_PATH) as con:
            row = con.execute("SELECT completed FROM progress WHERE user_id=? AND lesson_key=?", (user["id"], key)).fetchone()
            completed = bool(row and row[0])
    return render_template(
    "lesson.html",
    course=course,
    module_name=module_name,
    title=title,
    summary=summary,
    content=content,
    example=example,
    exercise=exercise,
    lesson_key=key,
    completed=completed,
    module_num=module_num,
    lesson_num=lesson_num,
    next_lesson=next_lesson
)



@app.post("/lesson/complete")
def complete_lesson():
    user = get_user()
    if not user:
        flash("Please sign in to save your learning progress.", "warning")
        return redirect(url_for("login"))

    lesson_key = request.form.get("lesson_key", "")
    valid_keys = {item["key"] for item in flatten_lessons()}

    if lesson_key not in valid_keys:
        abort(400)

    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            INSERT INTO progress (user_id, lesson_key, completed)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, lesson_key)
            DO UPDATE SET completed=1
        """, (user["id"], lesson_key))
        con.commit()

    
    slug, module_num, lesson_num = lesson_key.split(":")

    all_course_lessons = [
        item for item in flatten_lessons()
        if item["key"].startswith(slug + ":")
    ]

    with sqlite3.connect(DB_PATH) as con:
        completed_count = con.execute("""
            SELECT COUNT(*)
            FROM progress
            WHERE user_id = ?
            AND completed = 1
            AND lesson_key LIKE ?
        """, (user["id"], slug + ":%")).fetchone()[0]

        total_lessons = len(all_course_lessons)

        if total_lessons > 0 and completed_count >= total_lessons:
            already_sent = con.execute("""
                SELECT id FROM course_completion_emails
                WHERE user_id = ? AND course_slug = ?
            """, (user["id"], slug)).fetchone()

            if not already_sent:
                student = con.execute("""
                    SELECT email, username FROM users WHERE id = ?
                """, (user["id"],)).fetchone()

                if student:
                    course_name = slug.replace("-", " ").title()

                    email_sent = send_email_notification(
                        student[0],
                        f"Congratulations! You completed {course_name}",
                        f"Hello {student[1]},\n\n"
                        f"Congratulations! You have completed all lessons "
                        f"in {course_name}.\n\n"
                        "Keep learning with Cyber Malancy Academy!"
                    )

                    if email_sent:
                        con.execute("""
                            INSERT OR IGNORE INTO course_completion_emails
                            (user_id, course_slug)
                            VALUES (?, ?)
                        """, (user["id"], slug))
                        con.commit()

    flash("Lesson completed! Well done.", "success")


    return redirect(url_for(
        "lesson_page",
        slug=slug,
        module_num=int(module_num),
        lesson_num=int(lesson_num)
    ))

QUIZ_QUESTIONS = [
    {
        "question": "What is Python?",
        "options": ["A programming language", "A web browser", "A database", "A computer part"],
        "answer": 0,
        "explanation": "Python is a popular programming language used to build applications, websites, and automate tasks."
    },
    {
        "question": "Which function displays output in Python?",
        "options": ["show()", "echo()", "print()", "write()"],
        "answer": 2,
        "explanation": "The print() function displays information in the output."
    },
    {
        "question": "Which data type is used for text?",
        "options": ["int", "str", "bool", "float"],
        "answer": 1,
        "explanation": "The str data type is used to store text, also called strings."
    },
    {
        "question": "What symbol is commonly used to assign a value to a variable?",
        "options": ["==", ":", "=", "->"],
        "answer": 2,
        "explanation": "The = symbol assigns a value to a variable in Python."
    },
    {
        "question": "What does input() do?",
        "options": ["Deletes a variable", "Receives text from a user", "Repeats a loop", "Closes Python"],
        "answer": 1,
        "explanation": "The input() function receives information entered by the user."
    },
]


WEB_QUIZ_QUESTIONS = [
    {
        "question": "What does HTML stand for?",
        "options": [
            "HyperText Markup Language",
            "HighText Machine Language",
            "Hyper Transfer Main Link",
            "Home Tool Markup Language"
        ],
        "answer": 0
    },
    {
        "question": "Which HTML tag is used to create a hyperlink?",
        "options": ["<link>", "<a>", "<href>", "<url>"],
        "answer": 1
    },
    {
        "question": "What is CSS mainly used for?",
        "options": [
            "Storing data",
            "Creating databases",
            "Styling web pages",
            "Running a server"
        ],
        "answer": 2
    },
    {
        "question": "Which language adds interactivity to web pages?",
        "options": ["HTML", "CSS", "SQL", "JavaScript"],
        "answer": 3
    },
    {
        "question": "Which HTML tag is used to display an image?",
        "options": ["<image>", "<img>", "<picture-text>", "<src>"],
        "answer": 1
    }
]

CYBER_SECURITY_QUESTIONS = [
    {
        "question": "What is the main purpose of cyber security?",
        "options": [
            "To make computers faster",
            "To protect systems and information",
            "To design websites",
            "To create documents"
        ],
        "answer": 1
    },
    {
        "question": "Which of these is a common cyber threat?",
        "options": [
            "Phishing",
            "Typing",
            "Printing",
            "Formatting text"
        ],
        "answer": 0
    },
    {
        "question": "What is multi-factor authentication used for?",
        "options": [
            "To delete files",
            "To speed up the internet",
            "To add another layer of account security",
            "To change a computer screen"
        ],
        "answer": 2
    },
    {
        "question": "What should you do with a suspicious email link?",
        "options": [
            "Click it immediately",
            "Forward it to everyone",
            "Enter your password",
            "Avoid clicking and verify the sender"
        ],
        "answer": 3
    },
    {
        "question": "What does confidentiality mean in information security?",
        "options": [
            "Keeping information accessible only to authorized people",
            "Making every file public",
            "Deleting all information",
            "Sharing passwords"
        ],
        "answer": 0
    }
]

NETWORKING_QUESTIONS = [
    {
        "question": "What is a computer network?",
        "options": [
            "A type of keyboard",
            "A group of connected devices",
            "A programming language",
            "A web browser"
        ],
        "answer": 1
    },
    {
        "question": "What does an IP address identify?",
        "options": [
            "A website logo",
            "A computer or device on a network",
            "A password",
            "An email message"
        ],
        "answer": 1
    },
    {
        "question": "What does DNS do?",
        "options": [
            "Deletes files",
            "Converts domain names into IP addresses",
            "Creates passwords",
            "Runs antivirus software"
        ],
        "answer": 1
    },
    {
        "question": "Which device connects different networks together?",
        "options": [
            "Mouse",
            "Monitor",
            "Router",
            "Printer"
        ],
        "answer": 2
    },
    {
        "question": "Which protocol is commonly used for secure websites?",
        "options": [
            "FTP",
            "HTTP",
            "HTTPS",
            "SMTP"
        ],
        "answer": 2
    }
]

EXTRA_QUIZZES = {
    "network-security": {
        "title": "Network Security",
        "questions": [
            {"question": "What is the main goal of network security?",
             "options": ["To decorate a network", "To protect network systems and data", "To increase screen brightness", "To print documents"],
             "answer": 1},
            {"question": "What does a firewall do?",
             "options": ["Controls network traffic using rules", "Creates websites", "Charges a laptop", "Edits images"],
             "answer": 0},
            {"question": "What is malware?",
             "options": ["A secure password", "A network cable", "Malicious software", "A backup copy"],
             "answer": 2},
            {"question": "Why should software be updated?",
             "options": ["To remove all user accounts", "To fix bugs and known security weaknesses", "To share passwords", "To disable security"],
             "answer": 1},
            {"question": "What should you do if you notice unusual network activity?",
             "options": ["Ignore it forever", "Share your password", "Turn off every security control", "Report it and investigate safely"],
             "answer": 3}
        ]
    },

    "linux-fundamentals": {
        "title": "Linux Fundamentals",
        "questions": [
            {"question": "What is Linux?",
             "options": ["An operating-system kernel", "A web browser", "A database query", "A type of printer"],
             "answer": 0},
            {"question": "Which command lists files and directories?",
             "options": ["pwd", "ls", "cd", "whoami"],
             "answer": 1},
            {"question": "Which command displays the current directory?",
             "options": ["mkdir", "cp", "pwd", "clear"],
             "answer": 2},
            {"question": "Which command creates a directory?",
             "options": ["mkdir", "ls", "pwd", "cat"],
             "answer": 0},
            {"question": "What does the cd command do?",
             "options": ["Lists files", "Changes directory", "Creates a user", "Displays a web page"],
             "answer": 1}
        ]
    },

    "database-fundamentals": {
        "title": "Database Fundamentals",
        "questions": [
            {"question": "What is a database?",
             "options": ["A computer monitor", "A programming error", "An organized collection of information", "A network cable"],
             "answer": 2},
            {"question": "What is a table made up of?",
             "options": ["Rows and columns", "Only images", "Passwords only", "Web browsers"],
             "answer": 0},
            {"question": "What is the purpose of a primary key?",
             "options": ["To style a webpage", "To uniquely identify a row", "To shut down a database", "To connect a keyboard"],
             "answer": 1},
            {"question": "Which SQL command retrieves data?",
             "options": ["DELETE", "DROP", "UPDATE", "SELECT"],
             "answer": 3},
            {"question": "Why should SQL queries use parameters for user input?",
             "options": ["To make text colorful", "To avoid saving data", "To help prevent SQL injection", "To turn off the database"],
             "answer": 2}
        ]
    },

    "git-github": {
        "title": "Git and GitHub",
        "questions": [
            {"question": "What is Git mainly used for?",
             "options": ["Version control", "Browsing the internet", "Editing videos", "Charging devices"],
             "answer": 0},
            {"question": "What does a Git commit record?",
             "options": ["A Wi-Fi password", "A snapshot of project changes", "A browser history", "A computer's temperature"],
             "answer": 1},
            {"question": "Which command shows the working-tree status?",
             "options": ["git start", "git open", "git status", "git screen"],
             "answer": 2},
            {"question": "What is GitHub?",
             "options": ["A computer operating system", "A keyboard", "A programming variable", "An online platform for hosting Git repositories"],
             "answer": 3},
            {"question": "What should you avoid uploading to a public repository?",
             "options": ["A README file", "Passwords and secret API keys", "Your HTML practice page", "A public project description"],
             "answer": 1}
        ]
    },

    "app-development": {
        "title": "App Development",
        "questions": [
            {"question": "What is app development?",
             "options": ["Only typing documents", "Only repairing keyboards", "Planning, building, testing, and maintaining applications", "Only browsing websites"],
             "answer": 2},
            {"question": "What is a user interface (UI)?",
             "options": ["The part of an app users see and interact with", "A database password", "A network cable", "A programming error"],
             "answer": 0},
            {"question": "Why is testing important?",
             "options": ["It makes testing unnecessary", "It checks whether the app behaves as expected", "It removes all features", "It hides every error"],
             "answer": 1},
            {"question": "What is a bug in an application?",
             "options": ["A design color", "A user account", "A successful test", "An error or defect in the software"],
             "answer": 3},
            {"question": "What should a sign-up form do when required information is missing?",
             "options": ["Accept anything silently", "Display the user's password", "Show a helpful validation message", "Delete the application"],
             "answer": 2}
        ]
    },

    "full-stack-python": {
        "title": "Full-Stack Development with Python",
        "questions": [
            {"question": "What does full-stack development usually include?",
             "options": ["Frontend and backend development", "Only typing", "Only computer hardware", "Only database backups"],
             "answer": 0},
            {"question": "What is HTML used for?",
             "options": ["Storing passwords", "Structuring webpage content", "Managing server memory", "Replacing databases"],
             "answer": 1},
            {"question": "What role can Flask play in a Python web application?",
             "options": ["It is a monitor driver", "It is a spreadsheet", "It is a Python web framework", "It is a computer virus"],
             "answer": 2},
            {"question": "What is a database used for in a web application?",
             "options": ["Changing screen brightness", "Drawing keyboard keys", "Replacing HTML", "Storing and retrieving application data"],
             "answer": 3},
            {"question": "Why should passwords be stored as hashes rather than plain text?",
             "options": ["To make them easier to publish", "To improve password security if stored data is exposed", "To display them on every page", "To remove the need for login"],
             "answer": 1}
        ]
    }
}



@app.route("/quiz/python-basics", methods=["GET", "POST"])
def python_basics_quiz():
    user = get_user()
    result = None
    review = []

    if request.method == "POST":
        answers = request.form

        for i, q in enumerate(QUIZ_QUESTIONS):
            selected = answers.get(f"q{i}")

            try:
                selected_index = int(selected) if selected is not None else None
            except ValueError:
                selected_index = None

            valid_answer = (
                selected_index is not None
                and 0 <= selected_index < len(q["options"])
            )

            is_correct = valid_answer and selected_index == q["answer"]

            review.append({
                "question": q["question"],
                "selected": q["options"][selected_index] if valid_answer else "No answer",
                "correct": q["options"][q["answer"]],
                "is_correct": is_correct,
                "explanation": q.get("explanation", "")
            })

        score = sum(1 for item in review if item["is_correct"])

        result = {
            "score": score,
            "total": len(QUIZ_QUESTIONS),
            "percent": round(score * 100 / len(QUIZ_QUESTIONS))
        }

        
        if user:
            with sqlite3.connect(DB_PATH) as con:
                con.execute(
                    """
                    INSERT INTO quiz_results
                    (user_id, quiz_key, score, total)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user["id"], "python-basics", score, len(QUIZ_QUESTIONS))
                )
                con.commit()

                student = con.execute(
                    "SELECT email, username FROM users WHERE id = ?",
                    (user["id"],)
                ).fetchone()

            if student:
                send_email_notification(
                    student[0],
                    "Python Basics Quiz Completed",
                    f"Hello {student[1]},\n\n"
                    f"You have completed the Python Basics quiz.\n"
                    f"Your score: {score}/{len(QUIZ_QUESTIONS)}\n\n"
                    "Keep learning with Cyber Malancy Academy!"
                )
        else:
            flash(
                "Your score is shown, but sign in to save quiz results to your account.",
                "warning"
            )

    latest_result = None

    if user:
        with sqlite3.connect(DB_PATH) as con:
            row = con.execute(
                "SELECT score, total, taken_at FROM quiz_results WHERE user_id=? AND quiz_key=? ORDER BY id DESC LIMIT 1",
                (user["id"], "python-basics")
            ).fetchone()

            if row:
                latest_result = {
                    "score": row[0],
                    "total": row[1],
                    "taken_at": row[2]
                }

    return render_template(
        "quiz.html",
        questions=QUIZ_QUESTIONS,
        result=result,
        latest_result=latest_result,
        review=review
    )


def build_quiz_review(questions, answers):
    review = []

    for i, q in enumerate(questions):
        selected = answers.get(f"q{i}")

        try:
            selected_index = int(selected) if selected is not None else None
        except (TypeError, ValueError):
            selected_index = None

        valid = (
            selected_index is not None
            and 0 <= selected_index < len(q["options"])
        )

        correct_index = q["answer"]

        review.append({
            "question": q["question"],
            "selected": q["options"][selected_index] if valid else "No answer",
            "correct": q["options"][correct_index],
            "is_correct": valid and selected_index == correct_index,
            "explanation": q.get(
                "explanation",
                f"The correct answer is {q['options'][correct_index]}."
            )
        })

    return review


@app.route("/quiz/cyber-security", methods=["GET", "POST"])
def cyber_security_quiz():
    user = get_user()
    result = None
    review = []

    if request.method == "POST":
        review = build_quiz_review(
            CYBER_SECURITY_QUESTIONS,
            request.form
        )

        score = sum(1 for item in review if item["is_correct"])

        result = {
            "score": score,
            "total": len(CYBER_SECURITY_QUESTIONS),
            "percent": round(score * 100 / len(CYBER_SECURITY_QUESTIONS))
        }

        if user:
            with sqlite3.connect(DB_PATH) as con:
                con.execute(
                    """INSERT INTO quiz_results
                    (user_id, quiz_key, score, total)
                    VALUES (?, ?, ?, ?)""",
                    (
                        user["id"],
                        "introduction-cyber-security",
                        score,
                        len(CYBER_SECURITY_QUESTIONS)
                    )
                )
                con.commit()

                student = con.execute(
                    "SELECT email, username FROM users WHERE id = ?",
                    (user["id"],)
                ).fetchone()

            if student:
                send_email_notification(
                    student[0],
                    "Cyber Security Quiz Completed",
                    f"Hello {student[1]},\n\n"
                    "You have completed the Introduction to Cyber Security quiz.\n"
                    f"Your score: {score}/{len(CYBER_SECURITY_QUESTIONS)}\n\n"
                    "Keep learning with Cyber Malancy Academy!"
                )
    latest_result = None

    if user:
        with sqlite3.connect(DB_PATH) as con:
            row = con.execute(
                """SELECT score, total, taken_at
                FROM quiz_results
                WHERE user_id=? AND quiz_key=?
                ORDER BY id DESC LIMIT 1""",
                (user["id"], "introduction-cyber-security")
            ).fetchone()

            if row:
                latest_result = {
                    "score": row[0],
                    "total": row[1],
                    "taken_at": row[2]
                }

    return render_template(
        "quiz.html",
        questions=CYBER_SECURITY_QUESTIONS,
        result=result,
        latest_result=latest_result,
        review=review
    )


@app.route("/quiz/networking-fundamentals", methods=["GET", "POST"])
def networking_quiz():
    user = get_user()
    result = None
    review = []

    if request.method == "POST":
        review = build_quiz_review(NETWORKING_QUESTIONS, request.form)
        score = sum(1 for item in review if item["is_correct"])

        result = {
            "score": score,
            "total": len(NETWORKING_QUESTIONS),
            "percent": round(score * 100 / len(NETWORKING_QUESTIONS))
        }

        
        if user:
            with sqlite3.connect(DB_PATH) as con:
                con.execute(
                    """INSERT INTO quiz_results
                    (user_id, quiz_key, score, total)
                    VALUES (?, ?, ?, ?)""",
                    (user["id"], "networking-fundamentals",
                     score, len(NETWORKING_QUESTIONS))
                )
                con.commit()

                student = con.execute(
                    "SELECT email, username FROM users WHERE id = ?",
                    (user["id"],)
                ).fetchone()

            if student:
                send_email_notification(
                    student[0],
                    "Networking Fundamentals Quiz Completed",
                    f"Hello {student[1]},\n\n"
                    "You have completed the Networking Fundamentals quiz.\n"
                    f"Your score: {score}/{len(NETWORKING_QUESTIONS)}\n\n"
                    "Keep learning with Cyber Malancy Academy!"
                )

        else:
            flash("Sign in to save your quiz results.", "warning")

    latest_result = None

    if user:
        with sqlite3.connect(DB_PATH) as con:
            row = con.execute(
                """SELECT score, total, taken_at
                FROM quiz_results
                WHERE user_id=? AND quiz_key=?
                ORDER BY id DESC LIMIT 1""",
                (user["id"], "networking-fundamentals")
            ).fetchone()

            if row:
                latest_result = {
                    "score": row[0],
                    "total": row[1],
                    "taken_at": row[2]
                }

    return render_template(
        "quiz.html",
        questions=NETWORKING_QUESTIONS,
        result=result,
        latest_result=latest_result,
        review=review
    )


@app.route("/quiz/web-development", methods=["GET", "POST"])
def web_development_quiz():
    user = get_user()
    result = None
    review = []

    if request.method == "POST":
        review = build_quiz_review(WEB_QUIZ_QUESTIONS, request.form)
        score = sum(1 for item in review if item["is_correct"])

        result = {
            "score": score,
            "total": len(WEB_QUIZ_QUESTIONS),
            "percent": round(score * 100 / len(WEB_QUIZ_QUESTIONS))
        }

        
        if user:
            with sqlite3.connect(DB_PATH) as con:
                con.execute(
                    """INSERT INTO quiz_results
                    (user_id, quiz_key, score, total)
                    VALUES (?, ?, ?, ?)""",
                    (user["id"], "web-development",
                     score, len(WEB_QUIZ_QUESTIONS))
                )
                con.commit()

                student = con.execute(
                    "SELECT email, username FROM users WHERE id = ?",
                    (user["id"],)
                ).fetchone()

            if student:
                send_email_notification(
                    student[0],
                    "Web Development Quiz Completed",
                    f"Hello {student[1]},\n\n"
                    "You have completed the Web Development quiz.\n"
                    f"Your score: {score}/{len(WEB_QUIZ_QUESTIONS)}\n\n"
                    "Keep learning with Cyber Malancy Academy!"
                )

        else:
            flash(
                "Sign in to save your quiz results to your account.",
                "warning"
            )

    latest_result = None

    if user:
        with sqlite3.connect(DB_PATH) as con:
            row = con.execute(
                """SELECT score, total, taken_at
                FROM quiz_results
                WHERE user_id=? AND quiz_key=?
                ORDER BY id DESC LIMIT 1""",
                (user["id"], "web-development")
            ).fetchone()

            if row:
                latest_result = {
                    "score": row[0],
                    "total": row[1],
                    "taken_at": row[2]
                }

    return render_template(
        "web_quiz.html",
        questions=WEB_QUIZ_QUESTIONS,
        result=result,
        latest_result=latest_result,
        review=review
    )


@app.route("/quiz/course/<quiz_key>", methods=["GET", "POST"])
def course_quiz(quiz_key):
    quiz = EXTRA_QUIZZES.get(quiz_key)

    if not quiz:
        abort(404)

    questions = quiz["questions"]
    user = get_user()
    result = None
    review = []

    if request.method == "POST":
        review = build_quiz_review(questions, request.form)
        score = sum(1 for item in review if item["is_correct"])

        result = {
            "score": score,
            "total": len(questions),
            "percent": round(score * 100 / len(questions))
        }

        
        if user:
            with sqlite3.connect(DB_PATH) as con:
                con.execute(
                    """INSERT INTO quiz_results
                    (user_id, quiz_key, score, total)
                    VALUES (?, ?, ?, ?)""",
                    (user["id"], quiz_key, score, len(questions))
                )
                con.commit()

                student = con.execute(
                    "SELECT email, username FROM users WHERE id = ?",
                    (user["id"],)
                ).fetchone()

            if student:
                course_name = quiz.get("title", quiz_key.replace("-", " ").title())

                send_email_notification(
                    student[0],
                    f"{course_name} Quiz Completed",
                    f"Hello {student[1]},\n\n"
                    f"You have completed the {course_name} quiz.\n"
                    f"Your score: {score}/{len(questions)}\n\n"
                    "Keep learning with Cyber Malancy Academy!"
                )

        else:
            flash(
                "Sign in to save your quiz results.",
                "warning"
            )

    latest_result = None

    if user:
        with sqlite3.connect(DB_PATH) as con:
            row = con.execute(
                """SELECT score, total, taken_at
                FROM quiz_results
                WHERE user_id=? AND quiz_key=?
                ORDER BY id DESC LIMIT 1""",
                (user["id"], quiz_key)
            ).fetchone()

            if row:
                latest_result = {
                    "score": row[0],
                    "total": row[1],
                    "taken_at": row[2]
                }

    return render_template(
        "quiz.html",
        questions=questions,
        result=result,
        latest_result=latest_result,
        review=review
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if len(username) < 3:
            flash("Username must contain at least 3 characters.", "error")
        elif "@" not in email or "." not in email:
            flash("Please enter a valid email address.", "error")
        elif len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
        else:
            try:
                with sqlite3.connect(DB_PATH) as con:
                    cur = con.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                                      (username, email, generate_password_hash(password)))
                    con.commit()
                    session["user_id"] = cur.lastrowid
                flash("Account created. Welcome to the academy!", "success")
                return redirect(url_for("dashboard"))
            except sqlite3.IntegrityError:
                flash("That username or email is already registered.", "error")
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with sqlite3.connect(DB_PATH) as con:
            con.row_factory = sqlite3.Row
            user = con.execute("SELECT id, password_hash FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            flash("You are now signed in.", "success")
            return redirect(url_for("dashboard"))
        flash("Email or password is incorrect.", "error")
    return render_template("auth.html", mode="login")

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    user = get_user()
    if not user:
        return redirect(url_for("login"))
    all_lessons = flatten_lessons()
    total = len(all_lessons)

    with sqlite3.connect(DB_PATH) as con:
       done = {
        r[0] for r in con.execute(
            "SELECT lesson_key FROM progress WHERE user_id=? AND completed=1",
            (user["id"],)
        )
    }

    quiz_rows = con.execute(
        """SELECT quiz_key, score, total, taken_at
           FROM quiz_results
           WHERE user_id=?
           ORDER BY id DESC""",
        (user["id"],)
    ).fetchall()

    quiz_count = len(quiz_rows)
    quiz_total_score = sum(row[1] for row in quiz_rows)
    quiz_total_questions = sum(row[2] for row in quiz_rows)

    average_score = (
                  round(quiz_total_score * 100 / quiz_total_questions)
                  if quiz_total_questions else 0
                    )
    recent_quizzes = [
    {
        "quiz_key": row[0],
        "score": row[1],
        "total": row[2],
        "taken_at": row[3],
        "percent": round(row[1] * 100 / row[2]) if row[2] else 0
    }
    for row in quiz_rows[:5]
]

    badges = []
    
    if quiz_count >= 1:
        badge_title = "First Quiz Badge"
        badge_message = "Congratulations! You have completed your first quiz."
    
        with sqlite3.connect(DB_PATH) as con:
            existing = con.execute("""
                SELECT id FROM notifications
                WHERE user_id = ? AND title = ?
            """, (user["id"], badge_title)).fetchone()
    
        if not existing:
            create_notification(
                user["id"],
                badge_title,
                badge_message
            )
    
            with sqlite3.connect(DB_PATH) as con:
                student_email = con.execute(
                    "SELECT email FROM users WHERE id = ?",
                    (user["id"],)
                ).fetchone()
    
            if student_email:
                send_email_notification(
                    student_email[0],
                    badge_title,
                    badge_message
                )
    
        badges.append({
            "name": "First Quiz",
            "icon": "🥇",
            "description": "Completed your first quiz"
        })
    
        
    if len(done) >= 5:
        badges.append({
            "name": "Quick Learner",
            "icon": "📚",
            "description": "Completed 5 lessons"
        })

    if quiz_count >= 10:
        badges.append({
            "name": "Quiz Master",
            "icon": "🧠",
            "description": "Completed 10 quizzes"
        })

    if len(done) == total and total > 0:
        badges.append({
            "name": "Course Graduate",
            "icon": "🎓",
            "description": "Completed all course lessons"
        })

    leaderboard_names = [row["username"] for row in leaderboard] if False else []


    leaderboard = con.execute("""
        SELECT
            u.username,
            COALESCE(SUM(q.score), 0) AS total_score,
            COALESCE(SUM(q.total), 0) AS total_questions
        FROM users u
        LEFT JOIN quiz_results q ON q.user_id = u.id
        WHERE u.is_admin = 0
        GROUP BY u.id
        HAVING COUNT(q.id) > 0
        ORDER BY
            (100.0 * SUM(q.score) / NULLIF(SUM(q.total), 0)) DESC,
            SUM(q.score) DESC
        LIMIT 10
    """).fetchall()

    for position, student in enumerate(leaderboard, start=1):
        if student["username"] == user["username"] and position <= 3:
            badges.append({
                "name": "Top 3",
                "icon": "🏆",
                "description": "You are among the top 3 students"
            })
            break


    total = len(all_lessons)
    percent = round(len(done) * 100 / total) if total else 0
    course_progress = []
    for course in COURSES:
        keys = [x["key"] for x in all_lessons if x["course"]["slug"] == course["slug"]]
        count = sum(1 for key in keys if key in done)
        course_progress.append({"course": course, "completed": count, "total": len(keys),
                                 "percent": round(count * 100 / len(keys)) if keys else 0})
    
    return render_template(
    "dashboard.html",
    user=user,
    total=total,
    completed=len(done),
    percent=percent,
    course_progress=course_progress,
    quiz_count=quiz_count,
    average_score=average_score,
    recent_quizzes=recent_quizzes,
    leaderboard=leaderboard,
    badges=badges,
)
def create_notification(user_id, title, message):
    with sqlite3.connect(DB_PATH) as con:
        existing = con.execute("""
            SELECT id FROM notifications
            WHERE user_id = ? AND title = ? AND message = ?
        """, (user_id, title, message)).fetchone()

        if not existing:
            con.execute("""
                INSERT INTO notifications (user_id, title, message)
                VALUES (?, ?, ?)
            """, (user_id, title, message))
def send_email_notification(receiver_email, subject, message):
    sender_email = os.environ.get("EMAIL_ADDRESS")
    sender_password = os.environ.get("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("Email settings are not configured.")
        return False

    email = EmailMessage()
    email["From"] = sender_email
    email["To"] = receiver_email
    email["Subject"] = subject
    email.set_content(message)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(email)

        return True

    except Exception as error:
        print("Email sending failed:", error)
        return False
@app.route("/contact", methods=["GET", "POST"])
def contact():
    user = get_user()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Please fill in all fields.", "error")
        elif "@" not in email:
            flash("Please enter a valid email address.", "error")
        else:
            email_sent = send_email_notification(
                "cybermalancyacademy@gmail.com",
                f"New Contact Message from {name}",
                f"Name: {name}\n"
                f"Email: {email}\n\n"
                f"Message:\n{message}"
            )

            if email_sent:
                flash("Your message has been sent successfully!", "success")
            else:
                flash("Message could not be sent. Please try again later.", "error")

    return render_template("contact.html", user=user)

@app.route("/notifications")
def notifications():
    user = get_user()

    if not user:
        return redirect(url_for("login"))

    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row

        user_notifications = con.execute("""
            SELECT id, title, message, is_read, created_at
            FROM notifications
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user["id"],)).fetchall()
        unread_count = con.execute("""
            SELECT COUNT(*)
            FROM notifications
            WHERE user_id = ? AND is_read = 0
        """, (user["id"],)).fetchone()[0]
            
    return render_template(
        "notifications.html",
        user=user,
        notifications=user_notifications,
        unread_count=unread_count
    )
@app.route("/notifications/mark-read/<int:notification_id>", methods=["POST"])
def mark_notification_read(notification_id):
    user = get_user()

    if not user:
        return redirect(url_for("login"))

    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE id = ? AND user_id = ?
        """, (notification_id, user["id"]))

    return redirect(url_for("notifications"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row

        students = con.execute("""
            SELECT
                u.id,
                u.username,
                u.email,
                u.created_at,
                COUNT(q.id) AS quiz_attempts,
                COALESCE(SUM(q.score), 0) AS total_score,
                COALESCE(SUM(q.total), 0) AS total_questions
            FROM users u
            LEFT JOIN quiz_results q ON q.user_id = u.id
            WHERE u.is_admin = 0
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """).fetchall()
        
        student_performance = con.execute("""
            SELECT
                u.username,
                COUNT(q.id) AS quiz_attempts,
                COALESCE(SUM(q.score), 0) AS total_score,
                COALESCE(SUM(q.total), 0) AS total_questions,
                CASE
                    WHEN COALESCE(SUM(q.total), 0) = 0 THEN 0
                    ELSE ROUND(
                        100.0 * SUM(q.score) / SUM(q.total), 1
                    )
                END AS average_percentage
            FROM users u
            LEFT JOIN quiz_results q ON q.user_id = u.id
            WHERE u.is_admin = 0
            GROUP BY u.id
            ORDER BY average_percentage DESC
        """).fetchall()

        quiz_results = con.execute("""
            SELECT
                u.username,
                u.email,
                q.quiz_key,
                q.score,
                q.total,
                q.taken_at
            FROM quiz_results q
            JOIN users u ON u.id = q.user_id
            WHERE u.is_admin = 0
            ORDER BY q.id DESC
        """).fetchall()

        total_students = con.execute("""
            SELECT COUNT(*) FROM users WHERE is_admin = 0
        """).fetchone()[0]

        total_certificates = con.execute("""
            SELECT COUNT(*) FROM certificate_verifications
        """).fetchone()[0]

        total_quiz_attempts = con.execute("""
            SELECT COUNT(*) FROM quiz_results
        """).fetchone()[0]

        popular_course = con.execute("""
            SELECT course_name, COUNT(*) AS total
            FROM certificate_verifications
            GROUP BY course_name
            ORDER BY total DESC
            LIMIT 1
        """).fetchone()

        certificate_history = con.execute("""
            SELECT
                certificate_id,
                student_name,
                course_name,
                verified_at
            FROM certificate_verifications
            ORDER BY id DESC
        """).fetchall()

    return render_template(
        "admin_dashboard.html",
        students=students,
        student_performance=student_performance,
        quiz_results=quiz_results,
        certificate_history=certificate_history,
        total_students=total_students,
        total_certificates=total_certificates,
        total_quiz_attempts=total_quiz_attempts,
        popular_course=popular_course
    )

import csv
import io
from flask import make_response

@app.route("/admin/export-certificates")
@admin_required
def export_certificates():
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        certificates = con.execute("""
            SELECT
                student_name,
                course_name,
                certificate_id,
                verified_at
            FROM certificate_verifications
            ORDER BY id DESC
        """).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Student",
        "Course",
        "Certificate ID",
        "Verified Date"
    ])

    for certificate in certificates:
        writer.writerow([
            certificate["student_name"],
            certificate["course_name"],
            certificate["certificate_id"],
            certificate["verified_at"]
        ])

    response = make_response("\ufeff" + output.getvalue())
    response.headers["Content-Disposition"] = (
        "attachment; filename=certificate_history.csv"
    )
    response.headers["Content-Type"] = "text/csv; charset=utf-8"

    return response

@app.route("/profile")
def profile():
    user = get_user()

    if not user:
        return redirect(url_for("login"))

    return render_template("profile.html", user=user)

@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    user = get_user()

    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()

        if len(username) < 3:
            flash("Username must contain at least 3 characters.", "error")
        elif "@" not in email or "." not in email:
            flash("Please enter a valid email address.", "error")
        else:
            try:
                with sqlite3.connect(DB_PATH) as con:
                    con.execute(
                        """UPDATE users
                           SET username = ?, email = ?
                           WHERE id = ?""",
                        (username, email, user["id"])
                    )
                    con.commit()

                flash("Your profile has been updated successfully.", "success")
                return redirect(url_for("profile"))

            except sqlite3.IntegrityError:
                flash("That username or email is already in use.", "error")

    return render_template("edit_profile.html", user=user)

@app.route("/profile/change-password", methods=["GET", "POST"])
def change_password():
    user = get_user()

    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        with sqlite3.connect(DB_PATH) as con:
            con.row_factory = sqlite3.Row
            db_user = con.execute(
                "SELECT password_hash FROM users WHERE id = ?",
                (user["id"],)
            ).fetchone()

        if not db_user or not check_password_hash(
            db_user["password_hash"], current_password
        ):
            flash("Your current password is incorrect.", "error")

        elif len(new_password) < 8:
            flash("New password must contain at least 8 characters.", "error")

        elif new_password != confirm_password:
            flash("The new passwords do not match.", "error")

        else:
            new_hash = generate_password_hash(new_password)

            with sqlite3.connect(DB_PATH) as con:
                con.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (new_hash, user["id"])
                )
                con.commit()

            flash("Your password has been changed successfully.", "success")
            return redirect(url_for("profile"))

    return render_template("change_password.html", user=user)

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.route("/certificate/<slug>")
def certificate(slug):
    user = get_user()

    if not user:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    course = next(
        (c for c in COURSES if c["slug"] == slug),
        None
    )

    if course is None:
        abort(404)

    course_lessons = [
        item for item in flatten_lessons()
        if item["course"]["slug"] == slug
    ]

    with sqlite3.connect(DB_PATH) as con:
        completed = {
            row[0]
            for row in con.execute(
                "SELECT lesson_key FROM progress WHERE user_id=? AND completed=1",
                (user["id"],)
            )
        }

    if not course_lessons or not all(
        lesson["key"] in completed
        for lesson in course_lessons
    ):
        flash("Complete all lessons to earn your certificate.", "error")
        return redirect(url_for("course_detail", slug=slug))

    certificate_id = "CMA-" + hashlib.sha256(
        f"{user['id']}:{slug}".encode()
    ).hexdigest()[:10].upper()

    return render_template(
        "certificate.html",
        course=course,
        user=user,
        completion_date=datetime.now().strftime("%d %B %Y"),
        certificate_id=certificate_id
)


@app.route("/verify-certificate", methods=["GET", "POST"])
def verify_certificate():
    certificate_data = None
    message = None

    if request.method == "POST":
        certificate_id = request.form.get(
            "certificate_id", ""
        ).strip().upper()

        for course in COURSES:
            for user in get_all_users():
                expected_id = "CMA-" + hashlib.sha256(
                    f"{user['id']}:{course['slug']}".encode()
                ).hexdigest()[:10].upper()

                if certificate_id == expected_id:
                    course_lessons = [
                        item for item in flatten_lessons()
                        if item["course"]["slug"] == course["slug"]
                    ]

                    with sqlite3.connect(DB_PATH) as con:
                        completed = {
                            row[0] for row in con.execute(
                                "SELECT lesson_key FROM progress "
                                "WHERE user_id=? AND completed=1",
                                (user["id"],)
                            )
                        }

                    if course_lessons and all(
                        lesson["key"] in completed
                        for lesson in course_lessons
                    ):
                        certificate_data = {
                            "student": user["username"],
                            "course": course["title"],
                            "certificate_id": certificate_id
                        }

                        with sqlite3.connect(DB_PATH) as con:
                            con.execute(
                                """INSERT OR IGNORE INTO certificate_verifications
                                (certificate_id, student_name, course_name)
                                VALUES (?, ?, ?)""",
                                (
                                    certificate_id,
                                    user["username"],
                                    course["title"]
                                )
                            )
                    break

            if certificate_data:
                break

        if not certificate_data:
            message = "Certificate not found or not valid."

    return render_template(
        "verify_certificate.html",
        certificate_data=certificate_data,
        message=message
    )

init_db()

if __name__ == "__main__":
    app.run(debug=True)
