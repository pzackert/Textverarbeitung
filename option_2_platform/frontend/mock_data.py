from datetime import datetime, timedelta
import uuid

def generate_mock_data():
    users = [
        {"id": 1, "name": "Max Mustermann", "role": "Sachbearbeiter", "email": "max.mustermann@ifb.hamburg.de", "avatar": "https://ui-avatars.com/api/?name=Max+Mustermann&background=random"},
        {"id": 2, "name": "Erika Musterfrau", "role": "Teamleiter", "email": "erika.musterfrau@ifb.hamburg.de", "avatar": "https://ui-avatars.com/api/?name=Erika+Musterfrau&background=random"},
        {"id": 3, "name": "John Doe", "role": "Sachbearbeiter", "email": "john.doe@ifb.hamburg.de", "avatar": "https://ui-avatars.com/api/?name=John+Doe&background=random"},
    ]

    projects = [
        {
            "id": "projekt_12345678",
            "antragsteller": "TechStart GmbH",
            "projekt_name": "KI-basierte Logistikoptimierung",
            "modul": "PROFI Standard",
            "status": "In Prüfung",
            "status_color": "blue",
            "assigned_to": 1,
            "last_updated": (datetime.now() - timedelta(hours=2)).strftime("%d.%m.%Y %H:%M"),
            "priority": "Hoch",
            "description": "Entwicklung einer KI-Plattform zur Optimierung von Lieferketten in Echtzeit.",
            "documents": [
                {"name": "Handelsregisterauszug.pdf", "type": "pdf", "date": "20.11.2024"},
                {"name": "Projektbeschreibung.docx", "type": "docx", "date": "20.11.2024"},
                {"name": "Finanzplan.xlsx", "type": "xlsx", "date": "21.11.2024"},
            ]
        },
        {
            "id": "projekt_87654321",
            "antragsteller": "GreenEnergy Solutions",
            "projekt_name": "Solar-Speicher für KMU",
            "modul": "PROFI Umwelt",
            "status": "Neu",
            "status_color": "green",
            "assigned_to": 1,
            "last_updated": (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y %H:%M"),
            "priority": "Mittel",
            "description": "Entwicklung modularer Batteriespeicher für kleine und mittlere Unternehmen.",
            "documents": [
                {"name": "Antrag.pdf", "type": "pdf", "date": "19.11.2024"},
            ]
        },
        {
            "id": "projekt_abcdef12",
            "antragsteller": "Hafen Logistik AG",
            "projekt_name": "Autonome Drohnen im Hafen",
            "modul": "PROFI Impuls",
            "status": "Rückfrage",
            "status_color": "yellow",
            "assigned_to": 3,
            "last_updated": (datetime.now() - timedelta(days=3)).strftime("%d.%m.%Y %H:%M"),
            "priority": "Niedrig",
            "description": "Einsatz von Drohnen zur Inspektion von Containerbrücken.",
            "documents": []
        },
         {
            "id": "projekt_99887766",
            "antragsteller": "BioMed Research KG",
            "projekt_name": "Neue Impfstofftechnologie",
            "modul": "PROFI Standard",
            "status": "Abgeschlossen",
            "status_color": "gray",
            "assigned_to": 2,
            "last_updated": (datetime.now() - timedelta(days=10)).strftime("%d.%m.%Y %H:%M"),
            "priority": "Hoch",
            "description": "Forschung an mRNA-basierten Impfstoffen.",
            "documents": []
        },
        {
            "id": "projekt_55443322",
            "antragsteller": "EduTech Systems",
            "projekt_name": "Lernplattform für Schulen",
            "modul": "PROFI Digital",
            "status": "In Prüfung",
            "status_color": "blue",
            "assigned_to": 1,
            "last_updated": (datetime.now() - timedelta(minutes=30)).strftime("%d.%m.%Y %H:%M"),
            "priority": "Mittel",
            "description": "Digitale Lernplattform für Hamburger Schulen.",
            "documents": []
        }
    ]

    criteria = [
        {"id": "c1", "name": "Unternehmenssitz Hamburg", "category": "Harte Kriterien", "type": "auto", "status": "erfüllt"},
        {"id": "c2", "name": "KMU-Status", "category": "Harte Kriterien", "type": "auto", "status": "erfüllt"},
        {"id": "c3", "name": "Finanzielle Stabilität", "category": "Finanzielle Kriterien", "type": "manual", "status": "offen"},
        {"id": "c4", "name": "Innovationsgrad", "category": "Inhaltliche Kriterien", "type": "manual", "status": "offen"},
        {"id": "c5", "name": "Marktpotenzial", "category": "Inhaltliche Kriterien", "type": "manual", "status": "offen"},
    ]

    return users, projects, criteria

USERS, PROJECTS, CRITERIA = generate_mock_data()
