import json
import os
from anthropic import Anthropic, AnthropicError

class AIServiceError(Exception):
    pass


def parse_roadmap(raw_response):
    # Remove markdown formatting if Claude accidentally adds it
    cleaned = raw_response.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        cleaned = cleaned.rsplit("```", 1)[0].strip()

    try:
        roadmap = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError) as error:
        raise AIServiceError("Claude returned invalid JSON") from error

    if not isinstance(roadmap, dict):
        raise AIServiceError("Roadmap must be a JSON object")

    steps = roadmap.get("steps")
    not_now = roadmap.get("not_now")

    if not isinstance(steps, list) or not 5 <= len(steps) <= 9:
        raise AIServiceError("Roadmap must have 5–9 steps")

    if not isinstance(not_now, list) or not 2 <= len(not_now) <= 5:
        raise AIServiceError("Roadmap must have 2–5 not-now items")

    for step in steps:
        if not isinstance(step, dict) or any(
            not isinstance(step.get(field), str) or not step[field].strip()
            for field in ("title", "description", "reasoning", "est_time")
        ):
            raise AIServiceError("Invalid roadmap step")

    for item in not_now:
        if not isinstance(item, dict) or any(
            not isinstance(item.get(field), str) or not item[field].strip()
            for field in ("title", "reasoning")
        ):
            raise AIServiceError("Invalid not-now item")

    return roadmap

def build_prompt(intake):
    return f"""
You are an academic advisor helping a computer science student.

Generate a personalized learning roadmap using this intake:
{json.dumps(intake, indent=2)}

Requirements:
- Return ONLY valid JSON. No markdown or extra text.
- Include 5 to 9 steps.
- Include 2 to 5 not_now items.
- Every step must contain: title, description, reasoning, est_time.
- Every not_now item must contain: title, reasoning.
- Make recommendations realistic for the student's weekly_hours and credit_load.
- Explain recommendations using their actual skills, coursework, and commitments.

Return this JSON structure:
{{
  "steps": [
    {{
      "title": "...",
      "description": "...",
      "reasoning": "...",
      "est_time": "..."
    }}
  ],
  "not_now": [
    {{
      "title": "...",
      "reasoning": "..."
    }}
  ]
}}
"""

def generate_with_claude(intake):
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise AIServiceError("ANTHROPIC_API_KEY is not configured")

    client = Anthropic()

    for attempt in range(2):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2500,
                messages=[
                    {
                        "role": "user",
                        "content": build_prompt(intake)
                    }
                ]
            )

            if response.stop_reason == "max_tokens":
                raise AIServiceError("Claude response was truncated")

            raw_text = "".join(
                block.text
                for block in response.content
                if block.type == "text"
            )

            return parse_roadmap(raw_text)

        except AIServiceError:
            if attempt == 1:
                raise

        except AnthropicError as error:
            raise AIServiceError(
                f"Claude API request failed: {type(error).__name__}"
            ) from error

if __name__ == "__main__":
    mock_response = json.dumps({
        "steps": [
            {
                "title": f"Learning step {i}",
                "description": "Practice an important CS skill.",
                "reasoning": "The student is new and has limited weekly hours.",
                "est_time": "1 week"
            }
            for i in range(1, 6)
        ],
        "not_now": [
            {
                "title": "Advanced machine learning",
                "reasoning": "Focus on programming fundamentals first."
            },
            {
                "title": "Multiple simultaneous projects",
                "reasoning": "The student has limited available time."
            }
        ]
    })

    result = parse_roadmap(mock_response)

    print("SUCCESS: Roadmap JSON parsed and validated!")
    print(f"Steps: {len(result['steps'])}")
    print(f"Not-now items: {len(result['not_now'])}")

    try:
        parse_roadmap('{"steps": []}')
    except AIServiceError:
        print("SUCCESS: Invalid roadmap rejected!")

    sample_intake = {
        "year": "freshman",
        "major_status": "deciding",
        "has_pipeline": "no",
        "coursework": ["none"],
        "skills": [],
        "project_count": "0",
        "biggest_project_type": "none",
        "deployed": "no",
        "carrying": ["none"],
        "weekly_hours": "5_10",
        "credit_load": "12_15",
        "goal": "explore_cs",
        "free_text": "I want to learn programming."
    }

    print("\nPROMPT GENERATION TEST:")
    print(build_prompt(sample_intake))
    print("\nAPI ERROR TEST:")

    if not os.getenv("ANTHROPIC_API_KEY"):
        try:
            generate_with_claude(sample_intake)
        except AIServiceError as error:
            print("SUCCESS: Missing API key handled:", error)
    else:
        print("API key configured; skipping missing-key test")

        # TEST 2: Overloaded student
    overloaded_intake = {
        "year": "sophomore",
        "major_status": "declared",
        "has_pipeline": "yes",
        "coursework": ["intro", "oop", "dsa"],
        "skills": [
            {"language": "python", "level": "multi_file"}
        ],
        "project_count": "2_3",
        "biggest_project_type": "team",
        "deployed": "yes",
        "carrying": [
            "online_course",
            "leetcode",
            "hackathons",
            "club_leadership",
            "research"
        ],
        "weekly_hours": "5_10",
        "credit_load": "19_plus",
        "goal": "internship",
        "free_text": "I am overwhelmed with commitments."
    }

    print("\nOVERLOADED PROFILE PROMPT:")
    print(build_prompt(overloaded_intake))

    assert build_prompt(sample_intake) != build_prompt(overloaded_intake)
    print("SUCCESS: Two distinct student prompts generated!")
