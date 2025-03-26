# User Manager

Manages users on the platform.

## Responsibilities

- Provides an external API to login. Creates the user if it does not exist.
- Provides an external API to retrieve current user's information.
- Provides an internal API to verify JWT and puts user ID in request header on success.

## Authentication

Nginx will forward every request to the user manager for authentication purpose, and then forward it to the destination service.

If the user has not logged in, the request will not be modified.

If the user has logged in, User Manager will add a new header `X-User-Id` to the request, which contains the ID of the requesting user.

In practice, other services do not need to know the JWT secret in order to verify the JWT in the `Authorization` header, but rather only need to check the `X-User-Id` header. If there is no such header, it means the user has not logged in, and each API can decide how to handle this situation. If there is one, it means the user has logged in, and the value of the header is truly the user's ID.

## Events

### UserCreated

A new user has been created.

```json
{
  "id": "aeaedd47-3b68-42a8-86fa-4827deb10217",
  "username": "john",
  "createdAt": "2025-03-26T02:28:07.079Z"
}
```

- `id`: Unique identifier of the user in UUID v4 format.
- `username`: Name of the user.
- `createdAt`: ISO 8601 representation of when the user is created.
