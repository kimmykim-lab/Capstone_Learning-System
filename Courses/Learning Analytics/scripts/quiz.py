import json
import random
from pathlib import Path

# This script assumes it lives in: Learning Analytics/scripts/quiz.py
BASE_DIR = Path(__file__).resolve().parents[1]  # Learning Analytics/
DERIVED_DIR = BASE_DIR / "Derived"
QUIZ_OUT_DIR = BASE_DIR / "Outputs" / "Quizzes"


def ensure_dirs():
    QUIZ_OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def find_latest_day_structured() -> Path:
    # Finds latest Day-XX_structured.json based on XX
    candidates = list(DERIVED_DIR.glob("Day-*_structured.json"))
    if not candidates:
        raise FileNotFoundError(f"No structured day files found in: {DERIVED_DIR}")

    def day_num(p: Path) -> int:
        # Day-02_structured.json -> 2
        name = p.stem  # Day-02_structured
        try:
            return int(name.split("-")[1].split("_")[0])
        except Exception:
            return -1

    candidates.sort(key=day_num)
    latest = candidates[-1]
    if day_num(latest) < 0:
        raise ValueError("Could not parse day number from structured file names.")
    return latest


def make_quiz_items_from_prompt(prompt: dict) -> list[dict]:
    """
    Minimal quiz generator.
    - For reading: concept check, definition, example, contrast
    - For exercise: steps, constraints, reasoning, evaluation
    """
    p_type = (prompt.get("type") or "").lower()
    domain = prompt.get("domain") or ""
    text = prompt.get("text") or ""

    items = []

    if p_type == "reading":
        items = [
            {"id": "Q1", "type": "short", "question": f"[{domain}] Summarize the main idea of the reading prompt in 1-2 sentences.\nPrompt: {text}", "answer_key": "Should capture the core idea accurately."},
            {"id": "Q2", "type": "concept", "question": f"[{domain}] Name 2 key concepts you used or would need to explain this topic.", "answer_key": "Two relevant concepts."},
            {"id": "Q3", "type": "example", "question": f"[{domain}] Give one concrete example that illustrates the prompt.", "answer_key": "An example consistent with the prompt."},
            {"id": "Q4", "type": "contrast", "question": f"[{domain}] What is one common misunderstanding about this topic, and how would you correct it?", "answer_key": "Misconception + correction."}
        ]

    elif p_type == "exercise":
        items = [
            {"id": "Q1", "type": "checklist", "question": f"[{domain}] What is the intended output of today’s exercise? Write it clearly.\nPrompt: {text}", "answer_key": "Defines the expected artifact/output."},
            {"id": "Q2", "type": "steps", "question": f"[{domain}] List the 3-5 steps you would follow to complete the exercise.", "answer_key": "Reasonable ordered steps."},
            {"id": "Q3", "type": "constraint", "question": f"[{domain}] What is one constraint or trade-off you faced (or would face) and why?", "answer_key": "Constraint + justification."},
            {"id": "Q4", "type": "reflection", "question": f"[{domain}] Write one line: what did you learn about your decision-making or preferences?", "answer_key": "A reflective one-liner."}
        ]

    else:
        # fallback if type missing
        items = [
            {"id": "Q1", "type": "short", "question": f"Summarize today’s prompt in 1-2 sentences.\nPrompt: {text}", "answer_key": "Summary matches prompt."},
            {"id": "Q2", "type": "reflection", "question": "Write one line: what did you learn today?", "answer_key": "A reflective one-liner."}
        ]

    return items


def render_quiz_markdown(day: str, date_str: str, prompt: dict, items: list[dict]) -> str:
    prompt_id = prompt.get("prompt_id", "")
    p_type = prompt.get("type", "")
    domain = prompt.get("domain", "")
    text = prompt.get("text", "")

    lines = []
    lines.append(f"# Day {day} Quiz")
    lines.append("")
    lines.append(f"- Date: {date_str}")
    lines.append(f"- prompt_id: {prompt_id}")
    lines.append(f"- type: {p_type}")
    lines.append(f"- domain: {domain}")
    lines.append("")
    lines.append("## Prompt")
    lines.append(text)
    lines.append("")
    lines.append("## Questions")
    lines.append("")
    for q in items:
        lines.append(f"### {q['id']}")
        lines.append(q["question"])
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("")
        lines.append("")
    lines.append("---")
    lines.append("## Answer Key (for evaluation)")
    lines.append("")
    for q in items:
        lines.append(f"- {q['id']}: {q.get('answer_key', '')}")
    lines.append("")
    return "\n".join(lines)


def main():
    ensure_dirs()

    structured_path = find_latest_day_structured()
    data = load_json(structured_path)

    day = data.get("day", "")
    date_str = data.get("date", "")
    prompt = data.get("prompt", {}) or {}

    items = make_quiz_items_from_prompt(prompt)
    random.shuffle(items)

    md = render_quiz_markdown(day, date_str, prompt, items)

    out_path = QUIZ_OUT_DIR / f"Day-{day}_Quiz.md"
    out_path.write_text(md, encoding="utf-8")

    print("Done.")
    print("Loaded:", structured_path)
    print("Wrote:", out_path)


if __name__ == "__main__":
    main()