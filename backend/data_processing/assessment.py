from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List


QUESTION_MARKS = 10
TOTAL_QUESTIONS = 10
TOTAL_SCORE = QUESTION_MARKS * TOTAL_QUESTIONS


def load_question_bank() -> List[Dict]:
    question_path = Path(__file__).resolve().parents[1] / "data" / "assessment_questions.json"
    with question_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_proficiency_band(score: int) -> str:
    if score >= 80:
        return "Expert"
    if score >= 45:
        return "Intermediate"
    return "Beginner"


def get_career_band_recommendation(proficiency: str) -> Dict:
    mapping = {
        "Beginner": {
            "proficiency": "Beginner",
            "companyTypes": ["Service-based companies"],
            "salaryBandLPA": "3-4 LPA",
            "jobLevel": "Entry-level",
            "guidance": "Focus on fundamentals, projects, and internships before targeting advanced roles.",
        },
        "Intermediate": {
            "proficiency": "Intermediate",
            "companyTypes": ["Service-based companies", "Early-stage product companies"],
            "salaryBandLPA": "8-10 LPA",
            "jobLevel": "Junior to mid-level",
            "guidance": "Strengthen practical implementation and interview problem-solving to move into product teams.",
        },
        "Expert": {
            "proficiency": "Expert",
            "companyTypes": ["Product-based companies", "Service-based companies"],
            "salaryBandLPA": "10+ LPA (product), 3-10 LPA (service)",
            "jobLevel": "Mid to advanced",
            "guidance": "Target high-impact roles with strong portfolio depth and advanced specialization.",
        },
    }
    return mapping.get(proficiency, mapping["Beginner"])


def _normalize_skill(skill: str) -> str:
    return skill.strip().lower()


def select_assessment_questions(desired_role: str, user_skills: List[str], total_questions: int = TOTAL_QUESTIONS) -> List[Dict]:
    bank = load_question_bank()
    role_tokens = {_normalize_skill(token) for token in desired_role.replace("-", " ").split() if token.strip()}
    skill_tokens = {_normalize_skill(skill) for skill in user_skills if skill.strip()}
    relevance_tokens = role_tokens.union(skill_tokens)

    ranked = []
    for question in bank:
        question_skill = _normalize_skill(str(question.get("skill", "")))
        overlap = int(question_skill in relevance_tokens)
        ranked.append((overlap, random.random(), question))

    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    selected = [item[2] for item in ranked[:total_questions]]

    public_questions = []
    for question in selected:
        public_questions.append(
            {
                "id": question["id"],
                "skill": question["skill"],
                "question": question["question"],
                "options": question["options"],
                "marks": QUESTION_MARKS,
            }
        )
    return public_questions


def evaluate_assessment(answers: List[Dict]) -> Dict:
    bank = load_question_bank()
    answer_key = {question["id"]: question["answerIndex"] for question in bank}
    question_skill_map = {question["id"]: question["skill"] for question in bank}

    obtained = 0
    evaluated = 0
    skill_breakdown: Dict[str, Dict] = {}

    for item in answers[:TOTAL_QUESTIONS]:
        question_id = str(item.get("questionId", "")).strip()
        selected_index = item.get("selectedIndex")
        if question_id not in answer_key or not isinstance(selected_index, int):
            continue

        evaluated += 1
        skill = question_skill_map[question_id]
        is_correct = selected_index == answer_key[question_id]
        if is_correct:
            obtained += QUESTION_MARKS

        if skill not in skill_breakdown:
            skill_breakdown[skill] = {"correct": 0, "attempted": 0}
        skill_breakdown[skill]["attempted"] += 1
        if is_correct:
            skill_breakdown[skill]["correct"] += 1

    max_possible = TOTAL_SCORE
    proficiency = get_proficiency_band(obtained)

    skill_scores = []
    for skill, stats in skill_breakdown.items():
        attempted = stats["attempted"]
        correct = stats["correct"]
        score_pct = round((correct / attempted) * 100, 2) if attempted else 0
        skill_scores.append(
            {
                "skill": skill,
                "correct": correct,
                "attempted": attempted,
                "scorePercent": score_pct,
            }
        )

    skill_scores.sort(key=lambda item: item["scorePercent"], reverse=True)

    return {
        "score": obtained,
        "maxScore": max_possible,
        "proficiency": proficiency,
        "evaluatedQuestions": evaluated,
        "careerBand": get_career_band_recommendation(proficiency),
        "skillScores": skill_scores,
    }
