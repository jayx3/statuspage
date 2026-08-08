from datetime import datetime, timedelta

from bson.objectid import ObjectId
from pymongo import MongoClient

from config import Config

client = MongoClient(Config.MONGO_URI)
db = client.get_default_database()

users = db.users
projects = db.projects
components = db.components
incidents = db.incidents

COMPONENT_STATUSES = [
    "Operational",
    "Degraded Performance",
    "Partial Outage",
    "Major Outage",
    "Maintenance",
]

INCIDENT_STATUSES = ["Investigating", "Identified", "Monitoring", "Resolved"]


# --- Users ---

def create_user(name, email, password_hash):
    return users.insert_one(
        {"name": name, "email": email, "password_hash": password_hash}
    ).inserted_id


def find_user_by_email(email):
    return users.find_one({"email": email})


def find_user_by_id(user_id):
    return users.find_one({"_id": ObjectId(user_id)})


# --- Projects ---

def create_project(user_id, name, description, slug):
    return projects.insert_one(
        {
            "user_id": ObjectId(user_id),
            "name": name,
            "description": description,
            "slug": slug,
            "created_at": datetime.utcnow(),
        }
    ).inserted_id


def get_projects_for_user(user_id):
    return list(projects.find({"user_id": ObjectId(user_id)}).sort("created_at", -1))


def get_project(project_id):
    return projects.find_one({"_id": ObjectId(project_id)})


def get_project_by_slug(slug):
    return projects.find_one({"slug": slug})


def update_project(project_id, name, description):
    projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {"name": name, "description": description}},
    )


def delete_project(project_id):
    pid = ObjectId(project_id)
    projects.delete_one({"_id": pid})
    components.delete_many({"project_id": pid})
    incidents.delete_many({"project_id": pid})


def slug_exists(slug):
    return projects.find_one({"slug": slug}) is not None


# --- Components ---

def create_component(project_id, name, status="Operational"):
    now = datetime.utcnow()
    return components.insert_one(
        {
            "project_id": ObjectId(project_id),
            "name": name,
            "status": status,
            "created_at": now,
            "history": [{"status": status, "at": now}],
        }
    ).inserted_id


def get_components_for_project(project_id):
    return list(components.find({"project_id": ObjectId(project_id)}))


def get_component(component_id):
    return components.find_one({"_id": ObjectId(component_id)})


def update_component_status(component_id, status):
    now = datetime.utcnow()
    components.update_one(
        {"_id": ObjectId(component_id)},
        {"$set": {"status": status}, "$push": {"history": {"status": status, "at": now}}},
    )


def component_daily_status(component, days=90):
    history = sorted(component.get("history", []), key=lambda h: h["at"])
    if history:
        created_date = history[0]["at"].date()
    else:
        created_date = component.get("created_at", datetime.utcnow()).date()

    today = datetime.utcnow().date()
    bars = []
    for i in range(days - 1, -1, -1):
        day = today - timedelta(days=i)
        if day < created_date:
            bars.append({"date": day, "status": None})
            continue
        status = component.get("status")
        for h in history:
            if h["at"].date() > day:
                break
            status = h["status"]
        bars.append({"date": day, "status": status})
    return bars


def delete_component(component_id):
    components.delete_one({"_id": ObjectId(component_id)})


# --- Incidents ---

def create_incident(project_id, title, description, status="Investigating", started_at=None, ended_at=None):
    now = datetime.utcnow()
    return incidents.insert_one(
        {
            "project_id": ObjectId(project_id),
            "title": title,
            "description": description,
            "status": status,
            "resolved": status == "Resolved",
            "started_at": started_at or now,
            "ended_at": ended_at,
            "created_at": now,
            "updated_at": now,
        }
    ).inserted_id


def get_incidents_for_project(project_id):
    return list(
        incidents.find({"project_id": ObjectId(project_id)}).sort("created_at", -1)
    )


def get_incident(incident_id):
    return incidents.find_one({"_id": ObjectId(incident_id)})


def update_incident(incident_id, title, description, status, started_at, ended_at):
    incidents.update_one(
        {"_id": ObjectId(incident_id)},
        {
            "$set": {
                "title": title,
                "description": description,
                "status": status,
                "resolved": status == "Resolved",
                "started_at": started_at,
                "ended_at": ended_at,
                "updated_at": datetime.utcnow(),
            }
        },
    )


def delete_incident(incident_id):
    incidents.delete_one({"_id": ObjectId(incident_id)})
