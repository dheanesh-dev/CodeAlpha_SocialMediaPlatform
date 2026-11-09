# Circle — CodeAlpha Social Media Platform

A small Django social app for CodeAlpha internship Task 2. Members can create a profile, share posts, comment, like posts, follow other members, and discover people.

## Features

- Register, log in, and log out
- Browse a paginated community feed
- Create and delete your own posts
- Comment on posts and delete your own comments
- Like and unlike posts
- View profiles, edit your bio, and see post/follower/following counts
- Follow and unfollow members
- Search members by username or first name
- Responsive layout with character counters, confirmation prompts, accessible keyboard focus, and empty states

## Requirements

- Windows 10 or 11
- Python 3.11 or newer
- VS Code (recommended)
- Internet access for the first dependency installation

## Open the project in VS Code

Open VS Code, choose **File → Open Folder**, and select **CodeAlpha_SocialMediaPlatform**. You can also open PowerShell in the project folder and run:

    code .

## Install and run (PowerShell)

Run these commands from the project folder:

    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    Copy-Item .env.example .env

Generate a fresh development key and save it into .env:

    $secret = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    (Get-Content .env) -replace '^DJANGO_SECRET_KEY=.*$', "DJANGO_SECRET_KEY=$secret" | Set-Content .env

The .env file is read locally and ignored by Git. Never commit it. The provided .env.example contains only a placeholder, not a usable production key.

If PowerShell blocks activation, use this for the current terminal window only, then activate the environment again:

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

## Prepare the database

Apply the included migrations:

    python manage.py migrate

Create an administrator account if you want to use the Django admin:

    python manage.py createsuperuser

Start the development server:

    python manage.py runserver

Open http://127.0.0.1:8000/ in your browser. The admin site is at http://127.0.0.1:8000/admin/.

## Using Circle

1. Register a username and password.
2. Add a short introduction from **My profile → Edit profile**.
3. Write a post on the home page.
4. Open a post to comment, or use the heart button to like it.
5. Use **Discover** to search for other members and follow them.
6. Use your profile page to review your posts and follower counts.

Each account receives a profile automatically. Posts, comments, and profile bios have server-side length limits. Only the author can delete their own posts and comments.

## Upload to GitHub

1. Create an empty GitHub repository for this task, for example **CodeAlpha_SocialMediaPlatform**.
2. In GitHub Desktop, choose **File → Add local repository…** and select this project folder.
3. Review the changed files. Confirm that .env and db.sqlite3 are not included.
4. Commit the project and publish the repository.

If using Git in PowerShell instead, run:

    git init
    git add .
    git status --short
    git commit -m "Build CodeAlpha social media platform"
    git branch -M main
    git remote add origin https://github.com/YOUR-USERNAME/CodeAlpha_SocialMediaPlatform.git
    git push -u origin main

Replace YOUR-USERNAME with your GitHub username. If GitHub Desktop already initialized the folder, do not run git init again. Never add .env or db.sqlite3 to the repository.

## Security and deployment note

This project is configured for local learning and evaluation. DEBUG is enabled by the example .env for local development. Before deploying it publicly, set DJANGO_DEBUG=False, configure DJANGO_ALLOWED_HOSTS for the real domain, use HTTPS, and review Django's deployment checklist. Do not use the development server for production.
