# Bishal Majumdar — Portfolio

**🔗 Live site:** [https://myportfolio-evum.onrender.com](https://myportfolio-evum.onrender.com)

Dynamic personal portfolio built with Flask, PostgreSQL (Neon), and Cloudflare R2.

![Portfolio screenshot](https://myportfolio-evum.onrender.com/static/img/og-preview.png)

> Replace the screenshot URL above with an actual image once you upload one to R2 (or delete the line).

---

## Stack

- **Backend:** Flask 3 + SQLAlchemy + Flask-Migrate
- **Database:** PostgreSQL (Neon, free tier)
- **File storage:** Cloudflare R2 (free tier, S3-compatible)
- **Deployment:** Docker + Render
- **Server:** Gunicorn

## Features

- Dynamic content — all sections editable via a built-in admin panel
- Projects, resources, skills, education, certifications, blog posts
- File uploads (profile photo, CV, project images) to Cloudflare R2
- Contact form with message inbox
- Responsive white + green theme
- Fully self-hosted — no third-party CMS

## Local Development

### 1. Clone and enter

```bash
git clone https://github.com/NeuralBishal/Portfolio.git
cd Portfolio
