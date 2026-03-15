# Skill Gap Analyzer

Data-driven career intelligence platform for students.

## Features

- Secure user authentication (Register + Login)
- Student input: desired role + current skills
- 100-mark skill assessment test before recommendation
- Proficiency classification: Beginner (<45), Intermediate (45-79), Expert (80+)
- Skill gap analysis against job market demand
- Personalized recommended skills to learn
- Suggested career roles ranked by fit + demand
- Company type and salary band recommendations based on proficiency
- Trending roles and skills from yearly job data
- Power BI-ready CSV export endpoints

## Project Structure

```
Skill_Gap_Analyzer/
├── backend/
│   ├── app/
│   ├── data/
│   ├── data_processing/
│   ├── app.py
│   └── requirements.txt
└── frontend/
    ├── src/
    ├── package.json
    └── vite.config.js
```

## Backend Setup (Flask + Pandas + SQLAlchemy)

1. Open terminal in `backend`.
2. Create virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Optional: set DB URL (`.env`):

   ```env
   DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/skill_gap
   ```

   If not set, SQLite is used (`skill_gap.db`).

5. Run API:

   ```powershell
   python app.py
   ```

Backend runs at `http://localhost:5000`.

## Frontend Setup (React + Tailwind)

1. Open terminal in `frontend`.
2. Install dependencies:

   ```powershell
   npm install
   ```

3. Set API base URL in `.env` (optional):

   ```env
   VITE_API_BASE_URL=http://localhost:5000/api
   ```

4. Run frontend:

   ```powershell
   npm run dev
   ```

Frontend runs at `http://localhost:5173`.

## API Endpoints

- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/assessment/questions`
- `POST /api/assessment/submit`
- `POST /api/recommend`
- `GET /api/trends/roles`
- `GET /api/trends/skills`
- `GET /api/export/role_demand`
- `GET /api/export/skill_demand_by_year`
- `GET /api/export/latest_role_skills`

### New Flow

1. User registers/logs in.
2. Student enters desired role and existing skills.
3. System generates a 10-question assessment (100 marks).
4. Student submits answers.
5. System computes score and proficiency band.
6. Final recommendations include:
   - skill gap
   - recommended skills
   - suggested roles
   - company type + salary band guidance

### Recommendation Request Example

```json
{
  "desiredRole": "Data Analyst",
  "skills": ["Excel", "Tableau"]
}
```

## Power BI Integration

Use **Get Data > Web** in Power BI and connect to:

- `http://localhost:5000/api/export/role_demand`
- `http://localhost:5000/api/export/skill_demand_by_year`
- `http://localhost:5000/api/export/latest_role_skills`

## Notes

- Dataset source file: `backend/data/job_postings.csv`
- Role-skill catalog file: `backend/data/role_skill_catalog.csv`
- You can replace dataset with larger real job-posting data using columns:
  - `year`
  - `role`
  - `skill`
  - `demand_score`
- You can also maintain a role catalog using columns:
   - `role`
   - `skills` (pipe-separated, e.g. `Python|SQL|Power BI`)
