# MindBloom - Self Discovery Web App

A full-stack web application for self-discovery, journaling, personality tests, and personal growth tracking. Inspired by Breeze Self Discovery.

## Features

### 🏠 Home
- Weekly calendar view
- Daily routine tasks (auto-generated + custom)
- Task completion tracking
- Self-discovery quest progress (complete 3 tests to unlock reward)

### 📔 Journal
- 4 journal types: Release Worry, Calm Anxiety, Feeling Angry, Feeling Happy
- Each type has 4 guided questions
- Mood slider (1-5 scale with emoji)
- Feeling word chips (20 options)
- Activity tags (20 options)
- Photo upload
- Entry history with mood tracking

### 🧪 Tests
- 6 personality/psychology tests (True/False format, max 13 questions each)
  - Personality Type, Emotional Intelligence, Stress Resilience
  - Self-Confidence, Mindfulness Awareness, Communication Style
- Search functionality
- Featured test banner
- Horizontal scrollable test cards
- Progress tracking with dot navigation
- Score-based results with personalized feedback

### 🌱 Growth
- Personal growth assessment (15 questions across categories)
- Score visualization
- Category-based results (Thriving/Growing/Developing/Beginning)
- Personalized tips and recommendations
- Past assessment history

### 👤 Profile
- User avatar with initials
- Stats dashboard (journal entries, tests taken, assessments)
- Edit display name
- Change password
- Logout

### 🔐 Auth
- User registration with validation
- Login with JWT authentication
- Protected routes
- Persistent sessions (7-day token expiry)

---

## Tech Stack

- **Frontend**: React 18, Vite, React Router v6
- **Backend**: Python Django
- **Database**: MySQL
- **Auth**: JWT + Django password hashing

---

## Prerequisites

Make sure you have the following installed:

1. **Python 3.8+** → [Download Python](https://www.python.org/downloads/)
2. **Node.js 18+** → [Download Node.js](https://nodejs.org/)
3. **pip** (comes with Python)
4. **npm** (comes with Node.js)

To verify, run:
```
python --version
node --version
npm --version
```

---

## Database Setup

MindBloom now uses one persistent MySQL database for all app data. The Django backend creates tables and seeds reference data against that same database.

### 1. Install MySQL

Install MySQL Server 8.x and make sure the service is running.

Verify that the MySQL client works:

```powershell
mysql --version
```

### 2. Create the Database and User Once

Open a MySQL shell as an administrator and run:

```sql
CREATE DATABASE mindbloom CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'mindbloom_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON mindbloom.* TO 'mindbloom_user'@'localhost';
FLUSH PRIVILEGES;
```

This is a one-time setup. After that, the app keeps using the same `mindbloom` database.

If you are using a remote MySQL server, replace `'localhost'` with the appropriate host and allow that host in the user definition.

### 3. Configure Environment Variables

Create a backend `.env` file or set environment variables in your terminal:

```powershell
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=mindbloom_user
MYSQL_PASSWORD=your_strong_password
MYSQL_DATABASE=mindbloom
```

You can also point the app to a full MySQL connection string with `DATABASE_URL`, for example:

```powershell
DATABASE_URL=mysql+pymysql://mindbloom_user:your_strong_password@localhost:3306/mindbloom?charset=utf8mb4
```

### 4. Automatic Setup on First Run

When you start the backend, it will:

1. Connect to the existing `mindbloom` database using the environment variables above.
2. Create all application tables with Django migrations sync mode if they are missing.
3. Seed any missing default journal prompts, tests, and growth questions without duplicating existing rows.

If you need to reset the schema, drop the `mindbloom` database once, recreate it, and restart the backend.

## How to Run the Project

### Step 1: Clone / Navigate to the Project

```powershell
cd "C:\Users\sumit\WArp test\mindbloom"
```

### Step 2: Set Up the Backend

Open a terminal and run:

```powershell
# Navigate to the backend directory
cd "C:\Users\sumit\WArp test\mindbloom\backend"

# Create a Python virtual environment
python -m venv venv

# Activate the virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# macOS / Linux (bash/zsh):
source venv/bin/activate

# If you get an execution policy error on PowerShell, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install Python dependencies
pip install -r requirements.txt

# Make sure MySQL is running and the database exists.
# If you created a .env file, load it before starting the app.

# Bootstrap the database and run the backend server
python app.py bootstrap_db
python app.py
```

The backend will start at **http://127.0.0.1:5000**

You should see:
```
Database bootstrapped successfully!
```

### Step 3: Set Up the Frontend

Open a **new/second terminal** and run:

```powershell
# Navigate to the frontend directory
cd "C:\Users\sumit\WArp test\mindbloom\frontend"

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start at **http://localhost:3000**

### Production / Deployment Notes

For a production-style deployment:

1. Set the backend environment variables from [backend/.env.example](backend/.env.example).
2. Set `DJANGO_DEBUG=False` and configure `DJANGO_ALLOWED_HOSTS` for your server name or IP.
3. Set `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` to the frontend origin.
4. Build the frontend with `npm run build` and serve the generated `dist/` folder.
5. Set `VITE_API_BASE_URL` in [frontend/.env.example](frontend/.env.example) if the frontend is hosted on a different origin than the backend.
6. Use `gunicorn` to serve the Django app behind a reverse proxy such as Nginx, Apache, or a cloud load balancer.

Example backend launch in production:

```powershell
cd backend
gunicorn mindbloom.wsgi:application --bind 0.0.0.0:8000
```

### Step 4: Open the App

Open your browser and go to: **http://localhost:3000**

1. Click **Sign Up** to create a new account
2. Fill in your details (display name, username, email, password)
3. You'll be automatically logged in and taken to the Home page
4. Explore all 5 tabs: Home, Journal, Tests, Growth, Profile

---

## Project Structure

```
mindbloom/
├── backend/
│   ├── app.py              # Django launcher entry point
│   ├── models.py           # Database models (User, Journal, Tests, etc.)
│   ├── seed_data.py        # Seed data for tests, prompts, assessments
│   ├── requirements.txt    # Python dependencies
│   ├── uploads/            # Uploaded photos
│   └── routes/
│       ├── auth.py         # Register, Login, Get User
│       ├── home.py         # Daily tasks, Quest progress
│       ├── journal.py      # Journal entries, Prompts, Options
│       ├── tests.py        # Test definitions, Questions, Results
│       ├── growth.py       # Assessment questions, Results
│       └── profile.py      # Profile update, Change password
│
├── frontend/
│   ├── index.html          # HTML entry point
│   ├── package.json        # Node.js dependencies
│   ├── vite.config.js      # Vite config with backend proxy
│   └── src/
│       ├── main.jsx        # React entry point
│       ├── App.jsx         # Router + Auth wrapper
│       ├── index.css       # All styles (purple-indigo theme)
│       ├── api/
│       │   └── client.js   # API client for all endpoints
│       ├── context/
│       │   └── AuthContext.jsx  # Auth state management
│       ├── components/
│       │   └── Layout.jsx  # Bottom navigation layout
│       └── pages/
│           ├── Login.jsx       # Login page
│           ├── Register.jsx    # Registration page
│           ├── Home.jsx        # Home with calendar + tasks
│           ├── Journal.jsx     # Journal types + entries list
│           ├── JournalEntry.jsx # Journal form (questions, mood, feelings)
│           ├── Tests.jsx       # Tests list with search
│           ├── TakeTest.jsx    # True/False test flow
│           ├── Growth.jsx      # Growth assessment
│           └── Profile.jsx     # User profile + settings
│
└── README.md
```

---

## Color Theme

| Color       | Hex       | Usage            |
|------------|-----------|------------------|
| Primary    | #6C63FF   | Purple-Indigo    |
| Secondary  | #FF6B9D   | Coral-Pink       |
| Accent     | #00D2FF   | Cyan             |
| Success    | #4CAF50   | Green            |
| Warning    | #FFB74D   | Orange           |
| Background | #F8F9FE   | Light Lavender   |

---

## Troubleshooting

### "execution policy" error on Windows
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Backend port already in use
Change the port in `backend/app.py`:
```python
app.run(debug=True, port=5001)
```
Then update `frontend/vite.config.js` proxy target accordingly.

### Frontend can't connect to backend
Make sure both servers are running simultaneously in separate terminals.

### Reset the database
Drop and recreate the `mindbloom` database in MySQL, then run `python app.py bootstrap_db` again. It will recreate the tables and seed missing data automatically.

## **Machine Learning / Anomaly Detection**

MindBloom includes an anomaly-detection pipeline that watches for unusual patterns in a user’s mood, journaling, and activity history. It does not diagnose anyone. Its job is to raise a reviewable alert when the app sees a combination of signals that looks risky or different from the user’s normal pattern.

### What the model uses
- Mood history from journals, including the latest mood and recent mood trend.
- Daily task progress, including how many tasks were completed and the completion ratio.
- Recent test activity, so the model can see whether engagement suddenly changed.
- Journal note length.
- Simple note sentiment, based on positive and negative words.
- Risk keyword counts for phrases such as `hopeless`, `worthless`, `suicide`, or `self harm`.

### What the model does
- Builds a numeric feature vector for each user record.
- Scales the features and trains an Isolation Forest.
- Trains an autoencoder when TensorFlow is available.
- Combines the anomaly scores into a single risk score.
- Flags high-scoring rows as alerts.
- Stores retrain jobs in the database so the admin UI can show job status and logs.

### How it helps the user
- Catches concerning changes earlier than manual review alone.
- Gives admins a simple queue of alerts to inspect.
- Creates an audit trail for acknowledge / resolve actions.
- Keeps the app responsive even if TensorFlow is not installed, because it can fall back to Isolation Forest only.

### Training and scoring flow
1. Extract feature data from the app database.
2. Train the anomaly model and save artifacts in `backend/backend/ml_models/`.
3. Run scoring on new or recent data.
4. Create `Alert` records for high-risk rows.
5. Review alerts in the admin dashboard and record actions in `AlertAudit`.

### Admin review workflow
- New alerts appear in the admin dashboard.
- An admin can acknowledge or resolve an alert.
- Each action is logged so the review history is visible later.
- Retrain jobs can be launched from the dashboard and monitored by job status.

### Short FAQ
- **Is this a diagnosis model?** No. It is an anomaly detector for screening and review.
- **Does it replace a clinician or counselor?** No. It only helps prioritize cases for human review.
- **What happens if TensorFlow is missing?** Training still works with an Isolation Forest fallback.
- **What is saved after training?** The scaler, Isolation Forest, metadata, and autoencoder when available.
- **Where is the model used in the app?** In the scoring job and in the admin alert workflow.

Protected API endpoints exposed for the dashboard:
- `GET /api/admin/alerts`
- `GET /api/admin/alerts/stats`
- `GET /api/admin/alerts/{id}`
- `POST /api/admin/alerts/{id}/acknowledge`
- `POST /api/admin/alerts/{id}/resolve`
- `POST /api/admin/alerts/score`

### Quick Commands

Start by extracting data (example):

```powershell
cd backend
# activate venv
python manage.py extract_ml_data --start 2025-01-01 --end 2025-06-30
python -m api.ml_training.train_anomaly --config config/anomaly.yml
python -m api.ml_training.evaluate_anomaly --model backend/ml_models/anomaly_ensemble.pkl --test-file backend/ml_data/test.parquet
```

And to run the periodic scorer (example using Celery beat or cron):

```bash
python -m api.ml_models.score_recent --model backend/ml_models/anomaly_ensemble.pkl --window 24h
```

---

If you want, I can now:
- scaffold the `backend/api/ml_models/` and `backend/api/ml_data_pipeline/` folders with starter code,
- add the `alerts` DB migration and a Django admin view stub,
- or create the training script and a small sample dataset extractor. Tell me which first step you prefer.
