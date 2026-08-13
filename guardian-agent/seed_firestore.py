# Copyright 2026 Google LLC
# Seed Firestore database with emergency response guides and contacts for GuardianAgent.

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-745526bc47f0"


def seed_database():
    db = firestore.Client(project=PROJECT_ID)

    # Seed Emergency Guides Collection
    guides_ref = db.collection("emergency_guides")
    seeded_guides = [
        {
            "id": "fire_escape",
            "title": "Building Fire Evacuation Protocol",
            "category": "evacuation",
            "severity_level": "CRITICAL",
            "steps": [
                "Stay low to the ground below toxic smoke.",
                "Check door handles for heat before opening.",
                "Place wet fabric/towel over nose and mouth.",
                "Proceed to primary fire exit/stairwell. Do NOT use elevators.",
                "Once safe outside, alert 911 dispatch immediately."
            ],
            "supplies_needed": ["Wet cloth or towel", "Phone flashlight"]
        },
        {
            "id": "smoke_breathing",
            "title": "Smoke Inhalation Protection & Filter Masking",
            "category": "first_aid",
            "severity_level": "CRITICAL",
            "steps": [
                "Moisten clean cotton cloth or shirt with water.",
                "Secure tightly over nose and mouth.",
                "Crawl on hands and knees near floor where oxygen concentration is highest.",
                "Take shallow, slow breaths through the wet filter."
            ],
            "supplies_needed": ["Water", "Cotton cloth / towel / shirt"]
        },
        {
            "id": "earthquake_safety",
            "title": "Earthquake Shelter & Protocol",
            "category": "evacuation",
            "severity_level": "HIGH",
            "steps": [
                "Drop onto hands and knees under heavy desk or table.",
                "Cover head and neck with one arm.",
                "Hold on firmly to shelter until shaking stops.",
                "Keep clear of glass, overhead fixtures, and exterior walls."
            ],
            "supplies_needed": ["Heavy table/desk", "Arm/Pillow head protection"]
        }
    ]

    for guide in seeded_guides:
        doc_ref = guides_ref.document(guide["id"])
        doc_ref.set(guide)
        print(f"Seeded guide: {guide['id']} -> {guide['title']}")

    # Seed Emergency Contacts Collection
    contacts_ref = db.collection("emergency_contacts")
    seeded_contacts = [
        {
            "id": "dispatch_911",
            "name": "Emergency Services Dispatch (911/112)",
            "service_type": "First Responder",
            "phone": "911",
            "active": True
        },
        {
            "id": "fire_dept",
            "name": "Metropolitan Fire & Rescue Squad",
            "service_type": "Fire Department",
            "phone": "555-0199",
            "active": True
        }
    ]

    for contact in seeded_contacts:
        doc_ref = contacts_ref.document(contact["id"])
        doc_ref.set(contact)
        print(f"Seeded contact: {contact['id']} -> {contact['name']}")

    print("GuardianAgent Firestore seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
