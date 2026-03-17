from pathlib import Path

import pandas as pd


def load_job_data(csv_path: str | None = None) -> pd.DataFrame:
    default_path = Path(__file__).resolve().parents[1] / "data" / "job_postings.csv"
    path = Path(csv_path) if csv_path else default_path
    dataframe = pd.read_csv(path)

    if {"role", "skills"}.issubset(set(dataframe.columns)):
        dataframe = _expand_role_skill_catalog(dataframe)

    required_columns = {"year", "role", "skill", "demand_score"}
    missing = required_columns.difference(set(dataframe.columns))
    if missing:
        raise ValueError(f"Missing required columns in dataset: {sorted(missing)}")

    catalog_path = Path(__file__).resolve().parents[1] / "data" / "role_skill_catalog.csv"
    if catalog_path.exists() and path.resolve() != catalog_path.resolve():
        catalog_df = pd.read_csv(catalog_path)
        if {"role", "skills"}.issubset(set(catalog_df.columns)):
            catalog_expanded_df = _expand_role_skill_catalog(
                catalog_df,
                year=int(dataframe["year"].max()),
                default_demand=float(dataframe["demand_score"].median()),
            )
            dataframe = pd.concat([dataframe, catalog_expanded_df], ignore_index=True)

    dataframe = dataframe.drop_duplicates(subset=["year", "role", "skill"], keep="last")

    return dataframe


def _expand_role_skill_catalog(dataframe: pd.DataFrame, year: int = 2026, default_demand: float = 75.0) -> pd.DataFrame:
    expanded_rows = []
    for row in dataframe.to_dict(orient="records"):
        role = str(row.get("role", "")).strip()
        skills_raw = str(row.get("skills", ""))
        if not role:
            continue

        skills = [skill.strip() for skill in skills_raw.split("|") if skill.strip()]
        for skill in skills:
            expanded_rows.append(
                {
                    "year": int(row.get("year", year)),
                    "role": role,
                    "skill": skill,
                    "demand_score": float(row.get("demand_score", default_demand)),
                }
            )

    return pd.DataFrame(expanded_rows, columns=["year", "role", "skill", "demand_score"])
