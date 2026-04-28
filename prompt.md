# 📚 Study Planner

A full-featured **Study Planner web application** built using **Python, Streamlit, and SQLite**.

This app helps students manage study tasks, track deadlines, visualize workload, and receive intelligent study suggestions using AI.

---

## 🎯 Project Goal

The goal of this project is to build a **realistic and functional Streamlit application** that demonstrates:

* Strong Python fundamentals
* Clean and modular code structure
* Database integration
* Data visualization (data science)
* Responsible and meaningful use of AI tools

---

## 🚀 Features

| Feature                            | Description                                              |
| ---------------------------------- | -------------------------------------------------------- |
| **Dashboard**                      | Overview of total, completed, pending, and overdue tasks |
| **Add Task**                       | Form with validation to create study tasks               |
| **Manage Tasks**                   | Search, filter, sort, update, and delete tasks           |
| **Analytics (Data Science Bonus)** | Interactive charts showing workload and trends           |
| **AI Suggestions (AI Bonus)**      | Personalized study plan using Gemini or rule-based logic |
| **Database**                       | SQLite database automatically created and managed        |

---

## 🗂 Project Structure

```
study-planner/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
│
├── data/
│   └── study_planner.db
│
├── src/
│   ├── database.py
│   ├── utils.py
│   ├── ai_suggestions.py
│   └── seed_data.py
│
└── pages_app/
    ├── dashboard.py
    ├── add_task.py
    ├── manage_tasks.py
    ├── analytics_page.py
    └── ai_page.py
```

---

## ⚙️ Setup Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Enable AI

Create `.env` file:

```env
GEMINI_API_KEY=your_key_here
```

If no key is provided, the app will still work using a rule-based suggestion system.

### 3. (Optional) Add demo data

```bash
python -m src.seed_data
```

### 4. Run the app

```bash
streamlit run app.py
```

---

## 🧠 AI Feature (Bonus)

The app includes an **AI-powered study suggestion system**:

* Uses **Gemini API** when available
* Falls back to a **rule-based system** if no API key is provided

The AI analyzes:

* Task priorities
* Deadlines
* Estimated study hours
* Subject distribution

Then generates:

* Study plan
* Task prioritization
* Time management advice

---

## 📊 Data Science Feature (Bonus)

The Analytics page provides:

* Tasks distribution by subject
* Task status breakdown
* Study hours per subject
* Workload trend over time

These visualizations help users understand their study patterns and improve planning decisions.

---

## 🗃️ Database

SQLite is used for simplicity and portability:

* No external setup required
* Automatically created on first run

---

## 🧩 Design Decisions

* **Streamlit** → fast development and easy UI
* **SQLite** → lightweight, no server needed
* **Modular structure** → separates UI, logic, and database
* **AI fallback system** → ensures app works without API

---

## 🤖 AI Usage (Required Section)

### AI Tools Used

* Antigravity
* ChatGPT
* Claude

### What AI Was Used For

AI tools were used to:

* Plan project structure and architecture
* Generate initial code scaffolding
* Improve UI and code readability
* Debug errors and refine logic
* Assist in writing documentation

### Prompt Example

The project was built using a structured prompt (`prompt.md`) provided to AI tools.
Example excerpt:

```
Build a Study Planner web app using Streamlit with:
- Task management (CRUD)
- Search, filter, sorting
- SQLite database
- AI suggestion feature
- Data visualization dashboard
```

Additional prompts were used iteratively to refine features and fix issues.

### Workflow Notes

1. Designed project idea manually
2. Used structured prompts with Antigravity to generate base project
3. Used ChatGPT and Claude to refine and debug
4. Manually reviewed, tested, and modified code
5. Integrated all components into final working app

---

## 🧑‍💻 Work Done Without AI

The following parts were completed manually without direct AI generation:

* Understanding and structuring the project workflow
* Organizing files and modular architecture
* Testing all features (CRUD, filters, analytics, AI)
* Debugging runtime errors and fixing integration issues
* Verifying database behavior and UI interactions
* Updating and refining some parts of the code manually
* Ensuring the app meets assignment requirements

---

## ✅ Requirements Checklist

✔ Streamlit app
✔ Python-based
✔ Database integration
✔ Search / filter / sorting
✔ Input validation
✔ Clean UI
✔ AI feature implemented
✔ Data science feature implemented
✔ Organized code structure
✔ README included

---

## ☁️ Deployment

The app can be deployed using **Streamlit Community Cloud**:

1. Upload project to GitHub
2. Connect repository to Streamlit Cloud
3. Set `app.py` as entry point
4. Add API key (optional)
5. Deploy

---

## 📝 License

MIT License — Abdulaziz Alshammari
