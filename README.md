🚨 Emergency Evacuation Planner Pro

AI-powered web application for safe and efficient evacuation planning using advanced pathfinding algorithms and real-time hazard avoidance.

📌 Overview

Emergency Evacuation Planner Pro is a full-stack web application that helps users:

Design building layouts
Mark hazards (fire, smoke, blocked paths, etc.)
Calculate the safest evacuation routes
Visualize paths in real-time

It uses the A* (A-Star) Algorithm with hazard-aware cost functions to ensure optimal and safe evacuation.

🚀 Features
🧠 Smart A* Pathfinding
Finds shortest + safest path
Considers hazard intensity and type
🔥 Dynamic Hazard Detection
Fire, smoke, chemical, structural hazards
Real-time avoidance
📊 Dashboard & Analytics
Buildings count
Paths generated
Hazard statistics
🏢 Building Management
Create custom grid-based buildings
Multi-floor support
🎯 Real-time Visualization
Interactive grid system
Live path rendering
🔐 User Authentication
Register / Login system
Secure password hashing
💾 Export Feature
Download evacuation paths as JSON
🛠️ Tech Stack
🔹 Backend
Python (Flask)
SQLAlchemy (ORM)
PostgreSQL (Database)
Flask-Login (Authentication)
🔹 Frontend
HTML, CSS, Bootstrap
Jinja2 Templating Engine
JavaScript
🔹 Algorithm
A* (A-Star) Pathfinding Algorithm
Euclidean Distance Heuristic
🧠 How A* Algorithm Works

The system calculates the best path using:

g(n): Cost from start node
h(n): Heuristic (Euclidean distance)
f(n) = g(n) + h(n)

Additional logic:

High hazard = higher cost
Blocked areas = avoided completely
📁 Project Structure
AI-Based-Evacuation-main/
│
├── app.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── buildings.html
│   ├── map.html
│   ├── evacuation.html
│   ├── 404.html
│   ├── 500.html
│   └── 403.html
│
├── static/
│   ├── css/
│   └── js/
│
└── README.md
⚙️ Installation & Setup
🔹 1. Clone the repository
git clone   https://github.com/divyanshudobhal/Evacuation-System/new/master
cd AI-Based-Evacuation-main
🔹 2. Install dependencies
python -m pip install flask flask_sqlalchemy flask_login psycopg2-binary
🔹 3. Setup PostgreSQL
Create database:
CREATE DATABASE evacuation_db;
Update config in app.py:
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:YOUR_PASSWORD@localhost:5432/evacuation_db'
🔹 4. Run the application
python app.py
🔹 5. Open in browser
http://localhost:5000
👤 Demo Credentials
Username: demo
Password: demo123
📊 Use Cases
Building safety planning
Fire evacuation simulations
Disaster management systems
Smart city safety solutions
🔮 Future Improvements
AI-based real-time sensor integration
Mobile application support
Multi-user collaboration
3D building visualization
IoT-based hazard detection
🏆 Conclusion

This project demonstrates:

Real-world problem solving
Algorithm implementation (A*)
Full-stack development
Database integration
Secure authentication
👨‍💻 Author

Divyanshu Dobhal
B.Tech Student | Computer Science
Passionate about technology, AI & real-world solutions

⭐ Acknowledgment

Inspired by real-world emergency management systems and safety engineering concepts.
