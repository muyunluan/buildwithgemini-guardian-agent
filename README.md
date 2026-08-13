# 🚨 GuardianAgent — Emergency Response & Rescue Assistant

> **A conversational emergency response agent that empowers individuals in crisis to alert first responders and emergency contacts, while providing immediate real-time survival instructions, evacuation routes, and visual first-aid guidance.**

![GuardianAgent Demo](./demo.gif)

---

## 📖 Overview

In emergent and high-stress situations—such as building fires, natural disasters, or medical emergencies—seconds count. **GuardianAgent** acts as an intelligent emergency copilot. Accessible via a modern web interface equipped with voice speech input and one-click SOS alerts, it combines real-time data lookups, visual diagram generation, and direct communication integrations to guide victims to safety while notifying rescue teams and loved ones.

---

## ✨ Key Features

- **🚨 One-Click SOS Emergency Alert**: High-visibility header button (`🚨 SOS ALERT`) that instantly triggers first responder dispatch and sends emergency notifications to designated contacts.
- **🎙️ Hands-Free Voice Input (Speech-to-Text)**: Integrated Web Speech API microphone control (`🎙️`) for hands-free voice query input during high-stress situations.
- **💬 Modern Emergency Dialogue Layout**: Clean chat interface featuring distinct user/agent message cards, status light indicators (`🟢 SYSTEM READY`), and quick-action prompt chips.
- **🚑 First Responder Dispatch & Incident Logging**: Instantly dispatches alerts (mock 911/112 integration) with location and emergency details, recording official logs in Firestore.
- **📱 Emergency Contact Notifications**: Automatically sends status updates and location coordinates via SMS/push notifications to designated emergency contacts.
- **🏃 Dynamic Evacuation Route Guidance**: Computes the fastest and safest escape path tailored to current hazard locations, floor layouts, and blocked exits.
- **🩺 First-Aid & Breathing Procedures**: Provides immediate, actionable first-aid and survival steps using nearby items (e.g., creating makeshift smoke filtration masks from wet cloth).
- **🌤️ Live Hazard Weather & Smoke Dispersion**: Queries real-time wind speed, wind direction, and weather metrics to assess hazardous smoke or fire spread paths.
- **🗺️ Visual Emergency Diagram Generation**: Generates custom floorplan escape maps and visual safety illustrations on demand using `gemini-3.1-flash-lite-image`.

---

## 🛠️ Google Cloud Tools & Architecture

GuardianAgent leverages a full suite of Google Cloud and Vertex AI capabilities:

| Technology / Tool | Usage in GuardianAgent |
| :--- | :--- |
| **Vertex AI Memory Bank** | Persists user profile data across sessions (e.g., blood type, medical conditions, default emergency contacts, home layout). |
| **Google Cloud Firestore** | Stores persistent emergency incident logs and contact directories with real-time read/write tool integrations. |
| **Google Cloud Storage (GCS)** | Public bucket hosting for generated escape diagrams, maps, and static safety assets. |
| **`gemini-3.1-flash-lite-image`** | Generates high-quality visual evacuation route diagrams and step-by-step first-aid illustrations in the global region. |
| **Agent-to-User Interface (A2UI)** | Emits rich display cards, tables, and visual components rendered natively in the chat web interface. |
| **FastAPI Proxy & A2A Protocol** | Bridges the web frontend to the deployed Vertex AI Agent Engine using the GA Agent-to-Agent (A2A) SDK. |

---

## 🚀 Getting Started Locally

### Prerequisites
- Python 3.11+
- `gcloud` CLI authenticated with Application Default Credentials (`gcloud auth application-default login`)

### Running the Frontend
1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Activate the virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/python
   pip install -r requirements.txt
   ```
3. Start the FastAPI server:
   ```bash
   PORT=8080 .venv/bin/python main.py
   ```
4. Open **[http://localhost:8080](http://localhost:8080)** in your browser.

---

## 🛡️ Safety & Disclaimer
*GuardianAgent is built as a prototype demonstrator for Google Cloud & Vertex AI Agent Engine technologies. In a real emergency, always call local emergency services (e.g., 911) immediately when possible.*
