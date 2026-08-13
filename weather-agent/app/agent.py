# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.cloud import firestore
from google.genai import types


MODEL = "gemini-3.6-flash"
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-745526bc47f0"
db = firestore.Client(project=FIRESTORE_PROJECT_ID)


async def generate_memories_callback(callback_context: CallbackContext):
    """Sends completed turn session events to Vertex AI Memory Bank for extraction."""
    await callback_context.add_session_to_memory()
    return None


def get_emergency_guide(guide_id: str) -> dict:
    """Reads a specific emergency guide from Firestore.

    Args:
        guide_id: ID of the guide (e.g. 'fire_escape', 'smoke_breathing', 'earthquake_safety').

    Returns:
        Dictionary containing emergency guide details or error message.
    """
    doc_ref = db.collection("emergency_guides").document(guide_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return {"error": f"Emergency guide '{guide_id}' not found."}


def list_emergency_guides(category: str = "") -> list[dict]:
    """Lists available emergency guides from Firestore, optionally filtered by category.

    Args:
        category: Optional category filter ('evacuation', 'first_aid', etc.).

    Returns:
        List of guide dictionaries.
    """
    query = db.collection("emergency_guides")
    if category:
        query = query.where("category", "==", category)
    docs = query.stream()
    return [doc.to_dict() for doc in docs]


def create_incident_report(location: str, emergency_type: str, details: str) -> str:
    """Creates a new emergency incident report entry in Firestore.

    Args:
        location: Current location of the user/incident.
        emergency_type: Type of emergency (e.g., 'fire', 'medical', 'earthquake').
        details: Relevant incident description or status details.

    Returns:
        Confirmation message with report document ID.
    """
    incidents_ref = db.collection("emergency_incidents")
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report_data = {
        "location": location,
        "emergency_type": emergency_type,
        "details": details,
        "timestamp": now_str,
        "status": "DISPATCHED"
    }
    update_time, doc_ref = incidents_ref.add(report_data)
    return f"Emergency incident reported successfully. Incident ID: {doc_ref.id} at {now_str}."


def get_weather(city: str) -> str:
    """Gets weather information for a specified city.

    Args:
        city: The name of the city to get weather for.

    Returns:
        Weather report string.
    """
    city_lower = city.lower()
    if "tokyo" in city_lower:
        return "Tokyo: 22°C (72°F), Clear skies with a gentle breeze."
    elif "london" in city_lower:
        return "London: 18°C (64°F), Light rain showers."
    elif "paris" in city_lower:
        return "Paris: 20°C (68°F), Partly cloudy."
    elif "new york" in city_lower or "nyc" in city_lower:
        return "New York: 25°C (77°F), Sunny."
    elif "sf" in city_lower or "san francisco" in city_lower:
        return "San Francisco: 16°C (60°F), Foggy near the coast."
    elif "sydney" in city_lower:
        return "Sydney: 19°C (66°F), Clear and sunny."
    else:
        return f"{city}: 21°C (70°F), Fair weather."


def get_current_time(city: str) -> str:
    """Gets the current time for a specified city.

    Args:
        city: The name of the city to get current time for.

    Returns:
        Current time string formatted with timezone.
    """
    city_lower = city.lower()
    if "tokyo" in city_lower:
        tz_id = "Asia/Tokyo"
    elif "london" in city_lower:
        tz_id = "Europe/London"
    elif "paris" in city_lower:
        tz_id = "Europe/Paris"
    elif "new york" in city_lower or "nyc" in city_lower:
        tz_id = "America/New_York"
    elif "sf" in city_lower or "san francisco" in city_lower:
        tz_id = "America/Los_Angeles"
    elif "sydney" in city_lower:
        tz_id = "Australia/Sydney"
    else:
        tz_id = "UTC"

    tz = ZoneInfo(tz_id)
    now = datetime.datetime.now(tz)
    return f"The current time in {city} is {now.strftime('%I:%M %p (%Z)')}."


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are an Emergency Response & Rescue Assistant (GuardianAgent). "
        "You help people facing emergency situations by querying emergency survival "
        "guides from Firestore (`get_emergency_guide`, `list_emergency_guides`), "
        "reporting incidents (`create_incident_report`), and remembering user preferences "
        "across sessions."
    ),
    tools=[
        get_emergency_guide,
        list_emergency_guides,
        create_incident_report,
        get_weather,
        get_current_time,
        PreloadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)



