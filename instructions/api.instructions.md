---
applyTo: "**/api/**,**/routes/**,**/controllers/**,**/handlers/**"
---

# API implementation conventions

Apply these rules whenever editing or creating API endpoint handlers and route definitions.

## Input validation

- Validate all incoming data at the boundary (route handler or middleware) before it
  reaches business logic.
- Validate: presence of required fields, data types, string lengths, numeric ranges,
  and allowed enum values.
- Reject invalid requests immediately with a `400 Bad Request` and a structured error
  response — do not pass unvalidated input deeper.

## Error responses

Return structured JSON errors consistently:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Human-readable description",
    "details": [{ "field": "email", "issue": "must be a valid email address" }]
  }
}
```

- Never expose stack traces, internal file paths, or raw database error messages in
  responses. Log them server-side only.
- Use standard HTTP status codes:
  - `400` — invalid input
  - `401` — unauthenticated
  - `403` — authenticated but not authorised
  - `404` — resource not found
  - `409` — conflict (e.g. duplicate resource)
  - `422` — semantically invalid (passes schema but fails business rules)
  - `429` — rate limit exceeded
  - `500` — unexpected server error (generic message to client, full details in logs)

## Authentication & authorisation

- Verify authentication tokens on every route that returns user data or modifies state.
- Apply authorisation checks after authentication — do not assume authentication implies
  authorisation.
- Do not trust client-supplied identity headers (`X-User-Id`, `X-Role`) without
  verifying them against a session token.

## Rate limiting

- Apply rate limiting to authentication endpoints, password-reset flows, and any
  endpoint that sends external communications (email, SMS).
- Return `429 Too Many Requests` with a `Retry-After` header when limits are exceeded.

## Idempotency

- Make `PUT` and `DELETE` requests idempotent — repeated calls with the same input
  should produce the same result without side effects.
- For expensive or non-idempotent `POST` operations, consider accepting a client-supplied
  idempotency key.

## Security headers

Ensure responses include at minimum:

- `Content-Type: application/json` (not `text/html`) for JSON API responses.
- `X-Content-Type-Options: nosniff`
- `Cache-Control: no-store` for responses containing sensitive user data.
