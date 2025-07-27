# Grateful For API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

A RESTful API for a digital journaling application designed to encourage gratitude and mindful reflection.

## Overview

This project provides the backend services for "Grateful For". It allows users to create, manage, and reflect on their journal entries, with features for community sharing and personal analytics. The API is built with Django and Django REST Framework, using JSON Web Tokens (JWT) for authentication.

## Features

- **User Authentication**: Secure registration, login (email/password and Google OAuth2), and session management using JWT.
- **Journal Management**: Full CRUD (Create, Read, Update, Delete) operations for journal entries.
- **Daily Entry Limit**: Users can create up to three entries per day to encourage thoughtful posts.
- **Personal Analytics**: Track journaling habits, including total entries, monthly counts, and consecutive day streaks.
- **Calendar View**: Visualize entry history on a monthly calendar.
- **Community Feed**: Anonymized, randomized feed of public journal entries from the community.
- **User Profiles**: Manage user account information and view a personal dashboard.
- **Security**: Includes rate limiting on login attempts to prevent brute-force attacks.

## Tech Stack

- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL (recommended)
- **Authentication**: JSON Web Tokens (JWT), Google OAuth2
- **Containerization**: Docker, Docker Compose
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

3.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build -d
    ```
    The `-d` flag runs the containers in detached mode. The `entrypoint.sh` script will automatically run database migrations. The application will be available at `http://127.0.0.1:8000/`.

4.  **Create a superuser (Optional):**
    To create a superuser for admin access, run the following command:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

5.  **Stopping the application:**
    To stop the containers, run:
    ```bash
    docker-compose down
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

## API Endpoints

The API root is discoverable at `/api/v1/` and provides a list of all available endpoints. All data is exchanged in JSON format.

### Authentication

Handles user accounts, authentication tokens, and account management flows.

- `POST /api/v1/auth/registration/`: Create a new user account.
- `POST /api/v1/auth/login/`: Authenticate with email and password to receive JWTs.
- `POST /api/v1/auth/logout/`: Blacklist a refresh token to log out.
- `POST /api/v1/auth/token/refresh/`: Refresh an expired access token.
- `POST /api/v1/auth/google/`: Authenticate with access token from Google OAuth2 to receive JWTs.
- `POST /api/v1/auth/password/reset/`: Request a password reset email.
- `GET /api/v1/auth/password/reset/confirm/<uid>/<token>/`: (From email link) Redirects to frontend to complete reset.
- `POST /api/v1/auth/password/reset/confirm/`: (From frontend) Submits the new password.
- `POST /api/v1/auth/registration/resend-email/`: Resend the email verification link.
- `GET /api/v1/auth/registration/verify-email/<key>/`: (From email link) Redirects to frontend to complete verification.
- `POST /api/v1/auth/registration/verify-email/`: (From frontend) Submits the verification key.

### Journal

Endpoints for managing journal entries. All require authentication.

- `GET, POST /api/v1/journal/entries/`: List all of the user's entries or create a new one.
- `GET, PATCH, DELETE /api/v1/journal/entries/<entry_id>/`: Retrieve, update, or delete a specific entry.
- `GET /api/v1/journal/analytics/`: Get statistics about the user's entries.
- `GET /api/v1/journal/calendar/`: Get a calendar view of entries for a given month and year.

### Community

Endpoints for community features. All require authentication.

- `GET /api/v1/community/feed/`: Get a randomized feed of public journal entries. Supports `?period=today|week` and `?refresh=true` query parameters.

### User

Endpoints for user-specific data. All require authentication.

- `GET /api/v1/dashboard/`: Get dashboard data including recent entries and stats.
- `GET, PATCH /api/v1/account-management/`: Retrieve or update the authenticated user's account information.

---

## API Information

### Versioning

The API is currently at version `v1`. All endpoints are prefixed with `/api/v1/`.

-   **Backwards Compatibility**: We strive to make only backwards-compatible changes, such as adding new endpoints or new optional properties to existing responses.
-   **Breaking Changes**: Any backwards-incompatible changes will result in a new API version (e.g., `/api/v2/`).
-   **Deprecation**: Deprecated endpoints will be supported for at least 6 months after a new version is released.

### Interactive Documentation

You can explore the API interactively using the built-in documentation interfaces when the server is running:

-   **Swagger UI**: `/swagger/`
-   **ReDoc**: `/redoc/`

For example, on a local development server, you would visit `http://127.0.0.1:8000/swagger/`.

### Support

For technical support, questions, or feedback:

-   **Email:** `olujay.dev@gmail.com`
-   **Discord:** `@olujay`

We aim to respond to support requests within 48 hours.

### Changelog

**Version 1.0.0 (Current)**
-   Initial public release of the API.
-   Core features for user management, journaling, and community interaction.

<!-- ## Running Tests
*(This section can be filled out once tests are added to the project.)*

```bash
# Example command
pytest
``` -->

## Contributing

Contributions are welcome! Please see our Contributing Guide for more details on how to set up your development environment, run tests, and submit pull requests.