import json
import random
from datetime import date
from pathlib import Path

# This script assumes it lives in: Learning Analytics/scripts/generate_day.py
BASE_DIR = Path(__file__).resolve().parents[1]  # Learning Analytics/
INPUTS_DIR = BASE_DIR / "Inputs"
DERIVED_DIR = BASE_DIR / "Derived"
DAILY_DIR = BASE_DIR / "Daily_Logs"

PROMPT_POOL_PATH = INPUTS_DIR / "Prompt_Pool.json"
INTEREST_MAP_PATH = INPUTS_DIR / "simple_interest_map.json"  # optional


def ensure_dirs():
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_text_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def save_json_if_missing(path: Path, obj) -> bool:
    if path.exists():
        return False
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def pick_domain_from_intent(intent: str, interest_map: dict) -> str | None:
    if not intent or not interest_map:
        return None

    text = intent.lower()
    hits = []

    for keyword, domain in interest_map.items():
        if keyword.lower() in text:
            hits.append(domain)

    if not hits:
        return None

    # pick the most frequent domain among hits
    return max(set(hits), key=hits.count)


def pick_prompt(prompt_pool: list, domain: str | None = None) -> dict:
    if domain:
        filtered = [p for p in prompt_pool if p.get("domain") == domain]
        if filtered:
            return random.choice(filtered)

    # fallback: random from whole pool
    return random.choice(prompt_pool)


def next_day_number() -> str:
    # Find existing Day-XX_Log.md and pick next number
    existing = sorted(DAILY_DIR.glob("Day-*_Log.md"))
    if not existing:
        return "01"

    nums = []
    for p in existing:
        name = p.name  # Day-01_Log.md
        try:
            n = int(name.split("_")[0].split("-")[1])
            nums.append(n)
        except Exception:
            pass

    if not nums:
        return "02"

    return f"{max(nums) + 1:02d}"


def main():
    ensure_dirs()

    prompt_pool = load_json(PROMPT_POOL_PATH)
    if not prompt_pool or not isinstance(prompt_pool, list):
        raise FileNotFoundError(
            f"Prompt pool not found or invalid: {PROMPT_POOL_PATH}\n"
            f"Make sure Prompt_Pool.json exists and is a JSON array."
        )

    interest_map = load_json(INTEREST_MAP_PATH)
    if interest_map is None:
        interest_map = {}  # optional

    # Optional: user intent input
    print("Type your learning intent (or press Enter to pick randomly).")
    intent = input("> ").strip()

    domain = pick_domain_from_intent(intent, interest_map)
    chosen = pick_prompt(prompt_pool, domain=domain)

    day_num = next_day_number()
    today = date.today().isoformat()

    prompt_id = chosen.get("id", "")
    prompt_type = chosen.get("type", "")
    prompt_domain = chosen.get("domain", "")
    prompt_text = chosen.get("prompt", "")

    # 1) Create Day log (human-readable)
    log_path = DAILY_DIR / f"Day-{day_num}_Log.md"
    log_content = (
        f"# Day {day_num} - Learning Log\n\n"
        f"Date: {today}\n\n"
        f"## Selected Prompt\n"
        f"- prompt_id: {prompt_id}\n"
        f"- type: {prompt_type}\n"
        f"- domain: {prompt_domain}\n\n"
        f"### Prompt\n"
        f"{prompt_text}\n\n"
        f"## Your Work\n"
        f"- Output:\n"
        f"- Notes:\n\n"
        f"## Reflection\n"
        f"- Feeling:\n"
        f"- Realization:\n"
        f"- One-line note:\n"
    )
    log_created = save_text_if_missing(log_path, log_content)

    # 2) Create structured json template (machine-readable)
    structured_path = DERIVED_DIR / f"Day-{day_num}_structured.json"
    structured_obj = {
        "day": day_num,
        "date": today,
        "source": "prompt_pool",
        "prompt": {
            "prompt_id": prompt_id,
            "type": prompt_type,
            "domain": prompt_domain,
            "text": prompt_text
        },
        "user_intent": intent,
        "output": {
            "artifact_type": "",
            "artifact": ""
        },
        "reflection": {
            "feeling": "",
            "realization": "",
            "one_line_note": ""
        },
        "analysis": {
            "dominant_topics": [],
            "repeated_concepts": [],
            "abstraction_level": None
        }
    }
    structured_created = save_json_if_missing(structured_path, structured_obj)

    print("\nDone.")
    print("Log created:", log_created, "->", log_path)
    print("Structured created:", structured_created, "->", structured_path)
    if domain:
        print("Matched domain:", domain)
    else:
        print("Matched domain: (none, random prompt)")


if __name__ == "__main__":
    main()