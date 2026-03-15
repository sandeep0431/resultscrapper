from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_COLUMNS = ["Registration Number", "Name", "SGPA", "CGPA"]


def build_student_dataframe(records: list[dict]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=BASE_COLUMNS)

    df = pd.DataFrame(records).rename(
        columns={
            "regd_no": "Registration Number",
            "name": "Name",
            "sgpa": "SGPA",
            "cgpa": "CGPA",
        }
    )

    df["SGPA"] = pd.to_numeric(df["SGPA"], errors="coerce")
    df["CGPA"] = pd.to_numeric(df["CGPA"], errors="coerce")
    return df[BASE_COLUMNS]


def build_ranking_dataframe(records: list[dict], metric: str) -> pd.DataFrame:
    metric = metric.upper()
    if metric not in {"SGPA", "CGPA"}:
        raise ValueError("metric must be either 'SGPA' or 'CGPA'")

    df = build_student_dataframe(records)
    if df.empty:
        return pd.DataFrame(columns=["Rank", "Registration Number", "Name", metric])

    df = df.dropna(subset=[metric])
    df = df.sort_values(
        by=[metric, "Registration Number"],
        ascending=[False, True],
        kind="mergesort",
    ).reset_index(drop=True)
    df["Rank"] = df[metric].rank(ascending=False, method="min").astype(int)

    return df[["Rank", "Registration Number", "Name", metric]]


def save_dataframe_to_excel(df: pd.DataFrame, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_paths = [output_path]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate_paths.append(output_path.with_name(f"{output_path.stem}_{timestamp}{output_path.suffix}"))

    for candidate_path in candidate_paths:
        try:
            df.to_excel(candidate_path, index=False)
            return candidate_path
        except PermissionError:
            continue

    raise PermissionError(
        f"Unable to write Excel output. Close '{output_path.name}' if it is open and try again."
    )


def format_top_students(df: pd.DataFrame, metric: str, limit: int = 10) -> str:
    metric = metric.upper()
    if df.empty:
        return f"Top {limit} Students by {metric}\n\nNo valid student results were found."

    lines = [f"Top {limit} Students by {metric}", ""]
    for _, row in df.head(limit).iterrows():
        lines.append(f"{int(row['Rank'])}. {row['Name']} - {row[metric]:.2f}")
    return "\n".join(lines)
