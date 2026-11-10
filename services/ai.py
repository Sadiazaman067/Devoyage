
import json
import os
from pathlib import Path

from anthropic import Anthropic, AnthropicError
from dotenv import load_dotenv

from exceptions import AIServiceError


# Load the API key from the project's .env file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def parse_roadmap(raw_response):
    """Parse and validate Claude's roadmap response."""
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
    """Build a personalized prompt from student intake answers."""
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
- Every reasoning field must reference concrete facts from the student's intake where relevant, such as skills, coursework, workload, or goals.
- Do not invent experiences or qualifications not stated in the intake.


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


def generate_roadmap_from_intake(intake_data: dict) -> dict:
    """Generate a validated roadmap without accessing the database."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise AIServiceError("ANTHROPIC_API_KEY is not configured")

    if not isinstance(intake_data, dict):
        raise AIServiceError("Intake data must be a dictionary")

    client = Anthropic()

    for attempt in range(2):
        try:
            response = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
                max_tokens=2500,
                messages=[
                    {
                        "role": "user",
                        "content": build_prompt(intake_data),
                    }
                ],
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
