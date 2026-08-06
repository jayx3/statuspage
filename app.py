import re

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

import models
from auth import auth_bp, login_manager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

login_manager.init_app(app)
app.register_blueprint(auth_bp)

STATUS_COLORS = {
    "Operational": "success",
    "Degraded Performance": "warning",
    "Partial Outage": "serious",
    "Major Outage": "danger",
    "Maintenance": "info",
}

INCIDENT_COLORS = {
    "Investigating": "danger",
    "Identified": "warning",
    "Monitoring": "info",
    "Resolved": "success",
}

BAR_CLASS = {
    "Operational": "",
    "Degraded Performance": "bar-warning",
    "Partial Outage": "bar-serious",
    "Major Outage": "bar-danger",
    "Maintenance": "bar-info",
}


@app.context_processor
def inject_status_colors():
    return {"status_colors": STATUS_COLORS, "incident_colors": INCIDENT_COLORS}


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "project"


def get_owned_project_or_404(project_id):
    project = models.get_project(project_id)
    if not project or str(project["user_id"]) != current_user.id:
        abort(404)
    return project


def get_owned_incident_or_404(project_id, incident_id):
    incident = models.get_incident(incident_id)
    if not incident or str(incident["project_id"]) != project_id:
        abort(404)
    return incident


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("auth.login"))


@app.route("/dashboard")
@login_required
def dashboard():
    projects = models.get_projects_for_user(current_user.id)
    return render_template("dashboard.html", projects=projects)


@app.route("/projects/create", methods=["POST"])
@login_required
def create_project():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    if not name:
        flash("Project name is required.", "danger")
        return redirect(url_for("dashboard"))

    base_slug = slugify(name)
    slug = base_slug
    n = 1
    while models.slug_exists(slug):
        n += 1
        slug = f"{base_slug}-{n}"

    models.create_project(current_user.id, name, description, slug)
    flash("Project created.", "success")
    return redirect(url_for("dashboard"))


@app.route("/projects/<project_id>/edit", methods=["POST"])
@login_required
def edit_project(project_id):
    get_owned_project_or_404(project_id)
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    if name:
        models.update_project(project_id, name, description)
        flash("Project updated.", "success")
    return redirect(url_for("dashboard"))


@app.route("/projects/<project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    get_owned_project_or_404(project_id)
    models.delete_project(project_id)
    flash("Project deleted.", "success")
    return redirect(url_for("dashboard"))


@app.route("/projects/<project_id>")
@login_required
def project_detail(project_id):
    project = get_owned_project_or_404(project_id)
    components = models.get_components_for_project(project_id)
    incidents = models.get_incidents_for_project(project_id)
    return render_template(
        "project.html",
        project=project,
        components=components,
        incidents=incidents,
        component_statuses=models.COMPONENT_STATUSES,
    )


@app.route("/projects/<project_id>/components/create", methods=["POST"])
@login_required
def create_component(project_id):
    get_owned_project_or_404(project_id)
    name = request.form.get("name", "").strip()
    status = request.form.get("status", "Operational")
    if name and status in models.COMPONENT_STATUSES:
        models.create_component(project_id, name, status)
        flash("Component added.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/projects/<project_id>/components/<component_id>/update", methods=["POST"])
@login_required
def update_component(project_id, component_id):
    get_owned_project_or_404(project_id)
    status = request.form.get("status")
    if status in models.COMPONENT_STATUSES:
        models.update_component_status(component_id, status)
    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/projects/<project_id>/components/<component_id>/delete", methods=["POST"])
@login_required
def delete_component(project_id, component_id):
    get_owned_project_or_404(project_id)
    models.delete_component(component_id)
    flash("Component removed.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/projects/<project_id>/incidents/create", methods=["POST"])
@login_required
def create_incident(project_id):
    get_owned_project_or_404(project_id)
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if title:
        models.create_incident(project_id, title, description)
        flash("Incident created.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/projects/<project_id>/incidents/<incident_id>")
@login_required
def incident_detail(project_id, incident_id):
    project = get_owned_project_or_404(project_id)
    incident = get_owned_incident_or_404(project_id, incident_id)
    return render_template(
        "incident.html",
        project=project,
        incident=incident,
        incident_statuses=models.INCIDENT_STATUSES,
    )


@app.route("/projects/<project_id>/incidents/<incident_id>/update", methods=["POST"])
@login_required
def update_incident(project_id, incident_id):
    get_owned_project_or_404(project_id)
    get_owned_incident_or_404(project_id, incident_id)
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    status = request.form.get("status")
    if title and status in models.INCIDENT_STATUSES:
        models.update_incident(incident_id, title, description, status)
        flash("Incident updated.", "success")
    return redirect(url_for("incident_detail", project_id=project_id, incident_id=incident_id))


@app.route("/projects/<project_id>/incidents/<incident_id>/delete", methods=["POST"])
@login_required
def delete_incident(project_id, incident_id):
    get_owned_project_or_404(project_id)
    get_owned_incident_or_404(project_id, incident_id)
    models.delete_incident(incident_id)
    flash("Incident deleted.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/status/<slug>")
def public_status(slug):
    project = models.get_project_by_slug(slug)
    if not project:
        abort(404)
    components = models.get_components_for_project(project["_id"])
    for component in components:
        bars = models.component_daily_status(component)
        for bar in bars:
            bar["css_class"] = BAR_CLASS.get(bar["status"], "bar-none")
        component["uptime_bars"] = bars

    incidents = models.get_incidents_for_project(project["_id"])
    active_incidents = [i for i in incidents if not i["resolved"]]
    resolved_incidents = [i for i in incidents if i["resolved"]]
    return render_template(
        "public.html",
        project=project,
        components=components,
        active_incidents=active_incidents,
        resolved_incidents=resolved_incidents,
    )


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
