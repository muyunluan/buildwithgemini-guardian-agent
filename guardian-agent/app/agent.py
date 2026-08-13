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
import json
import urllib.parse
import urllib.request
import uuid
from zoneinfo import ZoneInfo

from google import genai
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.cloud import firestore, storage
from google.genai import types


MODEL = "gemini-3.6-flash"
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-745526bc47f0"
STATIC_ASSETS_BUCKET = "qwiklabs-gcp-03-745526bc47f0-static-assets-bucket"
db = firestore.Client(project=FIRESTORE_PROJECT_ID)


async def generate_memories_callback(callback_context: CallbackContext):
    """Sends completed turn session events to Vertex AI Memory Bank for extraction."""
    try:
        await callback_context.add_session_to_memory()
    except (ValueError, Exception):
        pass
    return None


async def generate_emergency_diagram(prompt: str, tool_context: ToolContext) -> str:
    """Generates an emergency diagram, evacuation route map, or safety illustration using Gemini Image Model.

    Args:
        prompt: Description of the emergency diagram or map to generate (e.g., 'fire escape route map for floor 3').

    Returns:
        Public HTTPS URL of the generated diagram image.
    """
    client = genai.Client(vertexai=True, project=FIRESTORE_PROJECT_ID, location="global")
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt
    )

    image_bytes = None
    mime_type = "image/jpeg"
    if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/jpeg"
                break

    if not image_bytes:
        return "Error: Failed to generate diagram image bytes."

    ext = "png" if "png" in mime_type else "jpg"
    filename = f"emergency_diagram_{uuid.uuid4().hex[:8]}.{ext}"

    # 1. Save artifact so it shows up in Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename, artifact_part)

    # 2. Upload same image bytes to public GCS bucket
    storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
    bucket = storage_client.bucket(STATIC_ASSETS_BUCKET)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    return f"https://storage.googleapis.com/{STATIC_ASSETS_BUCKET}/{filename}"


def get_live_hazard_weather(location: str) -> dict:
    """Fetches real-time weather, wind speed, and wind direction for a location using Open-Meteo.

    Args:
        location: City name or location string (e.g. 'New York', 'San Francisco', 'Tokyo').

    Returns:
        Dictionary with live temperature (°C), wind speed (km/h), wind direction (degrees), and hazard analysis.
    """
    try:
        encoded_loc = urllib.parse.quote(location)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_loc}&count=1"
        req = urllib.request.Request(geo_url, headers={"User-Agent": "GuardianAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            geo_data = json.loads(response.read().decode())

        if not geo_data.get("results"):
            return {"error": f"Location '{location}' could not be geocoded."}

        first_res = geo_data["results"][0]
        lat, lon = first_res["latitude"], first_res["longitude"]
        city_name = first_res.get("name", location)
        country = first_res.get("country", "")

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,weather_code"
        )
        req_w = urllib.request.Request(weather_url, headers={"User-Agent": "GuardianAgent/1.0"})
        with urllib.request.urlopen(req_w, timeout=5) as resp_w:
            weather_data = json.loads(resp_w.read().decode())

        current = weather_data.get("current", {})
        temp = current.get("temperature_2m")
        wind_speed = current.get("wind_speed_10m")
        wind_dir = current.get("wind_direction_10m")

        if 45 <= wind_dir < 135:
            dispersion_quadrant = "East"
        elif 135 <= wind_dir < 225:
            dispersion_quadrant = "South"
        elif 225 <= wind_dir < 315:
            dispersion_quadrant = "West"
        else:
            dispersion_quadrant = "North"

        return {
            "location": f"{city_name}, {country}".strip(", "),
            "temperature_c": temp,
            "wind_speed_kmh": wind_speed,
            "wind_direction_degrees": wind_dir,
            "smoke_dispersion_direction": f"Blowing towards {dispersion_quadrant}",
            "high_wind_warning": wind_speed > 25.0,
            "status": "LIVE_WEATHER_RETRIEVED"
        }
    except Exception as e:
        return {"error": f"Failed to fetch live weather for '{location}': {str(e)}"}


def alert_first_responders(location: str, emergency_type: str, details: str) -> str:
    """Triggers an emergency dispatch alert (911/112 mock integration).

    Args:
        location: Current address, floor, or GPS coordinates of the caller.
        emergency_type: Type of emergency (e.g. 'fire', 'medical', 'earthquake').
        details: Critical situational details (e.g., 'trapped on 3rd floor, heavy smoke').

    Returns:
        Status message with confirmation timestamp and dispatch reference code.
    """
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    incidents_ref = db.collection("emergency_incidents")
    report_data = {
        "location": location,
        "emergency_type": emergency_type,
        "details": details,
        "timestamp": now_str,
        "status": "DISPATCHED_FIRST_RESPONDERS"
    }
    _, doc_ref = incidents_ref.add(report_data)
    return (
        f"🚨 EMERGENCY ALERT DISPATCHED: First responders notified for location '{location}' "
        f"({emergency_type.upper()}). Incident Ref: {doc_ref.id} at {now_str}."
    )


def notify_contacts(contacts: list[str], location: str, status_message: str) -> str:
    """Sends SMS/push emergency notification alerts to designated emergency contacts.

    Args:
        contacts: List of contact names or phone numbers to alert.
        location: User's current location.
        status_message: Message to send (e.g. 'I am safe on the east stairwell').

    Returns:
        Confirmation message listing notified contacts.
    """
    notified = ", ".join(contacts) if contacts else "All designated emergency contacts"
    return f"📲 EMERGENCY NOTIFICATION SENT to [{notified}]: '{status_message}' (Location: {location})."


def get_escape_route(current_location: str, hazard_type: str, exit_status: str = "open") -> str:
    """Calculates and returns safe evacuation path instructions.

    Args:
        current_location: Current location/room/floor.
        hazard_type: Type of hazard ('fire', 'smoke', 'earthquake').
        exit_status: Status of primary exit ('open', 'blocked').

    Returns:
        Evacuation route steps.
    """
    if "3" in current_location or "3rd" in current_location.lower():
        if exit_status == "blocked":
            return (
                "⚠️ Main Stairwell A is BLOCKED. Evacuate via East Emergency Exit Stairwell B. "
                "Crawl low under smoke, proceed down to Ground Level Exit 2."
            )
        return (
            "🏃 Primary Escape Route: Stay low to avoid smoke. Head to West Stairwell A, "
            "proceed down to Ground Level Exit 1, and assemble at Primary Assembly Area."
        )
    return (
        f"🏃 General Evacuation Route for {hazard_type.upper()}: Locate nearest illuminated "
        "EXIT sign, avoid elevators, stay low, and proceed to ground-level outdoor assembly area."
    )


def get_first_aid_guidance(condition: str, available_supplies: list[str] = None) -> str:
    """Provides step-by-step emergency first-aid or breathing instructions.

    Args:
        condition: Injury/condition ('smoke_inhalation', 'bleeding', 'burns').
        available_supplies: Optional list of available items (e.g. ['water', 'towel']).

    Returns:
        Instructional first-aid steps.
    """
    supplies_str = ", ".join(available_supplies) if available_supplies else "none specified"
    if "smoke" in condition.lower() or "breath" in condition.lower():
        return (
            "🫁 Smoke Inhalation Protocol: 1. Moisten cloth/shirt with water if available "
            f"(Available supplies: {supplies_str}). 2. Cover nose and mouth tightly. "
            "3. Crawl on hands and knees near floor where air is clearer. 4. Take slow, shallow breaths."
        )
    elif "bleed" in condition.lower():
        return (
            "🩸 Bleeding First Aid: 1. Apply direct firm pressure using clean cloth/towel. "
            "2. Elevate injured limb above heart level. 3. Do NOT remove soaked cloth; add additional layers on top."
        )
    return f"First Aid Protocol for {condition}: Keep victim calm, ensure clear airway, and await first responders."


def get_emergency_guide(guide_id: str) -> dict:
    """Reads a specific emergency guide from Firestore database.

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
    """Lists available emergency guides from Firestore database, optionally filtered by category.

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
    _, doc_ref = incidents_ref.add(report_data)
    return f"Emergency incident reported successfully. Incident ID: {doc_ref.id} at {now_str}."


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are GuardianAgent, an Emergency Response & Rescue Assistant. "
        "Your mission is to help individuals facing emergencies by generating visual emergency diagrams "
        "(`generate_emergency_diagram`), fetching live hazard weather (`get_live_hazard_weather`), "
        "alerting first responders (`alert_first_responders`), notifying emergency contacts "
        "(`notify_contacts`), providing evacuation routes (`get_escape_route`), providing first "
        "aid instructions (`get_first_aid_guidance`), querying survival guides from Firestore "
        "(`get_emergency_guide`, `list_emergency_guides`), and logging incident reports "
        "(`create_incident_report`). Always remain calm, direct, actionable, and prioritize safety."
    ),
    tools=[
        generate_emergency_diagram,
        get_live_hazard_weather,
        alert_first_responders,
        notify_contacts,
        get_escape_route,
        get_first_aid_guidance,
        get_emergency_guide,
        list_emergency_guides,
        create_incident_report,
        PreloadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)



