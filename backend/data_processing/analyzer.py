from __future__ import annotations

from difflib import get_close_matches
from dataclasses import dataclass
from typing import Dict, List, Set

import numpy as np
import pandas as pd


@dataclass
class RecommendationResult:
    desired_role: str
    user_skills: List[str]
    role_match_score: float
    missing_skills: List[str]
    recommended_skills: List[str]
    suggested_roles: List[Dict]


class SkillGapAnalyzer:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()
        self._normalize()

    def _normalize(self) -> None:
        self.df["role"] = self.df["role"].str.strip().str.lower()
        self.df["skill"] = self.df["skill"].str.strip().str.lower()
        self.df["year"] = self.df["year"].astype(int)
        self.df["demand_score"] = self.df["demand_score"].astype(float)

    def _skills_by_role(self) -> Dict[str, Set[str]]:
        grouped = self.df.groupby("role")["skill"].apply(set)
        return grouped.to_dict()

    def _latest_year(self) -> int:
        return int(self.df["year"].max())

    def _skill_trend_scores(self) -> pd.DataFrame:
        yearly = self.df.groupby(["year", "skill"], as_index=False)["demand_score"].sum()
        pivot = yearly.pivot(index="skill", columns="year", values="demand_score").fillna(0)

        years = sorted(pivot.columns.tolist())
        if len(years) < 2:
            pivot["trend_score"] = pivot[years[-1]]
        else:
            first = pivot[years[0]]
            last = pivot[years[-1]]
            delta = last - first
            pivot["trend_score"] = delta + (0.3 * last)

        pivot = pivot.reset_index()[["skill", "trend_score"]]
        return pivot.sort_values("trend_score", ascending=False)

    def _role_demand(self) -> pd.DataFrame:
        latest = self._latest_year()
        role_scores = (
            self.df[self.df["year"] == latest]
            .groupby("role", as_index=False)["demand_score"]
            .sum()
            .sort_values("demand_score", ascending=False)
        )
        return role_scores

    def _resolve_desired_role(self, desired_role: str, user_skill_set: Set[str], role_skill_map: Dict[str, Set[str]]) -> str:
        desired_role = desired_role.strip().lower()
        available_roles = list(role_skill_map.keys())

        if desired_role in role_skill_map:
            return desired_role

        for role in available_roles:
            if desired_role and (desired_role in role or role in desired_role):
                return role

        fuzzy_matches = get_close_matches(desired_role, available_roles, n=1, cutoff=0.5)
        if fuzzy_matches:
            return fuzzy_matches[0]

        desired_tokens = {token for token in desired_role.replace("-", " ").split() if token}
        if desired_tokens:
            token_ranked_roles = []
            for role in available_roles:
                role_tokens = {token for token in role.replace("-", " ").split() if token}
                overlap = len(desired_tokens.intersection(role_tokens))
                union = len(desired_tokens.union(role_tokens))
                similarity = (overlap / union) if union else 0.0
                token_ranked_roles.append((role, overlap, similarity))

            token_ranked_roles.sort(key=lambda item: (item[1], item[2]), reverse=True)
            if token_ranked_roles and token_ranked_roles[0][1] > 0:
                return token_ranked_roles[0][0]

        if user_skill_set:
            role_demand_df = self._role_demand()
            demand_map = dict(zip(role_demand_df["role"], role_demand_df["demand_score"]))

            scored_roles = []
            for role, skills in role_skill_map.items():
                if not skills:
                    continue
                overlap = len(skills.intersection(user_skill_set))
                jaccard = overlap / len(skills.union(user_skill_set)) if skills.union(user_skill_set) else 0
                scored_roles.append((role, overlap, jaccard, demand_map.get(role, 0.0)))

            scored_roles.sort(key=lambda item: (item[1], item[2], item[3]), reverse=True)
            if scored_roles and scored_roles[0][1] > 0:
                return scored_roles[0][0]

        return self._role_demand().head(1)["role"].iloc[0]

    def recommend(self, desired_role: str, user_skills: List[str], top_n_roles: int = 5) -> RecommendationResult:
        desired_role = desired_role.strip().lower()
        user_skill_set = {skill.strip().lower() for skill in user_skills if skill.strip()}

        role_skill_map = self._skills_by_role()
        desired_role = self._resolve_desired_role(desired_role, user_skill_set, role_skill_map)

        target_skills = role_skill_map.get(desired_role, set())
        overlap = target_skills.intersection(user_skill_set)
        role_match_score = (len(overlap) / len(target_skills) * 100) if target_skills else 0

        missing_skills = sorted(target_skills.difference(user_skill_set))

        trend_df = self._skill_trend_scores()
        recommended_skills = (
            trend_df[trend_df["skill"].isin(missing_skills)]
            .head(8)["skill"]
            .tolist()
        )

        role_scores = []
        role_demand_df = self._role_demand()
        demand_map = dict(zip(role_demand_df["role"], role_demand_df["demand_score"]))
        max_demand = max(demand_map.values()) if demand_map else 1

        for role, skills in role_skill_map.items():
            if not skills:
                continue
            match_ratio = len(skills.intersection(user_skill_set)) / len(skills)
            normalized_demand = demand_map.get(role, 0) / max_demand
            score = (match_ratio * 85.0) + (normalized_demand * 15.0)
            role_scores.append(
                {
                    "role": role,
                    "match_percentage": round(match_ratio * 100, 2),
                    "market_demand": round(float(demand_map.get(role, 0)), 2),
                    "composite_score": round(float(score), 2),
                }
            )

        suggested_roles = sorted(role_scores, key=lambda item: item["composite_score"], reverse=True)[:top_n_roles]

        return RecommendationResult(
            desired_role=desired_role,
            user_skills=sorted(user_skill_set),
            role_match_score=round(role_match_score, 2),
            missing_skills=missing_skills,
            recommended_skills=recommended_skills,
            suggested_roles=suggested_roles,
        )

    def trending_roles(self, top_n: int = 10) -> List[Dict]:
        role_demand_df = self._role_demand().head(top_n)
        return role_demand_df.to_dict(orient="records")

    def trending_skills(self, top_n: int = 10) -> List[Dict]:
        trend_df = self._skill_trend_scores().head(top_n)
        trend_df["trend_score"] = trend_df["trend_score"].round(2)
        return trend_df.to_dict(orient="records")

    def power_bi_export(self) -> Dict[str, pd.DataFrame]:
        latest = self._latest_year()
        role_demand = self._role_demand()
        skill_demand_by_year = self.df.groupby(["year", "skill"], as_index=False)["demand_score"].sum()
        latest_role_skills = self.df[self.df["year"] == latest][["role", "skill", "demand_score"]]

        return {
            "role_demand": role_demand,
            "skill_demand_by_year": skill_demand_by_year,
            "latest_role_skills": latest_role_skills,
        }
