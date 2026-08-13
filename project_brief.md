# My agent: Emergency Response & Rescue Assistant (GuardianAgent)
One-liner: A conversational emergency response agent that helps individuals in crisis alert first responders and emergency contacts, while providing immediate real-time survival instructions, evacuation routes, and first-aid guidance.

Tool coverage:
- Memory: User profile (medical info, blood type, address, emergency contact list, building floor/layout preferences)
- Tools:
  - `alert_first_responders(location, emergency_type, details)`: Triggers emergency dispatch alert (911/112 integration mock)
  - `notify_contacts(contact_list, location, status_message)`: Sends SMS/push notification alerts to designated emergency contacts
  - `get_escape_route(current_location, hazard_type, exit_status)`: Calculates and returns safe evacuation path instructions
  - `get_first_aid_guidance(condition, available_supplies)`: Provides step-by-step emergency first-aid or breathing instructions
- Catalog/UI: Emergency Contact list, Nearest Exit routes, Step-by-Step Survival Guides (renders cleanly as cards/tables)
- Image gen: Visual floorplan evacuation map / step-by-step first-aid instructional diagrams (e.g., wet cloth breathing filter demonstration)
- Sandbox: Computes shortest safe evacuation route and estimated time to exit based on fire/hazard location data

Core rails (everyone): memory, tools, eval, deploy, frontend
My stretch menu (pick later): A2UI evacuation cards, floorplan image generation, evacuation route computation sandbox
First eval question: "There is a fire on the 3rd floor outside my office! I am trapped on the 3rd floor, what should I do and can you notify 911 and my emergency contacts?"
