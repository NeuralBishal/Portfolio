import os
import re
from datetime import datetime

from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, current_app, abort,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import (
    db, AdminUser, SiteConfig,
    Project, Resource, Skill, Education, Certification,
    LearningItem, BlogPost, ContactMessage,
)
from app.storage import save_file, delete_file


admin_bp = Blueprint("admin", __name__)


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def _int_or_zero(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def _unique_slug(base: str, exclude_id: int = None) -> str:
    """Generate a slug; if taken, append -2, -3, etc."""
    slug = base
    n = 2
    while True:
        q = BlogPost.query.filter_by(slug=slug)
        if exclude_id:
            q = q.filter(BlogPost.id != exclude_id)
        if not q.first():
            return slug
        slug = f"{base}-{n}"
        n += 1


# ─────────────────────────────────────────────────────────────
# Login / Logout
# ─────────────────────────────────────────────────────────────
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = AdminUser.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Welcome back!", "success")
            return redirect(request.args.get("next") or url_for("admin.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("admin/login.html")


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "info")
    return redirect(url_for("public.index"))


# ─────────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────────
@admin_bp.route("/")
@login_required
def dashboard():
    stats = {
        "projects": Project.query.count(),
        "resources": Resource.query.count(),
        "posts": BlogPost.query.count(),
        "unread": ContactMessage.query.filter_by(is_read=False).count(),
        "total_messages": ContactMessage.query.count(),
    }
    recent_messages = (
        ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    )
    return render_template("admin/dashboard.html", stats=stats, recent_messages=recent_messages)


# ═════════════════════════════════════════════════════════════
# PROJECTS
# ═════════════════════════════════════════════════════════════
@admin_bp.route("/projects")
@login_required
def projects_list():
    projects = Project.query.order_by(Project.display_order, Project.id.desc()).all()
    return render_template("admin/projects_list.html", projects=projects)


@admin_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def projects_new():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Title is required.", "danger")
            return redirect(url_for("admin.projects_new"))
        image_url = ""
        file = request.files.get("image")
        if file and file.filename:
            try:
                image_url = save_file(file, folder="images")
            except ValueError as e:
                flash(str(e), "danger")
                return redirect(url_for("admin.projects_new"))
        project = Project(
            title=title,
            description=request.form.get("description", "").strip(),
            tech_stack=request.form.get("tech_stack", "").strip(),
            github_url=request.form.get("github_url", "").strip(),
            demo_url=request.form.get("demo_url", "").strip(),
            status=request.form.get("status", "live"),
            featured=bool(request.form.get("featured")),
            display_order=_int_or_zero(request.form.get("display_order")),
            image_url=image_url,
        )
        db.session.add(project)
        db.session.commit()
        flash(f"Project '{title}' created.", "success")
        return redirect(url_for("admin.projects_list"))
    return render_template("admin/projects_form.html", project=None)


@admin_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def projects_edit(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Title is required.", "danger")
            return redirect(url_for("admin.projects_edit", project_id=project.id))
        project.title = title
        project.description = request.form.get("description", "").strip()
        project.tech_stack = request.form.get("tech_stack", "").strip()
        project.github_url = request.form.get("github_url", "").strip()
        project.demo_url = request.form.get("demo_url", "").strip()
        project.status = request.form.get("status", "live")
        project.featured = bool(request.form.get("featured"))
        project.display_order = _int_or_zero(request.form.get("display_order"))
        file = request.files.get("image")
        if file and file.filename:
            if project.image_url:
                delete_file(project.image_url)
            try:
                project.image_url = save_file(file, folder="images")
            except ValueError as e:
                flash(str(e), "danger")
                return redirect(url_for("admin.projects_edit", project_id=project.id))
        db.session.commit()
        flash("Project updated.", "success")
        return redirect(url_for("admin.projects_list"))
    return render_template("admin/projects_form.html", project=project)


@admin_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def projects_delete(project_id):
    project = Project.query.get_or_404(project_id)
    title = project.title
    if project.image_url:
        delete_file(project.image_url)
    db.session.delete(project)
    db.session.commit()
    flash(f"Project '{title}' deleted.", "info")
    return redirect(url_for("admin.projects_list"))


# ═════════════════════════════════════════════════════════════
# RESOURCES
# ═════════════════════════════════════════════════════════════
@admin_bp.route("/resources")
@login_required
def resources_list():
    resources = Resource.query.order_by(Resource.display_order, Resource.id.desc()).all()
    return render_template("admin/resources_list.html", resources=resources)


@admin_bp.route("/resources/new", methods=["GET", "POST"])
@login_required
def resources_new():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Title is required.", "danger")
            return redirect(url_for("admin.resources_new"))
        image_url = ""
        file = request.files.get("image")
        if file and file.filename:
            try:
                image_url = save_file(file, folder="images")
            except ValueError as e:
                flash(str(e), "danger")
                return redirect(url_for("admin.resources_new"))
        resource = Resource(
            title=title,
            tagline=request.form.get("tagline", "").strip(),
            description=request.form.get("description", "").strip(),
            topics=request.form.get("topics", "").strip(),
            url=request.form.get("url", "").strip(),
            status=request.form.get("status", "growing"),
            display_order=_int_or_zero(request.form.get("display_order")),
            image_url=image_url,
        )
        db.session.add(resource)
        db.session.commit()
        flash(f"Resource '{title}' created.", "success")
        return redirect(url_for("admin.resources_list"))
    return render_template("admin/resources_form.html", resource=None)


@admin_bp.route("/resources/<int:resource_id>/edit", methods=["GET", "POST"])
@login_required
def resources_edit(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Title is required.", "danger")
            return redirect(url_for("admin.resources_edit", resource_id=resource.id))
        resource.title = title
        resource.tagline = request.form.get("tagline", "").strip()
        resource.description = request.form.get("description", "").strip()
        resource.topics = request.form.get("topics", "").strip()
        resource.url = request.form.get("url", "").strip()
        resource.status = request.form.get("status", "growing")
        resource.display_order = _int_or_zero(request.form.get("display_order"))
        file = request.files.get("image")
        if file and file.filename:
            if resource.image_url:
                delete_file(resource.image_url)
            try:
                resource.image_url = save_file(file, folder="images")
            except ValueError as e:
                flash(str(e), "danger")
                return redirect(url_for("admin.resources_edit", resource_id=resource.id))
        db.session.commit()
        flash("Resource updated.", "success")
        return redirect(url_for("admin.resources_list"))
    return render_template("admin/resources_form.html", resource=resource)


@admin_bp.route("/resources/<int:resource_id>/delete", methods=["POST"])
@login_required
def resources_delete(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    title = resource.title
    if resource.image_url:
        delete_file(resource.image_url)
    db.session.delete(resource)
    db.session.commit()
    flash(f"Resource '{title}' deleted.", "info")
    return redirect(url_for("admin.resources_list"))


# ═════════════════════════════════════════════════════════════
# SKILLS
# ═════════════════════════════════════════════════════════════
@admin_bp.route("/skills")
@login_required
def skills_list():
    skills = Skill.query.order_by(Skill.category, Skill.display_order).all()
    grouped = {}
    for s in skills:
        grouped.setdefault(s.category, []).append(s)
    return render_template("admin/skills_list.html", skills=skills, grouped=grouped)


@admin_bp.route("/skills/new", methods=["GET", "POST"])
@login_required
def skills_new():
    if request.method == "POST":
        category = request.form.get("category", "").strip()
        name = request.form.get("name", "").strip()
        if not (category and name):
            flash("Category and name are required.", "danger")
            return redirect(url_for("admin.skills_new"))
        db.session.add(Skill(
            category=category, name=name,
            display_order=_int_or_zero(request.form.get("display_order")),
        ))
        db.session.commit()
        flash(f"Skill '{name}' added.", "success")
        return redirect(url_for("admin.skills_list"))
    return render_template("admin/skills_form.html", skill=None)


@admin_bp.route("/skills/<int:skill_id>/edit", methods=["GET", "POST"])
@login_required
def skills_edit(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if request.method == "POST":
        skill.category = request.form.get("category", "").strip()
        skill.name = request.form.get("name", "").strip()
        skill.display_order = _int_or_zero(request.form.get("display_order"))
        db.session.commit()
        flash("Skill updated.", "success")
        return redirect(url_for("admin.skills_list"))
    return render_template("admin/skills_form.html", skill=skill)


@admin_bp.route("/skills/<int:skill_id>/delete", methods=["POST"])
@login_required
def skills_delete(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    db.session.delete(skill)
    db.session.commit()
    flash("Skill deleted.", "info")
    return redirect(url_for("admin.skills_list"))


# ═════════════════════════════════════════════════════════════
# EDUCATION
# ═════════════════════════════════════════════════════════════
@admin_bp.route("/education")
@login_required
def education_list():
    items = Education.query.order_by(Education.display_order).all()
    learning = LearningItem.query.order_by(LearningItem.display_order).all()
    return render_template("admin/education_list.html", education=items, learning=learning)


@admin_bp.route("/education/new", methods=["GET", "POST"])
@login_required
def education_new():
    if request.method == "POST":
        institution = request.form.get("institution", "").strip()
        if not institution:
            flash("Institution is required.", "danger")
            return redirect(url_for("admin.education_new"))
        db.session.add(Education(
            institution=institution,
            degree=request.form.get("degree", "").strip(),
            start_year=request.form.get("start_year", "").strip(),
            end_year=request.form.get("end_year", "").strip(),
            grade=request.form.get("grade", "").strip(),
            details=request.form.get("details", "").strip(),
            display_order=_int_or_zero(request.form.get("display_order")),
        ))
        db.session.commit()
        flash("Education entry added.", "success")
        return redirect(url_for("admin.education_list"))
    return render_template("admin/education_form.html", edu=None)


@admin_bp.route("/education/<int:edu_id>/edit", methods=["GET", "POST"])
@login_required
def education_edit(edu_id):
    edu = Education.query.get_or_404(edu_id)
    if request.method == "POST":
        edu.institution = request.form.get("institution", "").strip()
        edu.degree = request.form.get("degree", "").strip()
        edu.start_year = request.form.get("start_year", "").strip()
        edu.end_year = request.form.get("end_year", "").strip()
        edu.grade = request.form.get("grade", "").strip()
        edu.details = request.form.get("details", "").strip()
        edu.display_order = _int_or_zero(request.form.get("display_order"))
        db.session.commit()
        flash("Education updated.", "success")
        return redirect(url_for("admin.education_list"))
    return render_template("admin/education_form.html", edu=edu)


@admin_bp.route("/education/<int:edu_id>/delete", methods=["POST"])
@login_required
def education_delete(edu_id):
    edu = Education.query.get_or_404(edu_id)
    db.session.delete(edu)
    db.session.commit()
    flash("Education entry deleted.", "info")
    return redirect(url_for("admin.education_list"))


# ── Learning items (nested under education page) ──
@admin_bp.route("/learning/new", methods=["POST"])
@login_required
def learning_new():
    topic = request.form.get("topic", "").strip()
    if not topic:
        flash("Topic is required.", "danger")
        return redirect(url_for("admin.education_list"))
    db.session.add(LearningItem(
        topic=topic,
        description=request.form.get("description", "").strip(),
        display_order=_int_or_zero(request.form.get("display_order")),
    ))
    db.session.commit()
    flash(f"'{topic}' added to Currently Learning.", "success")
    return redirect(url_for("admin.education_list"))


@admin_bp.route("/learning/<int:item_id>/delete", methods=["POST"])
@login_required
def learning_delete(item_id):
    item = LearningItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Learning item deleted.", "info")
    return redirect(url_for("admin.education_list"))


# ═════════════════════════════════════════════════════════════
# CERTIFICATIONS
# ═════════════════════════════════════════════════════════════
@admin_bp.route("/certifications")
@login_required
def certifications_list():
    certs = Certification.query.order_by(Certification.display_order).all()
    return render_template("admin/certifications_list.html", certifications=certs)


@admin_bp.route("/certifications/new", methods=["GET", "POST"])
@login_required
def certifications_new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name is required.", "danger")
            return redirect(url_for("admin.certifications_new"))

        image_url = ""
        file = request.files.get("image")
        if file and file.filename:
            try:
                image_url = save_file(file, folder="images")
            except ValueError as e:
                flash(str(e), "danger")
                return redirect(url_for("admin.certifications_new"))

        db.session.add(Certification(
            name=name,
            issuer=request.form.get("issuer", "").strip(),
            date_earned=request.form.get("date_earned", "").strip(),
            url=request.form.get("url", "").strip(),
            image_url=image_url,
            display_order=_int_or_zero(request.form.get("display_order")),
        ))
        db.session.commit()
        flash(f"Certification '{name}' added.", "success")
        return redirect(url_for("admin.certifications_list"))
    return render_template("admin/certifications_form.html", cert=None)


@admin_bp.route("/certifications/<int:cert_id>/edit", methods=["GET", "POST"])
@login_required
def certifications_edit(cert_id):
    cert = Certification.query.get_or_404(cert_id)
    if request.method == "POST":
        cert.name = request.form.get("name", "").strip()
        cert.issuer = request.form.get("issuer", "").strip()
        cert.date_earned = request.form.get("date_earned", "").strip()
        cert.url = request.form.get("url", "").strip()
        cert.display_order = _int_or_zero(request.form.get("display_order"))

        # ── Image upload ──
        file = request.files.get("image")
        if file and file.filename:
            if cert.image_url:
                delete_file(cert.image_url)
            try:
                cert.image_url = save_file(file, folder="images")
            except ValueError as e:
                flash(str(e), "danger")
                return redirect(url_for("admin.certifications_edit", cert_id=cert.id))

        db.session.commit()
        flash("Certification updated.", "success")
        return redirect(url_for("admin.certifications_list"))
    return render_template("admin/certifications_form.html", cert=cert)


@admin_bp.route("/certifications/<int:cert_id>/delete", methods=["POST"])
@login_required
def certifications_delete(cert_id):
    cert = Certification.query.get_or_404(cert_id)
    if cert.image_url:
        delete_file(cert.image_url)
    db.session.delete(cert)
    db.session.commit()
    flash("Certification deleted.", "info")
    return redirect(url_for("admin.certifications_list"))


# ═════════════════════════════════════════════════════════════
# BLOG
# ═════════════════════════════════════════════════════════════
@admin_bp.route("/blog")
@login_required
def blog_list():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template("admin/blog_list.html", posts=posts)


@admin_bp.route("/blog/new", methods=["GET", "POST"])
@login_required
def blog_new():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Title is required.", "danger")
            return redirect(url_for("admin.blog_new"))
        slug_input = request.form.get("slug", "").strip()
        base_slug = _slugify(slug_input or title)
        slug = _unique_slug(base_slug)

        cover_url = ""
        file = request.files.get("cover_image")
        if file and file.filename:
            try:
                cover_url = save_file(file, folder="images")
            except ValueError as e:
                flash(str(e), "danger")
                return redirect(url_for("admin.blog_new"))

        post = BlogPost(
            title=title,
            slug=slug,
            summary=request.form.get("summary", "").strip(),
            content=request.form.get("content", ""),
            cover_image_url=cover_url,
            tags=request.form.get("tags", "").strip(),
            published=bool(request.form.get("published")),
        )
        db.session.add(post)
        db.session.commit()
        flash(f"Post '{title}' created.", "success")
        return redirect(url_for("admin.blog_list"))
    return render_template("admin/blog_form.html", post=None)


@admin_bp.route("/blog/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def blog_edit(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if request.method == "POST":
        post.title = request.form.get("title", "").strip()
        new_slug_input = request.form.get("slug", "").strip()
        base_slug = _slugify(new_slug_input or post.title)
        if base_slug != post.slug:
            post.slug = _unique_slug(base_slug, exclude_id=post.id)
        post.summary = request.form.get("summary", "").strip()
        post.content = request.form.get("content", "")
        post.tags = request.form.get("tags", "").strip()
        post.published = bool(request.form.get("published"))
        file = request.files.get("cover_image")
        if file and file.filename:
            if post.cover_image_url:
                delete_file(post.cover_image_url)
            try:
                post.cover_image_url = save_file(file, folder="images")
            except ValueError as e:
                flash(str(e), "danger")
                return redirect(url_for("admin.blog_edit", post_id=post.id))
        db.session.commit()
        flash("Post updated.", "success")
        return redirect(url_for("admin.blog_list"))
    return render_template("admin/blog_form.html", post=post)


@admin_bp.route("/blog/<int:post_id>/delete", methods=["POST"])
@login_required
def blog_delete(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if post.cover_image_url:
        delete_file(post.cover_image_url)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "info")
    return redirect(url_for("admin.blog_list"))


# ═════════════════════════════════════════════════════════════
# MESSAGES
# ═════════════════════════════════════════════════════════════
@admin_bp.route("/messages")
@login_required
def messages_list():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin/messages_list.html", messages=messages)


@admin_bp.route("/messages/<int:msg_id>")
@login_required
def message_detail(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    if not msg.is_read:
        msg.is_read = True
        db.session.commit()
    return render_template("admin/message_detail.html", msg=msg)


@admin_bp.route("/messages/<int:msg_id>/delete", methods=["POST"])
@login_required
def message_delete(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash("Message deleted.", "info")
    return redirect(url_for("admin.messages_list"))


# ═════════════════════════════════════════════════════════════
# SITE SETTINGS
# ═════════════════════════════════════════════════════════════
@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    cfg = SiteConfig.get()

    if request.method == "POST":
        cfg.full_name = request.form.get("full_name", "").strip()
        cfg.title = request.form.get("title", "").strip()
        cfg.tagline = request.form.get("tagline", "").strip()
        cfg.bio = request.form.get("bio", "").strip()
        cfg.email = request.form.get("email", "").strip()
        cfg.location = request.form.get("location", "").strip()
        cfg.linkedin_url = request.form.get("linkedin_url", "").strip()
        cfg.github_url = request.form.get("github_url", "").strip()
        cfg.twitter_url = request.form.get("twitter_url", "").strip()
        cfg.kaggle_url = request.form.get("kaggle_url", "").strip()
        cfg.youtube_url = request.form.get("youtube_url", "").strip()

        # Profile photo
        photo = request.files.get("profile_photo")
        if photo and photo.filename:
            if cfg.profile_photo_url:
                delete_file(cfg.profile_photo_url)
            try:
                cfg.profile_photo_url = save_file(photo, folder="images")
            except ValueError as e:
                flash(f"Photo: {e}", "danger")

        # CV PDF
        cv = request.files.get("cv_pdf")
        if cv and cv.filename:
            if cfg.cv_pdf_url:
                delete_file(cfg.cv_pdf_url)
            try:
                cfg.cv_pdf_url = save_file(cv, folder="pdfs")
            except ValueError as e:
                flash(f"CV: {e}", "danger")

        db.session.commit()
        flash("Settings saved.", "success")
        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html", cfg=cfg)


# ═════════════════════════════════════════════════════════════
# CHANGE PASSWORD
# ═════════════════════════════════════════════════════════════
@admin_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_pw = request.form.get("current_password", "")
        new_pw = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")

        if not check_password_hash(current_user.password_hash, current_pw):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("admin.change_password"))
        if len(new_pw) < 8:
            flash("New password must be at least 8 characters.", "danger")
            return redirect(url_for("admin.change_password"))
        if new_pw != confirm:
            flash("New passwords do not match.", "danger")
            return redirect(url_for("admin.change_password"))

        current_user.password_hash = generate_password_hash(new_pw)
        db.session.commit()
        flash("Password changed successfully.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/change_password.html")