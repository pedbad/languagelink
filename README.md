# languagelink
LanguageLink Advising Appointment System - A web-based application that facilitates scheduling and managing language advising appointments between students and teachers. 

# 🏫 LanguageLink Advising System

**LanguageLink** is a web-based application that facilitates scheduling and managing language advising appointments between students and teachers. It is built with **Django** for the backend and **TailwindCSS** for styling.

---

## 🚀 Installation & Setup

### **1️⃣ Clone the Repository**
If you haven’t already, clone the repository:
```sh
git clone https://github.com/your-repo/languagelink.git
cd languagelink

## 2️⃣ Set Up Python Virtual Environment
Ensure Python 3.8+ is installed, then create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # MacOS/Linux
venv\Scripts\activate     # Windows

## 3️⃣ Install Django Dependencies
Install the required Python packages:

pip install -r requirements.txt


## 4️⃣ Install Node.js & Tailwind Dependencies
Ensure Node.js (v16 or later) is installed, then install the necessary dependencies:

npm install

## 5️⃣ Build & Watch Tailwind CSS
To compile and watch Tailwind CSS, use the npm scripts included in package.json:

Build Tailwind once (for production):

npm run build

Watch for changes & auto-update styles (during development):

npm run watch

## Start Django & auto-refresh with BrowserSync:

npm run serve

## 6️⃣ Apply Django Migrations
python manage.py migrate

## 7️⃣ Create a Superuser (Admin)
python manage.py createsuperuser

8️⃣ Run the Django Server
python manage.py runserver

Once the server is running, open http://127.0.0.1:8000 in your browser.




