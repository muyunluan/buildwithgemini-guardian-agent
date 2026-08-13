# Copyright 2026 Google LLC
# Seed Firestore database with emergency response guides and contacts.

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-745526bc47f0"


def seed_database():
    db = firestore.Client(project=PROJECT_ID)

    # Seed Emergency Guides Collection
    guides_ref = db.collection("emergency_guides")
    seeded_guides = [
        {
            "id": "fire_escape",
            "title": "Building Fire Evacuation Guide",
            "category": "evacuation",
            "severity_level": "CRITICAL",
            "steps": [
                "Stay low to the ground to avoid smoke inhalation.",
                "Feel door handles before opening — if hot, do NOT open.",
                "Use wet cloth over nose and mouth if smoke is present.",
                "Proceed to nearest marked fire exit / stairwell. Never use elevators.",
                "Once safe outside, call emergency dispatch immediately."
            ],
            "supplies_needed": ["Wet cloth or towel", "Flashlight/Phone light"]
        },
        {
            "id": "smoke_breathing",
            "title": "Improvised Smoke Breathing & Filtration",
            "category": "first_aid",
            "severity_level": "CRITICAL",
            "steps": [
                "Moisten a clean cotton cloth, towel, or shirt with water.",
                "Cover both nose and mouth tightly with the wet fabric.",
                "Crawl on hands and knees where air is cleaner near the floor.",
                "Take shallow, calm breaths through the fabric."
            ],
            "supplies_needed": ["Water", "Cotton cloth / towel / shirt"]
        },
        {
            "id": "earthquake_safety",
            "title": "Earthquake Drop, Cover, and Hold On",
            "category": "evacuation",
            "severity_level": "HIGH",
            "steps": [
                "Drop onto hands and knees under sturdy furniture (table or desk).",
                "Cover head and neck with one arm.",
                "Hold on to your shelter until shaking stops.",
                "Stay away from glass, windows, and exterior walls."
            ],
            "supplies_needed": ["Sturdy table/desk", "Head/Neck protection"]
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
            "name": "Local Emergency Dispatch (911/112)",
            "service_type": "First Responder",
            "phone": "911",
            "active": True
        },
        {
            "id": "fire_dept",
            "name": "Metropolitan Fire & Rescue",
            "service_type": "Fire Department",
            "phone": "555-0199",
            "active": True
        }
    ]

    for contact in seeded_contacts:
        doc_ref = contacts_ref.document(contact["id"])
        doc_ref.set(contact)
        print(f"Seeded contact: {contact['id']} -> {contact['name']}")

    print("Firestore database seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
