from datetime import datetime

from .database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class StudentSubmission(db.Model):
    __tablename__ = "student_submissions"

    id = db.Column(db.Integer, primary_key=True)
    desired_role = db.Column(db.String(120), nullable=False)
    skills_csv = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class RecommendationSnapshot(db.Model):
    __tablename__ = "recommendation_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("student_submissions.id"), nullable=False)
    recommended_roles_json = db.Column(db.Text, nullable=False)
    missing_skills_json = db.Column(db.Text, nullable=False)
    recommended_skills_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class TestAttempt(db.Model):
    __tablename__ = "test_attempts"

    id = db.Column(db.Integer, primary_key=True)
    desired_role = db.Column(db.String(120), nullable=False)
    skills_csv = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    proficiency = db.Column(db.String(32), nullable=False)
    skill_scores_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
