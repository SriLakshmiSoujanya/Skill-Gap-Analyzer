from __future__ import annotations

import json
from io import BytesIO

from flask import Blueprint, jsonify, request, send_file

from .auth import auth_required, create_auth_token, get_user_from_request, hash_password, verify_password
from data_processing.assessment import evaluate_assessment, get_career_band_recommendation, get_proficiency_band, select_assessment_questions
from data_processing.analyzer import SkillGapAnalyzer
from data_processing.load_jobs import load_job_data

from .database import db
from .models import RecommendationSnapshot, StudentSubmission, TestAttempt, User

api_bp = Blueprint("api", __name__)


def _get_analyzer() -> SkillGapAnalyzer:
    dataframe = load_job_data()
    return SkillGapAnalyzer(dataframe)


@api_bp.get("/health")
def health_check():
    return jsonify({"status": "ok"})


@api_bp.post("/auth/register")
def register():
    payload = request.get_json(silent=True) or {}
    full_name = str(payload.get("fullName", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", "")).strip()

    if not full_name:
        return jsonify({"error": "fullName is required"}), 400
    if not email:
        return jsonify({"error": "email is required"}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists with this email"}), 409

    user = User(full_name=full_name, email=email, password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()

    token = create_auth_token(user.id)
    return jsonify(
        {
            "token": token,
            "user": {
                "id": user.id,
                "fullName": user.full_name,
                "email": user.email,
            },
        }
    )


@api_bp.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", "")).strip()

    if not email or not password:
        return jsonify({"error": "Email and Password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_auth_token(user.id)
    return jsonify(
        {
            "token": token,
            "user": {
                "id": user.id,
                "fullName": user.full_name,
                "email": user.email,
            },
        }
    )


@api_bp.get("/auth/me")
def auth_me():
    user = get_user_from_request()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify(
        {
            "user": {
                "id": user.id,
                "fullName": user.full_name,
                "email": user.email,
            }
        }
    )


@api_bp.post("/recommend")
@auth_required
def recommend():
    payload = request.get_json(silent=True) or {}
    desired_role = str(payload.get("desiredRole", "")).strip()
    skills = payload.get("skills", [])
    test_score = payload.get("testScore")
    proficiency = str(payload.get("proficiency", "")).strip()

    if not desired_role:
        return jsonify({"error": "desiredRole is required"}), 400
    if not isinstance(skills, list):
        return jsonify({"error": "skills must be an array"}), 400

    if isinstance(test_score, (int, float)):
        test_score = int(test_score)
        proficiency = get_proficiency_band(test_score)
    elif not proficiency:
        proficiency = "Beginner"

    analyzer = _get_analyzer()
    result = analyzer.recommend(desired_role=desired_role, user_skills=skills)
    career_band = get_career_band_recommendation(proficiency)

    submission = StudentSubmission(desired_role=desired_role, skills_csv=",".join(result.user_skills))
    db.session.add(submission)
    db.session.flush()

    snapshot = RecommendationSnapshot(
        submission_id=submission.id,
        recommended_roles_json=json.dumps(result.suggested_roles),
        missing_skills_json=json.dumps(result.missing_skills),
        recommended_skills_json=json.dumps(result.recommended_skills),
    )
    db.session.add(snapshot)
    db.session.commit()

    return jsonify(
        {
            "desiredRole": result.desired_role,
            "userSkills": result.user_skills,
            "roleMatchScore": result.role_match_score,
            "missingSkills": result.missing_skills,
            "recommendedSkills": result.recommended_skills,
            "suggestedRoles": result.suggested_roles,
            "proficiency": proficiency,
            "testScore": test_score,
            "careerBand": career_band,
        }
    )


@api_bp.post("/assessment/questions")
@auth_required
def assessment_questions():
    payload = request.get_json(silent=True) or {}
    desired_role = str(payload.get("desiredRole", "")).strip()
    skills = payload.get("skills", [])

    if not desired_role:
        return jsonify({"error": "desiredRole is required"}), 400
    if not isinstance(skills, list):
        return jsonify({"error": "skills must be an array"}), 400

    questions = select_assessment_questions(desired_role=desired_role, user_skills=skills)
    return jsonify(
        {
            "desiredRole": desired_role,
            "totalQuestions": len(questions),
            "totalMarks": 100,
            "questions": questions,
        }
    )


@api_bp.post("/assessment/submit")
@auth_required
def assessment_submit():
    payload = request.get_json(silent=True) or {}
    desired_role = str(payload.get("desiredRole", "")).strip()
    skills = payload.get("skills", [])
    answers = payload.get("answers", [])

    if not desired_role:
        return jsonify({"error": "desiredRole is required"}), 400
    if not isinstance(skills, list):
        return jsonify({"error": "skills must be an array"}), 400
    if not isinstance(answers, list):
        return jsonify({"error": "answers must be an array"}), 400

    evaluation = evaluate_assessment(answers)

    attempt = TestAttempt(
        desired_role=desired_role,
        skills_csv=",".join([str(skill).strip().lower() for skill in skills if str(skill).strip()]),
        score=evaluation["score"],
        max_score=evaluation["maxScore"],
        proficiency=evaluation["proficiency"],
        skill_scores_json=json.dumps(evaluation["skillScores"]),
    )
    db.session.add(attempt)
    db.session.commit()

    return jsonify(evaluation)


@api_bp.get("/trends/roles")
@auth_required
def trending_roles():
    analyzer = _get_analyzer()
    return jsonify({"items": analyzer.trending_roles(top_n=10)})


@api_bp.get("/trends/skills")
@auth_required
def trending_skills():
    analyzer = _get_analyzer()
    return jsonify({"items": analyzer.trending_skills(top_n=10)})


@api_bp.get("/export/<dataset_name>")
@auth_required
def export_for_power_bi(dataset_name: str):
    analyzer = _get_analyzer()
    export_data = analyzer.power_bi_export()

    if dataset_name not in export_data:
        return jsonify({"error": f"dataset '{dataset_name}' not found"}), 404

    df = export_data[dataset_name]
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    buffer = BytesIO(csv_bytes)

    return send_file(
        buffer,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{dataset_name}.csv",
    )
