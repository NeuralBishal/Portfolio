"""
Seed script — populates the portfolio with initial data.

Usage:
    docker compose exec web python seed.py
    # or, if running locally:
    python seed.py

Idempotent — safe to run multiple times. It checks for existing
records before inserting, so you won't get duplicates.
"""

import os
import sys
from datetime import datetime

from app import create_app
from app.models import (
    db, AdminUser, SiteConfig,
    Project, Resource, Skill, Education, Certification,
    LearningItem, BlogPost,
)
from werkzeug.security import generate_password_hash


def _get_or_create(model, defaults=None, **filters):
    """Fetch first matching row; if none, create it with defaults."""
    obj = model.query.filter_by(**filters).first()
    if obj:
        return obj, False
    obj = model(**{**filters, **(defaults or {})})
    db.session.add(obj)
    return obj, True


def seed():
    app = create_app()
    with app.app_context():

        # ────────────────────────────────────────────────────
        # ADMIN USER
        # ────────────────────────────────────────────────────
        username = os.environ.get("ADMIN_USERNAME", "bishal")
        password = os.environ.get("ADMIN_PASSWORD", "changeme123")

        user, created = _get_or_create(
            AdminUser,
            username=username,
            defaults={"password_hash": generate_password_hash(password)},
        )
        print(f"{'✅ Created' if created else '⏭️  Exists'} admin user: {username}")

        # ────────────────────────────────────────────────────
        # SITE CONFIG
        # ────────────────────────────────────────────────────
        cfg = SiteConfig.get()
        cfg.full_name = cfg.full_name or "Bishal Majumdar"
        cfg.title = cfg.title or "B.Tech CSE (AI & ML) Student"
        cfg.tagline = (
            cfg.tagline
            or "Building intelligent systems at the intersection of computer vision and embedded hardware."
        )
        cfg.bio = cfg.bio or (
            "<p>I'm a third-year B.Tech student specializing in Artificial Intelligence "
            "and Machine Learning at Dr. B.C. Roy Engineering College, Durgapur. My interests "
            "sit at the intersection of computer vision, embedded systems, and practical software "
            "— I love building tools that solve real problems.</p>"
            "<p>Right now I'm working on a CCTV-based automated attendance system, exploring "
            "Whisper for multilingual subtitle generation, and writing beginner-friendly guides "
            "on tools like Conda, Docker, and Git for students who — like me — started from zero.</p>"
        )
        cfg.email = cfg.email or "bishalmajumdar505@gmail.com"
        cfg.location = cfg.location or "Durgapur, West Bengal, India"
        cfg.linkedin_url = cfg.linkedin_url or "https://www.linkedin.com/in/neural-bishal-01627136a/"
        cfg.github_url = cfg.github_url or "https://github.com/NeuralBishal"
        cfg.twitter_url = cfg.twitter_url or "https://x.com/Bishal1Majumdar"
        cfg.kaggle_url = cfg.kaggle_url or "https://www.kaggle.com/bishalmajumdar"
        cfg.youtube_url = cfg.youtube_url or "https://www.youtube.com/@esbbmgamingyt"
        print("✅ Site config initialized")

        # ────────────────────────────────────────────────────
        # PROJECTS
        # ────────────────────────────────────────────────────
        projects_data = [
            {
                "title": "Automated Attendance System",
                "description": (
                    "CCTV-based automatic attendance system using Python and OpenCV. "
                    "Applies face recognition to reduce manual attendance effort by an expected 80%."
                ),
                "tech_stack": "Python, OpenCV, Face Recognition",
                "github_url": "https://github.com/NeuralBishal/automatic-attendance-system-AAS-",
                "demo_url": "",
                "status": "private",
                "featured": True,
                "display_order": 1,
            },
            {
                "title": "Intelligent Video Processing & Subtitle System",
                "description": (
                    "Multi-format video extraction with Whisper-powered subtitle generation "
                    "(~85–90% accuracy) and lexical simplification to reduce text complexity by ~40%."
                ),
                "tech_stack": "Python, OpenCV, Whisper, Streamlit, FFmpeg",
                "github_url": "https://github.com/NeuralBishal/video-frame-extractor",
                "demo_url": "https://video-frame-extractor-ypuahusgncnfuzp5ekdebd.streamlit.app/",
                "status": "live",
                "featured": True,
                "display_order": 2,
            },
            {
                "title": "CIACON 2026 Demo Website",
                "description": (
                    "Responsive demo website for an AI builders conference — includes event details, "
                    "agenda, speaker highlights, calls to action, and conference statistics."
                ),
                "tech_stack": "HTML, CSS, JavaScript, Python",
                "github_url": "https://github.com/NeuralBishal/ciacon2026-demo-website",
                "demo_url": "https://ciacon2026-demo-website.onrender.com/",
                "status": "live",
                "featured": True,
                "display_order": 3,
            },
        ]

        for data in projects_data:
            _, created = _get_or_create(Project, title=data["title"], defaults=data)
            print(f"{'✅ Created' if created else '⏭️  Exists'} project: {data['title']}")

        # ────────────────────────────────────────────────────
        # RESOURCES
        # ────────────────────────────────────────────────────
        resources_data = [
            {
                "title": "From Zero To Deployment",
                "tagline": "Beginner-friendly guides for Git, Conda, Docker, and terminal workflows.",
                "description": (
                    "<p>A growing resource hub covering the tools and technologies today's "
                    "software and DevOps engineers need.</p>"
                    "<p>Written from a beginner's perspective — I came from a biology background "
                    "with zero coding experience, so every concept is explained without assuming "
                    "any prior knowledge.</p>"
                ),
                "topics": "Conda, Docker, Git, Terminal, Beginner Guides",
                "url": "https://github.com/NeuralBishal/From-Zero-To-Deployment",
                "status": "growing",
                "display_order": 1,
            },
        ]

        for data in resources_data:
            _, created = _get_or_create(Resource, title=data["title"], defaults=data)
            print(f"{'✅ Created' if created else '⏭️  Exists'} resource: {data['title']}")

        # ────────────────────────────────────────────────────
        # SKILLS
        # ────────────────────────────────────────────────────
        skills_data = [
            # (category, name, display_order)
            ("Programming", "Python", 1),
            ("Programming", "C", 2),
            ("Programming", "Embedded C", 3),
            ("Programming", "HTML", 4),
            ("Programming", "CSS", 5),
            ("Programming", "JavaScript", 6),

            ("AI / ML", "Scikit-learn", 1),
            ("AI / ML", "OpenCV", 2),
            ("AI / ML", "Whisper", 3),

            ("Data & Visualization", "NumPy", 1),
            ("Data & Visualization", "Pandas", 2),
            ("Data & Visualization", "Matplotlib", 3),
            ("Data & Visualization", "Microsoft Excel", 4),
            ("Data & Visualization", "Power BI", 5),

            ("Tools", "Jupyter", 1),
            ("Tools", "VS Code", 2),
            ("Tools", "Google Colab", 3),
            ("Tools", "Render", 4),
            ("Tools", "KiCad", 5),
        ]

        for category, name, order in skills_data:
            _, created = _get_or_create(
                Skill,
                category=category,
                name=name,
                defaults={"display_order": order},
            )
            if created:
                print(f"✅ Skill: {category} → {name}")

        # ────────────────────────────────────────────────────
        # EDUCATION
        # ────────────────────────────────────────────────────
        education_data = [
            {
                "institution": "Dr. B.C. Roy Engineering College, Durgapur",
                "degree": "B.Tech in CSE (Artificial Intelligence and Machine Learning)",
                "start_year": "2024",
                "end_year": "2028",
                "grade": "YGPA: 8.69/10 (Year 1); SGPA: 9.14/10 (Semester 3)",
                "details": "",
                "display_order": 1,
            },
            {
                "institution": "Benachity High School, Durgapur",
                "degree": "Higher Secondary (WBCHSE)",
                "start_year": "2019",
                "end_year": "2021",
                "grade": "89.6% (448/500)",
                "details": "Physics: 90, Chemistry: 91, Mathematics: 88, Biology: 91",
                "display_order": 2,
            },
        ]

        for data in education_data:
            _, created = _get_or_create(
                Education, institution=data["institution"], defaults=data
            )
            print(f"{'✅ Created' if created else '⏭️  Exists'} education: {data['institution']}")

        # ────────────────────────────────────────────────────
        # CERTIFICATIONS
        # ────────────────────────────────────────────────────
        certs_data = [
            {
                "name": "Embedded Systems with 8051 & Embedded C",
                "issuer": "Udemy",
                "date_earned": "July 3, 2026",
                "url": "",
                "display_order": 1,
            },
        ]

        for data in certs_data:
            _, created = _get_or_create(Certification, name=data["name"], defaults=data)
            print(f"{'✅ Created' if created else '⏭️  Exists'} certification: {data['name']}")

        # ────────────────────────────────────────────────────
        # LEARNING ITEMS
        # ────────────────────────────────────────────────────
        learning_data = [
            {
                "topic": "KiCad for PCB Design",
                "description": "Learning to design printed circuit boards from scratch.",
                "display_order": 1,
            },
            {
                "topic": "Embedded Systems with 8051",
                "description": "Register-level programming and microcontroller fundamentals.",
                "display_order": 2,
            },
            {
                "topic": "OpenCV through 35 practical projects",
                "description": "Deepening computer vision skills via hands-on mini-projects.",
                "display_order": 3,
            },
        ]

        for data in learning_data:
            _, created = _get_or_create(
                LearningItem, topic=data["topic"], defaults=data
            )
            print(f"{'✅ Created' if created else '⏭️  Exists'} learning item: {data['topic']}")

        # ────────────────────────────────────────────────────
        # SAMPLE BLOG POST
        # ────────────────────────────────────────────────────
        _, created = _get_or_create(
            BlogPost,
            slug="why-i-built-from-zero-to-deployment",
            defaults={
                "title": "Why I Built 'From Zero To Deployment'",
                "slug": "why-i-built-from-zero-to-deployment",
                "summary": (
                    "A short note on why I'm writing beginner-friendly guides for tools "
                    "nobody teaches you in first year."
                ),
                "content": (
                    "<p>When I started engineering, I had no coding background. Every tutorial "
                    "assumed I already knew the basics. I spent months copying commands without "
                    "understanding them.</p>"
                    "<p>So I started writing the guide I wish I had — one that assumes nothing "
                    "and explains everything from the ground up. It's called "
                    "<strong>From Zero To Deployment</strong>.</p>"
                    "<p>If you're a student who feels lost, that repository is for you.</p>"
                ),
                "tags": "learning, guides, beginner",
                "published": False,  # Draft — you can review and publish from the admin panel
            },
        )
        print(f"{'✅ Created' if created else '⏭️  Exists'} blog post: Why I Built...")

        # ────────────────────────────────────────────────────
        # COMMIT
        # ────────────────────────────────────────────────────
        db.session.commit()
        print("\n✅ Seed complete.\n")


if __name__ == "__main__":
    try:
        seed()
    except Exception as e:
        print(f"\n❌ Seed failed: {e}", file=sys.stderr)
        sys.exit(1)