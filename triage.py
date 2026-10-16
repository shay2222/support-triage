"""
Core classification logic. To adapt this pattern to another startup problem
(lead qualification, bug intake, feedback analysis, invoice routing), change
CATEGORIES, URGENCIES, and PROMPT_TEMPLATE. The validation and retry logic
stays the same.
"""
import json
from google import genai
from google.genai import types

MODEL = "gemini-3.7-flash"
CATEGORIES = ["bug", "billing", "feature_request", "other"]
URGENCIES = ["low", "medium", "high"]

PROMPT_TEMPLATE = """You classify customer support messages for a software startup.
Return only a JSON object with these keys:
- "category": one of {categories}
- "urgency": one of {urgencies}
- "summary": one sentence describing the customer's issue

Urgency guide:
- high: outage, data loss, security concern, or the customer cannot work at all
- medium: a clear problem that has a workaround
- low: questions, suggestions, or general feedback

Message:
\"\"\"{ticket}\"\"\"
"""


class TriageError(Exception):
    pass


def build_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def _validate(result: dict) -> dict:
    if result.get("category") not in CATEGORIES:
        raise TriageError(f"Invalid category: {result.get('category')}")
    if result.get("urgency") not in URGENCIES:
        raise TriageError(f"Invalid urgency: {result.get('urgency')}")
    if not isinstance(result.get("summary"), str) or not result["summary"].strip():
        raise TriageError("Missing summary")
    return result


def triage_ticket(client: genai.Client, ticket_text: str, retries: int = 2) -> dict:
    """Classify one ticket. Retries when the model returns invalid output."""
    prompt = PROMPT_TEMPLATE.format(
        categories=CATEGORIES, urgencies=URGENCIES, ticket=ticket_text
    )
    last_error = None
    for _ in range(retries + 1):
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0,
            ),
        )
        try:
            return _validate(json.loads(response.text))
        except (json.JSONDecodeError, TriageError) as err:
            last_error = err
    raise TriageError(f"Failed after {retries + 1} attempts: {last_error}")