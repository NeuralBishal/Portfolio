from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


# ─────────────────────────────────────────────────────────────
# 1. ADMIN USER (for the admin panel login)
# ─────────────────────────────────────────────────────────────
class AdminUser(UserMixin, db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────────────────────
# 2. SITE CONFIG (singleton row — your bio, tagline, socials, CV)
# ─────────────────────────────────────────────────────────────
class SiteConfig(db.Model):
    __tablename__ = "site_config"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), default="Bishal Majumdar")
    title = db.Column(db.String(200), default="B.Tech CSE (AI & ML) Student")
    tagline = db.Column(db.String(300), default="")
    bio = db.Column(db.Text, default="")
    email = db.Column(db.String(120), default="bishalmajumdar505@gmail.com")
    location = db.Column(db.String(200), default="Durgapur, West Bengal, India")

    # Social links
    linkedin_url = db.Column(db.String(300), default="")
    github_url = db.Column(db.String(300), default="")
    twitter_url = db.Column(db.String(300), default="")
    kaggle_url = db.Column(db.String(300), default="")
    youtube_url = db.Column(db.String(300), default="")

    # Uploaded media URLs (populated via admin panel — R2 URLs)
    profile_photo_url = db.Column(db.String(500), default="")
    cv_pdf_url = db.Column(db.String(500), default="")

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get():
        """Fetch the single config row, or create it if missing."""
        cfg = SiteConfig.query.first()
        if not cfg:
            cfg = SiteConfig()
            db.session.add(cfg)
            db.session.commit()
        return cfg


# ─────────────────────────────────────────────────────────────
# 3. PROJECT
# ─────────────────────────────────────────────────────────────
class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    tech_stack = db.Column(db.String(300), default="")   # comma-separated
    github_url = db.Column(db.String(500), default="")
    demo_url = db.Column(db.String(500), default="")
    image_url = db.Column(db.String(500), default="")    # R2 URL

    # "live" | "private" | "coming-soon"
    status = db.Column(db.String(30), default="live")

    featured = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def tech_list(self):
        """Split comma-separated tech into a list for templates."""
        if not self.tech_stack:
            return []
        return [t.strip() for t in self.tech_stack.split(",") if t.strip()]

    @property
    def status_label(self):
        return {
            "live": "✅ Live",
            "private": "🔒 Private",
            "coming-soon": "🚧 Coming Soon",
        }.get(self.status, self.status)


# ─────────────────────────────────────────────────────────────
# 4. RESOURCE (open-source / learning materials section)
# ─────────────────────────────────────────────────────────────
class Resource(db.Model):
    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    tagline = db.Column(db.String(300), default="")
    description = db.Column(db.Text, default="")
    topics = db.Column(db.String(300), default="")       # comma-separated
    url = db.Column(db.String(500), default="")
    image_url = db.Column(db.String(500), default="")
    status = db.Column(db.String(30), default="growing") # growing | stable | archived
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def topic_list(self):
        if not self.topics:
            return []
        return [t.strip() for t in self.topics.split(",") if t.strip()]

    @property
    def status_label(self):
        return {
            "growing": "🚧 Actively Growing",
            "stable": "✅ Stable",
            "archived": "📦 Archived",
        }.get(self.status, self.status)


# ─────────────────────────────────────────────────────────────
# 5. SKILL (grouped by category in templates)
# ─────────────────────────────────────────────────────────────
class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)  # e.g. "Programming"
    name = db.Column(db.String(100), nullable=False)      # e.g. "Python"
    display_order = db.Column(db.Integer, default=0)


# ─────────────────────────────────────────────────────────────
# 6. EDUCATION
# ─────────────────────────────────────────────────────────────
class Education(db.Model):
    __tablename__ = "education"

    id = db.Column(db.Integer, primary_key=True)
    institution = db.Column(db.String(200), nullable=False)
    degree = db.Column(db.String(200), default="")
    start_year = db.Column(db.String(20), default="")
    end_year = db.Column(db.String(20), default="")
    grade = db.Column(db.String(100), default="")
    details = db.Column(db.Text, default="")
    display_order = db.Column(db.Integer, default=0)


# ─────────────────────────────────────────────────────────────
# 7. CERTIFICATION
# ─────────────────────────────────────────────────────────────
class Certification(db.Model):
    __tablename__ = "certifications"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    issuer = db.Column(db.String(200), default="")
    date_earned = db.Column(db.String(50), default="")
    url = db.Column(db.String(500), default="")
    image_url = db.Column(db.String(500), default="")      # ← ADD THIS
    display_order = db.Column(db.Integer, default=0)


# ─────────────────────────────────────────────────────────────
# 8. LEARNING ITEM (Currently Learning)
# ─────────────────────────────────────────────────────────────
class LearningItem(db.Model):
    __tablename__ = "learning_items"

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    display_order = db.Column(db.Integer, default=0)


# ─────────────────────────────────────────────────────────────
# 9. BLOG POST
# ─────────────────────────────────────────────────────────────
class BlogPost(db.Model):
    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True, nullable=False)
    summary = db.Column(db.String(500), default="")
    content = db.Column(db.Text, default="")              # Markdown-ish / HTML
    cover_image_url = db.Column(db.String(500), default="")
    tags = db.Column(db.String(300), default="")          # comma-separated
    published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",") if t.strip()]


# ─────────────────────────────────────────────────────────────
# 10. CONTACT MESSAGE (from the contact form)
# ─────────────────────────────────────────────────────────────
class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), default="")
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)