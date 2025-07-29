# Grateful For API

[![CI](https://github.com/theolujay/grateful_for/actions/workflows/ci.yml/badge.svg)](https://github.com/theolujay/grateful_for/actions/workflows/ci.yml)

A RESTful API for a digital journaling application designed to encourage gratitude and mindful reflection.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This project provides the backend services for "Grateful For". It allows users to create, manage, and reflect on their journal entries, with features for community sharing and personal analytics. The API is built with Django and Django REST Framework, using JSON Web Tokens (JWT) for authentication.

## Features

- **User Authentication**: Secure registration, login (email/password and Google OAuth2), and session management using JWT.
- **Journal Management**: Full CRUD (Create, Read, Update, Delete) operations for journal entries.
- **Daily Entry Limit**: Users can create up to three entries per day to encourage thoughtful posts.
- **Asynchronous Tasks**: Offloads slow operations like email sending to a background worker using Celery and Redis.
- **Personal Analytics**: Track journaling habits, including total entries, monthly counts, and consecutive day streaks.
- **Calendar View**: Visualize entry history on a monthly calendar.
- **Community Feed**: Anonymized, randomized feed of public journal entries from the community.
- **User Profiles**: Manage user account information and view a personal dashboard.
- **Security**: Includes rate limiting on login attempts to prevent brute-force attacks.

## Tech Stack

- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL (recommended)
- **Authentication**: JSON Web Tokens (JWT), Google OAuth2
- **Asynchronous Tasks**: Celery, Redis
- **Containerization**: Docker, Docker Compose
- **Task Monitoring**: Flower
- **API Documentation**: Swagger (drf-yasg) / ReDoc / Hand-written

---

## Prerequisites

- Python 3.11+
- Django 5+
- A PostgreSQL database is recommended for production.
- Docker and Docker Compose (for containerized setup)

## Setup and Installation

You can set up the project using Docker (recommended for ease of use and consistency) or manually.

### Using Docker (Recommended)

This project is configured to run with Docker and Docker Compose for a streamlined development setup.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/theolujay/grateful_for
    cd grateful_for
    ```

2.  **Configure environment variables:**
    Create a `.env` file in the project root by copying the `example.env` template. This file is used by Docker Compose to configure the application and database containers.
    ```env
    SECRET_KEY='your-super-secret-key'
    DEBUG=True # Set to False in production

    # PostgreSQL settings for Docker Compose
    POSTGRES_DB=grateful_for_db
    POSTGRES_USER=grateful_for_user
    POSTGRES_PASSWORD=a_secure_password
    DATABASE_URL='postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}'

    # Frontend Redirect URLs
    EMAIL_CONFIRM_REDIRECT_BASE_URL='http://localhost:3000/auth/email/confirm/' # Note the trailing slash
    PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL='http://localhost:3000/auth/password/reset/confirm/' # Note the trailing slash
    # ... other settings for email, Google OAuth, etc.
    ```

3.  **Make the entrypoint script executable:**
    The script that starts the application inside the container needs execute permissions. When you clone a repository, these permissions are not always preserved. Run this command in your terminal:
    ```bash
    chmod +x entrypoint.sh
    ```

4.  **Build and run with Docker Compose:**
    ```bash
    docker compose up --build -d
    ```
    The `-d` flag runs the containers in detached mode. The `entrypoint.sh` script will automatically run database migrations. The application will be available at `http://127.0.0.1:8000/`.

5.  **Accessing Services:**
    -   **API**: `http://127.0.0.1:8000/api/v1/`
    -   **Admin**: `http://127.0.0.1:8000/admin/`
    -   **Flower (Task Monitoring)**: `http://localhost:5555/`

6.  **Create a superuser (Optional):**
    To create a superuser for admin access, run the following command:
    ```bash
    docker compose exec web python manage.py createsuperuser
    ```

7.  **Stopping the application:**
    To stop the containers, run:
    ```bash
    docker compose down
    ```

### Manual Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/theolujay/grateful_for
    cd grateful_for
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On macOS/Linux: source .venv/bin/activate
    # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:** `pip install -r requirements.txt`

4.  **Configure environment variables:** Create a `.env` file as shown in the Docker setup, but point `DATABASE_URL` to your local database instance (e.g., `postgres://user:password@localhost:5432/dbname` or `sqlite:///db.sqlite3` for local development).

5.  **Run database migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000/`, with the API root at `http://127.0.0.1:8000/api/v1/`.

## API Documentation

For detailed information on all API endpoints, request/response formats, and authentication, please see the full API Documentation.

Interactive documentation (Swagger/ReDoc) is also available when the server is running. See the full documentation for links.

## Running Tests

To run the automated tests for the project, use `pytest`. You can run the tests inside the Docker container after ensuring all dependencies from `requirements.txt` are installed:

```bash
docker compose exec web pytest
```

## Contributing

Contributions are welcome! Please see our Contributing Guide for more details on how to set up your development environment, run tests, and submit pull requests.
