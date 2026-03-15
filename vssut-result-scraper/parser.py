from __future__ import annotations

from typing import Optional

from bs4 import BeautifulSoup


def _clean_text(value: str) -> str:
    return " ".join(value.split())


def parse_result_page(html: str, requested_regd_no: str | None = None) -> Optional[dict]:
    soup = BeautifulSoup(html, "lxml")

    for table in soup.find_all("table", class_="table"):
        rows = table.find_all("tr")
        if not rows:
            continue

        table_text = _clean_text(table.get_text(" ", strip=True))
        if "No result found" in table_text:
            return None

        student_name = None
        registration_number = requested_regd_no
        sgpa = None
        cgpa = None

        for row in rows:
            cells = [_clean_text(cell.get_text(" ", strip=True)) for cell in row.find_all(["td", "th"])]
            if not cells:
                continue

            if len(cells) >= 4 and cells[0].lower() == "name" and cells[2].lower().startswith("registration no"):
                student_name = cells[1] or None
                registration_number = cells[3] or registration_number

            for index, cell_value in enumerate(cells[:-1]):
                if cell_value.upper() == "SGPA":
                    try:
                        sgpa = float(cells[index + 1])
                    except (TypeError, ValueError):
                        sgpa = None
                if cell_value.upper() == "CGPA":
                    try:
                        cgpa = float(cells[index + 1])
                    except (TypeError, ValueError):
                        cgpa = None

        if student_name and registration_number and (sgpa is not None or cgpa is not None):
            return {
                "regd_no": str(registration_number),
                "name": student_name,
                "sgpa": sgpa,
                "cgpa": cgpa,
            }

    return None
