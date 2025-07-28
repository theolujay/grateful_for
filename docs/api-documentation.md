# Grateful For API Documentation
 
## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Journal Endpoints](#journal-endpoints)
  - [Community Endpoints](#community-endpoints)
  - [User Endpoints](#user-endpoints)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Versioning](#versioning)
- [Interactive Documentation](#interactive-documentation)
- [Support](#support)
- [Changelog](#changelog)

---

## Overview

Welcome to the Grateful For API documentation. This guide provides detailed information about the available endpoints, request formats, and response structures to help you build a frontend application that interacts with our services.

---

## Base URL

All API endpoints are prefixed with the following base URL.

**Production:**
`https://api.gratefulfor.com/api/v1/`

**Local Development:**
`http://127.0.0.1:8000/api/v1/`

## Authentication

Most endpoints require authentication using JSON Web Tokens (JWT). After a successful login, you will receive an `access` and a `refresh` token.

You must include the `access` token in the `Authorization` header for all protected requests. The scheme is `Bearer`.

**Example Header:**
```
Authorization: Bearer <your_access_token>
```

When the access token expires, your application should use the `refresh` token with the `/auth/token/refresh/` endpoint to obtain a new pair of tokens without requiring the user to log in again.

---

## API Endpoints

## Authentication Endpoints

This collection of endpoints handles user registration, login, logout, and account management tasks like password resets and email verification.

### 1. Register User

Creates a new user account. An email verification link will be sent to the provided email address.

> **Note:** This process is asynchronous. The API will respond immediately, and the verification email will be sent in the background.

- **Endpoint:** `POST /auth/registration/`
- **Authentication:** None

#### Request Body

```json
{
  "email": "new.user@example.com",
  "password1": "a-very-strong-password-123!",
  "password2": "a-very-strong-password-123!",
  "first_name": "New",
  "phone": "123-456-7890",
  "date_of_birth": "1995-05-10"
}

```

#### Responses

- **`201 Created`**
  Indicates that the user account was created successfully.

  ```json
  {
    "access_token": "...",
    "refresh_token": "...",
    "user": {
        "id": "...",
        "email": "new.user@example.com",
        "first_name": "New",
        "phone": "123-456-7890",
        "date_of_birth": "1995-05-10",
        "date_joined": "..."
    }
  }
  ```

- **`400 Bad Request`**
  Occurs if the provided data is invalid (e.g., email already exists, passwords don't match).

  ```json
  {
    "email": [
      "user with this email address already exists."
    ]
  }
  ```

---

### 2. Login User

Authenticates a user with their email and password and returns JWT access and refresh tokens.

- **Endpoint:** `POST /auth/login/`
- **Authentication:** None

#### Request Body

```json
{
  "email": "new.user@example.com",
  "password": "a-very-strong-password-123!"
}
```

#### Responses

- **`200 OK`**
  Successful authentication. The `access` and `refresh` tokens are returned.

  ```json
  {
    "detail": "Login successful",
    "tokens": {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    },
    "user": {
        "id": "...",
        "email": "new.user@example.com",
        "first_name": "New",
        "phone": "123-456-7890",
        "date_of_birth": "1995-05-10",
        "date_joined": "..."
    },
    "user_route": "/api/v1/dashboard/"
  }
  ```

- **`401 Unauthorized`**
  Invalid credentials provided.

  ```json
  {
    "detail": "No active account found with the given credentials"
  }
  ```

---

### 3. Logout User

Blacklists a refresh token, effectively logging the user out and preventing the token from being used to generate new access tokens.

- **Endpoint:** `POST /auth/logout/`
- **Authentication:** Required

#### Request Body

```json
{
  "refresh_token": "<your_refresh_token>"
}
```

#### Responses

- **`200 OK`**
  The refresh token was successfully blacklisted.

  ```json
  {
      "detail": "Logout successful"
  }
  ```

- **`400 Bad Request`**
  The provided token is invalid or expired.

  ```json
  {
    "detail": "Token is invalid or expired"
  }
  ```

---

### 4. Refresh Access Token

Obtains a new access token using a valid refresh token.

- **Endpoint:** `POST /auth/token/refresh/`
- **Authentication:** None

#### Request Body

```json
{
  "refresh": "<your_refresh_token>"
}
```

#### Responses

- **`200 OK`**
  A new access token is returned. The refresh token remains valid until it expires.

  ```json
  {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```

- **`401 Unauthorized`**
  The refresh token is invalid or expired.

  ```json
  {
    "detail": "Token is invalid or expired",
    "code": "token_not_valid"
  }
  ```

---

### 5. Google OAuth2 Authentication

Authenticates a user via a Google-provided access token.

- **Endpoint:** `POST /auth/google/`
- **Authentication:** None

#### Request Body

```json
{
  "access_token": "<google_id_token>"
}
```

#### Responses

- **`200 OK`**
  Successful authentication. Returns JWT tokens for your API.

  ```json
  {
    "access": "...",
    "refresh": "...",
    "user": { ... }
  }
  ```

- **`400 Bad Request`**
  The Google access token is invalid or expired.

  ```json
  {
    "error": "invalid_grant",
    "error_description": "Bad Request"
  }
  ```

---

### 6. Request Password Reset

Initiates the password reset process by sending an email to the user.

- **Endpoint:** `POST /auth/password/reset/`
- **Authentication:** None

#### Request Body

```json
{
  "email": "jane.doe@example.com"
}
```

#### Responses

- **`200 OK`**
  Indicates that the request was processed. An email will be sent if the user exists.

  ```json
  {
    "detail": "Password reset e-mail has been sent."
  }
  ```

---

### 7. Confirm Password Reset (Two-Step Flow)

This is a two-step process initiated by the user clicking the link in the password reset email.

**Step 1: User Clicks Reset Link (Browser `GET` Request)**

The user's browser makes a `GET` request to a unique URL sent to their email. The backend validates the request and redirects to the frontend.

- **Endpoint:** `GET /auth/password/reset/confirm/<uid>/<token>/`
- **Authentication:** None

##### Response

- **`302 Found`**
  The API validates the `uid` and `token`. If they are valid, it redirects the user's browser to the frontend application. The frontend URL is configured on the backend. The `uid` and `token` are passed along in the redirect URL.

  **Example Redirect Location Header:**
  `http://localhost:3000/auth/password/reset/confirm/<uid>/<token>/`

---

**Step 2: Frontend Submits New Password (API `POST` Request)**

After being redirected, the user sees a form on the frontend to enter a new password. The frontend then submits this form's data to the API.

- **Endpoint:** `POST /auth/password/reset/confirm/`
- **Authentication:** None

##### Request Body

```json
{
  "uid": "<the_uidb64_from_the_redirected_url>",
  "token": "<the_token_from_the_redirected_url>",
  "new_password1": "a-new-strong-password",
  "new_password2": "a-new-strong-password"
}
```

##### Responses

- **`200 OK`**
  The password has been successfully reset.

  ```json
  {
    "detail": "Password has been reset with the new password."
  }
  ```

- **`400 Bad Request`**
  The token is invalid, expired, or the passwords do not match.

  ```json
  {
    "token": [
      "Invalid token for given user."
    ]
  }
  ```

---

### 8. Resend Verification Email

Resends the email verification link to the user.

- **Endpoint:** `POST /auth/registration/resend-email/`
- **Authentication:** None

#### Request Body

```json
{
  "email": "user@example.com"
}
```

#### Responses

- **`200 OK`**
  ```json
  {
    "detail": "ok"
  }
  ```

---

### 9. Verify Email (Two-Step Flow)

This is a two-step process, similar to password reset, initiated by the user clicking the link in the verification email.

**Step 1: User Clicks Verification Link (Browser `GET` Request)**

The user's browser makes a `GET` request to a unique URL sent to their email. The backend validates the request and redirects to the frontend.

- **Endpoint:** `GET /auth/registration/verify-email/<key>/`
- **Authentication:** None

##### Response

- **`302 Found`**
  The API validates the `key`. If valid, it redirects the user's browser to the frontend application. The frontend URL is configured on the backend. The `key` is passed along in the redirect URL.

  **Example Redirect Location Header:**
  `http://localhost:3000/auth/email/confirm/<key>/`

---

**Step 2: Frontend Confirms Verification (API `POST` Request)**

After being redirected, the frontend application can make a `POST` request to finalize the verification.

- **Endpoint:** `POST /auth/registration/verify-email/`
- **Authentication:** None

##### Request Body

```json
{
  "key": "<the_key_from_the_redirected_url>"
}
```

##### Responses

- **`200 OK`**
  The email has been successfully verified.

  ```json
  {
    "detail": "ok"
  }
  ```

- **`400 Bad Request`**
  The key is invalid or expired.

  ```json
  {
    "detail": "Error. Invalid key."
  }
  ```

---


---

## Journal Endpoints

These endpoints are used for managing journal entries. All require authentication.

### 10. List or Create Journal Entries

Retrieves a list of journal entries for the authenticated user or creates a new entry.

- **Endpoint:** `GET /journal/entries/` or `POST /journal/entries/`
- **Authentication:** Required

#### GET Request

##### Query Parameters

*   None

##### Responses

- **`200 OK`**

  ```json
  {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "c4a3d2b1-1234-5678-90ab-cdef12345678",
            "content": "Today I'm grateful for good coffee.",
            "photo": null,
            "public": false,
            "created_at": "2023-10-27T10:00:00Z"
        }
    ]
  }
  ```

#### POST Request

Creates a new journal entry.

##### Request Body

- **Body** (`form-data`):
  - `content` (text): "Feeling grateful for a productive day!"
  - `public` (boolean): `true`
  - `photo` (file): (optional) select an image file to upload.

##### Responses

- **`201 Created`**

  ```json
  {
    "id": "a1b2c3d4-...",
    "content": "Feeling grateful for a productive day!",
    "user": { ... },
    "photo": "/media/journal_photos/image.jpg",
    "public": true,
    "created_at": "...",
    "updated_at": "..."
  }
  ```

- **`400 Bad Request`**
  Occurs when the request body is invalid.

---

### 11. Retrieve, Update, or Delete a Specific Journal Entry

Allows you to retrieve, update, or delete a specific journal entry.

- **Endpoint:** `GET /journal/entries/<entry_id>/`, `PATCH /journal/entries/<entry_id>/`, or `DELETE /journal/entries/<entry_id>/`
- **Authentication:** Required

#### GET Request

##### Responses

- **`200 OK`**

  ```json
  {
    "id": "a1b2c3d4-...",
    "content": "Feeling grateful for a productive day!",
    "user": { ... },
    "photo": "/media/journal_photos/image.jpg",
    "public": true,
    "created_at": "...",
    "updated_at": "..."
  }
  ```

- **`404 Not Found`**
  Occurs when the journal entry is not found.

#### PATCH Request

##### Request Body

- **Body** (`form-data`):
  - `content` (text): "Today, I am really grateful for..."
  - `public` (boolean): `false`

##### Responses

- **`200 OK`**

  ```json
  {
    "id": "a1b2c3d4-...",
    "content": "Today, I am really grateful for..."
    "user": { ... },
    "photo": "/media/journal_photos/image.jpg",
    "public": false,
    "created_at": "...",
    "updated_at": "..."
  }
  ```

- **`400 Bad Request`**
  Occurs when the request body is invalid.

- **`404 Not Found`**
  Occurs when the journal entry is not found.

#### DELETE Request

##### Responses

- **`204 No Content`**
  Occurs when the journal entry is successfully deleted.

- **`404 Not Found`**
  Occurs when the journal entry is not found.

---

### 12. Get Journal Analytics

Retrieves analytics data for the authenticated user's journal entries.

- **Endpoint:** `GET /journal/analytics/`
- **Authentication:** Required

#### Responses

- **`200 OK`**

  ```json
  {
    "total_entries": 25,
    "entries_this_month": 10,
    "current_streak": 5,
    "entries_today": 1
  }
  ```

---

### 13. Get Journal Calendar

Retrieves a calendar view of the authenticated user's journal entries for a given month and year.

- **Endpoint:** `GET /journal/calendar/?month=1&year=2024`
- **Authentication:** Required

#### Query Parameters

*   `month` (integer): The month to retrieve entries for.
*   `year` (integer): The year to retrieve entries for.

#### Responses

- **`200 OK`**

  ```json
  {
    "year": 2024,
    "month": 1,
    "entries": {
        "2023-10-01": 1,
        "2023-10-03": 2,
        "2023-10-15": 1
    }
  }
  ```

---

## Community Endpoints

Endpoints for community features. All require authentication.

### 14. Get Community Feed

Retrieves a randomized feed of public journal entries from the community.

- **Endpoint:** `GET /community/feed/`
- **Authentication:** Required

#### Query Parameters

*   `period` (string, optional):  `today` or `week`.
*   `refresh` (boolean, optional): `true` to refresh the feed.

#### Responses

- **`200 OK`**

  ```json
  {
    "count": 50,
    "next": "{ BASE URL }/api/v1/community/feed/?page=2",
    "previous": null,
    "results": [
        {
            "id": "...",
            "content": "So thankful for my friends and family.",
            "photo": null,
            "public": true,
            "created_at": "..."
        },
        {
            "id": "...",
            "content": "The sunset was beautiful today.",
            "photo": "/media/journal_photos/sunset.jpg",
            "public": true,
            "created_at": "..."
        }
    ]
  }
  ```

---

## User Endpoints

Endpoints for user-specific data. All require authentication.

### 15. Get Dashboard Data

Retrieves dashboard data including recent entries and stats for the authenticated user.

- **Endpoint:** `GET /dashboard/`
- **Authentication:** Required

#### Responses

- **`200 OK`**

  ```json
  {
    "name": "New",
    "email": "new.user@example.com",
    "total_entries": 1,
    "recent_entries": [
        {
            "id": 3,
            "content": "Thankful for sunshine!",
            "photo": "media/journal_photos/sunshine.jpg",
            "public": true,
            "created_at": "2025-07-25T06:59:35.203666+01:00"
        }
    ]
  }
  ```

---

### 16. Get or Update Account Information

Retrieves or updates the authenticated user's account information.

- **Endpoint:** `GET /account-management/` or `PATCH /account-management/`
- **Authentication:** Required

#### GET Request

##### Responses

- **`200 OK`**

  ```json
  {
    "profile": {
        "id": "43067c8a-b507-4895-a59d-33ca1ff390fc",
        "email": "new.user@example.com",
        "first_name": "New",
        "phone": "",
        "date_of_birth": null,
        "date_joined": "2025-07-24T12:33:31.519211+01:00"
    }
  }
  ```

#### PATCH Request

##### Request Body

```json
{
  "first_name": "Janet"
}
```

##### Responses

- **`200 OK`**

  ```json
  {
    "message": "Account updated successfully",
    "profile": {
        "id": "43067c8a-b507-4895-a59d-33ca1ff390fc",
        "email": "new.user@example.com",
        "first_name": "Janet",
        "phone": "",
        "date_of_birth": null,
        "date_joined": "2025-07-24T12:33:31.519211+01:00"
    }
  }
  ```

- **`400 Bad Request`**
  Occurs when the request body is invalid.

---

---

## Rate Limiting

To protect the API from brute-force attacks, rate limiting is applied to certain endpoints, particularly those related to authentication.

-   **Login Attempts**: The `/auth/login/` endpoint is rate-limited. If a user makes too many login attempts in a short period from the same IP address, they will receive a `429 Too Many Requests` response. The current limit is 5 attempts per minute.

Please handle this response gracefully in your client by informing the user and preventing further requests for a short duration.

---

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of a request. In case of an error, the response body will typically contain a JSON object with details about the error.

### Common Error Response Formats

For validation errors (`400 Bad Request`), the response will detail which fields are invalid.

```json
{
  "field_name": [
    "A list of errors specific to this field."
  ]
}
```

For other errors, a `detail` key is often provided.

```json
{
  "detail": "A human-readable error message."
}
```

### Common HTTP Status Codes

-   **`200 OK`**: The request was successful (for GET, PATCH).
-   **`201 Created`**: The resource was successfully created (for POST).
-   **`204 No Content`**: The request was successful, and there is no content to return (e.g., for a DELETE request).
-   **`400 Bad Request`**: The server could not process the request due to invalid syntax or missing parameters. The response body will contain details about the validation errors.
-   **`401 Unauthorized`**: The request requires user authentication, but the `Authorization` header is missing or contains an invalid token.
-   **`403 Forbidden`**: The authenticated user does not have the necessary permissions to perform the action (e.g., trying to modify another user's journal entry).
-   **`404 Not Found`**: The requested resource could not be found.
-   **`429 Too Many Requests`**: The user has sent too many requests in a given amount of time ("rate limiting").
-   **`500 Internal Server Error`**: An unexpected error occurred on the server.
---

## Versioning

The API is currently at version `v1`. All endpoints are prefixed with `/api/v1/`.

-   **Backwards Compatibility**: We strive to make only backwards-compatible changes, such as adding new endpoints or new optional properties to existing responses.
-   **Breaking Changes**: Any backwards-incompatible changes will result in a new API version (e.g., `/api/v2/`).
-   **Deprecation**: Deprecated endpoints will be supported for at least 6 months after a new version is released.

---

## Interactive Documentation

You can explore the API interactively using the built-in documentation interfaces when the server is running:

-   **Swagger UI**: `/swagger/`
-   **ReDoc**: `/redoc/`

For example, on a local development server, you would visit `http://127.0.0.1:8000/swagger/`.

---

## Support

For technical support, questions, or feedback:

-   **Email:** `olujay.dev@gmail.com`
-   **Discord:** `@olujay`

We aim to respond to support requests within 48 hours.

---

## Changelog

### Version 1.0.0 (Current)

-   Initial public release of the API.
-   Core features for user management, journaling, and community interaction.

---

_Last Updated: July 2025_