from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.storage import save_file
from app.models import (
    db,
    SiteConfig,
    Project,
    Resource,
    Skill,
    Education,
    Certification,
    LearningItem,
    BlogPost,
    ContactMessage,
)

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    cfg = SiteConfig.get()
    projects = (
        Project.query.order_by(Project.display_order, Project.id.desc()).limit(3).all()
    )
    resources = Resource.query.order_by(
        Resource.display_order, Resource.id.desc()
    ).limit(2).all()
    return render_template(
        "index.html",
        page=None,
        cfg=cfg,
        projects=projects,
        resources=resources,
    )



@public_bp.route("/projects")
def projects():
    all_projects = Project.query.order_by(
        Project.display_order, Project.id.desc()
    ).all()
    return render_template("projects.html", page="Projects", cfg=SiteConfig.get(), projects=all_projects)



@public_bp.route("/resources")
def resources():
    all_resources = Resource.query.order_by(
        Resource.display_order, Resource.id.desc()
    ).all()
    return render_template("resources.html", page="Resources", cfg=SiteConfig.get(), resources=all_resources)


@public_bp.route("/skills")
def skills():
    grouped = {}
    for s in Skill.query.order_by(Skill.category, Skill.display_order).all():
        grouped.setdefault(s.category, []).append(s)
    return render_template("skills.html", page="Skills", cfg=SiteConfig.get(), skills_grouped=grouped)


@public_bp.route("/education")
def education():
    items = Education.query.order_by(Education.display_order).all()
    certs = Certification.query.order_by(Certification.display_order).all()
    learning = LearningItem.query.order_by(LearningItem.display_order).all()
    return render_template(
        "education.html",
        page="Education",
        cfg=SiteConfig.get(),
        education=items,
        certifications=certs,
        learning=learning,
    )

@public_bp.route("/blog")
def blog():
    posts = (
        BlogPost.query.filter_by(published=True)
        .order_by(BlogPost.created_at.desc())
        .all()
    )
    return render_template("blog.html", page="Blog", cfg=SiteConfig.get(), posts=posts)



@public_bp.route("/blog/<slug>")
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template("blog_post.html", page=post.title, cfg=SiteConfig.get(), post=post)


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    cfg = SiteConfig.get()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not (name and email and message):
            flash("Please fill in all required fields.", "warning")
            return redirect(url_for("public.contact"))

        msg = ContactMessage(name=name, email=email, subject=subject, message=message)
        db.session.add(msg)
        db.session.commit()

        flash("Thanks for reaching out! I'll get back to you soon.", "success")
        return redirect(url_for("public.contact"))

    return render_template("contact.html", page="Contact", cfg=cfg)

