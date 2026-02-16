# API Documentation - Cirujano System

## Base URL

```
Development:  http://localhost:8000
Staging:      https://staging.cirujano.app
Production:   https://cirujano.app
```

## Authentication

All endpoints (except `/auth/login` and `/auth/register`) require a Bearer token:

```bash
Authorization: Bearer <access_token>
```

### Obtain Token

**POST** `/api/auth/login`

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## API Endpoints

### Authentication

#### Register User
**POST** `/api/auth/register`

```json
{
  "email": "newuser@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "phone": "+34912345678"
}
```

#### Refresh Token
**POST** `/api/auth/refresh`

Headers:
```
Authorization: Bearer <refresh_token>
```

#### Logout
**POST** `/api/auth/logout`

### Users

#### Get Current User
**GET** `/api/users/me`

```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "admin",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Update Profile
**PUT** `/api/users/me`

```json
{
  "full_name": "Jane Doe",
  "phone": "+34912345678",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

#### Change Password
**POST** `/api/users/me/change-password`

```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword123!"
}
```

#### List Users (Admin)
**GET** `/api/admin/users?page=1&limit=20&role=technician`

### Repairs

#### List Repairs
**GET** `/api/repairs?status=pending&page=1&limit=50`

Query Parameters:
- `status`: pending, in_progress, completed, cancelled
- `client_id`: Filter by client
- `technician_id`: Filter by technician
- `page`: Page number
- `limit`: Items per page

```json
{
  "total": 150,
  "page": 1,
  "limit": 50,
  "items": [
    {
      "id": "repair-uuid",
      "client_id": "client-uuid",
      "technician_id": "tech-uuid",
      "device": "iPhone 14",
      "issue": "Screen broken",
      "status": "pending",
      "priority": "high",
      "estimated_cost": 150.00,
      "created_at": "2024-01-20T09:00:00Z",
      "updated_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

#### Create Repair
**POST** `/api/repairs`

```json
{
  "client_id": "client-uuid",
  "device": "MacBook Pro",
  "issue": "Keyboard not working",
  "priority": "medium",
  "estimated_cost": 200.00,
  "notes": "Customer notes here"
}
```

#### Get Repair Details
**GET** `/api/repairs/{repair_id}`

#### Update Repair
**PUT** `/api/repairs/{repair_id}`

```json
{
  "status": "in_progress",
  "technician_id": "tech-uuid",
  "notes": "Progress update"
}
```

#### Complete Repair
**POST** `/api/repairs/{repair_id}/complete`

```json
{
  "final_cost": 150.00,
  "notes": "Repair completed successfully",
  "parts_replaced": ["Screen", "Connector"]
}
```

#### Cancel Repair
**POST** `/api/repairs/{repair_id}/cancel`

```json
{
  "reason": "Customer requested cancellation"
}
```

### Clients

#### List Clients
**GET** `/api/clients?search=&page=1&limit=50`

#### Create Client
**POST** `/api/clients`

```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "+34912345678",
  "address": "123 Main St",
  "city": "Madrid",
  "postal_code": "28001",
  "country": "Spain"
}
```

#### Get Client Details
**GET** `/api/clients/{client_id}`

#### Update Client
**PUT** `/api/clients/{client_id}`

#### Delete Client
**DELETE** `/api/clients/{client_id}`

### Inventory

#### List Items
**GET** `/api/inventory?category=parts&page=1&limit=50`

```json
{
  "total": 500,
  "items": [
    {
      "id": "item-uuid",
      "name": "iPhone 14 Screen",
      "category": "parts",
      "quantity": 25,
      "min_quantity": 5,
      "unit_cost": 150.00,
      "supplier": "TechSupply Co",
      "last_updated": "2024-01-20T09:00:00Z"
    }
  ]
}
```

#### Create Inventory Item
**POST** `/api/inventory`

```json
{
  "name": "Samsung Galaxy S24 Battery",
  "category": "parts",
  "quantity": 50,
  "min_quantity": 10,
  "unit_cost": 45.00,
  "supplier_id": "supplier-uuid"
}
```

#### Update Inventory
**PUT** `/api/inventory/{item_id}`

#### Record Stock Movement
**POST** `/api/inventory/{item_id}/movement`

```json
{
  "type": "out",
  "quantity": 1,
  "reason": "repair_use",
  "repair_id": "repair-uuid",
  "notes": "Used for repair"
}
```

### Appointments

#### List Appointments
**GET** `/api/appointments?date=2024-01-20&technician_id=&page=1`

#### Create Appointment
**POST** `/api/appointments`

```json
{
  "client_id": "client-uuid",
  "technician_id": "tech-uuid",
  "date": "2024-01-22",
  "time": "10:00",
  "type": "diagnosis",
  "notes": "Initial diagnosis needed"
}
```

#### Cancel Appointment
**POST** `/api/appointments/{appointment_id}/cancel`

### Quotes

#### Create Quote
**POST** `/api/quotes`

```json
{
  "repair_id": "repair-uuid",
  "items": [
    {
      "description": "Screen Replacement",
      "quantity": 1,
      "unit_price": 150.00
    },
    {
      "description": "Labor",
      "quantity": 2,
      "unit_price": 30.00
    }
  ],
  "expiration_days": 7,
  "notes": "Valid for 7 days"
}
```

#### Get Quote
**GET** `/api/quotes/{quote_id}`

#### Send Quote to Client
**POST** `/api/quotes/{quote_id}/send`

#### Approve Quote
**POST** `/api/quotes/{quote_id}/approve`

### Logging & Monitoring

#### Send Logs
**POST** `/api/logs`

```json
{
  "level": "ERROR",
  "message": "API call failed",
  "context": {
    "endpoint": "/api/repairs",
    "status": 500
  }
}
```

#### Get Logs
**GET** `/api/logs?level=ERROR&limit=50`

#### Get Statistics
**GET** `/api/logs/stats`

```json
{
  "total_logs": 1500,
  "error_count": 45,
  "critical_count": 2,
  "avg_duration_ms": 125,
  "slow_operations": [
    {
      "name": "database_query",
      "duration": 5000,
      "timestamp": "2024-01-20T10:30:00Z"
    }
  ]
}
```

### Admin

#### System Health
**GET** `/api/admin/health`

```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "uptime": 3600,
  "version": "1.0.0"
}
```

#### Dashboard Stats
**GET** `/api/admin/stats`

```json
{
  "total_clients": 250,
  "active_repairs": 45,
  "completed_repairs": 1200,
  "total_revenue": 45000.00,
  "avg_repair_time": 2.5,
  "technician_utilization": 0.92
}
```

## Error Responses

All error responses follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### Status Codes

- `200` - OK
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Unprocessable Entity
- `429` - Too Many Requests (Rate Limited)
- `500` - Internal Server Error
- `503` - Service Unavailable

### Common Error Codes

- `AUTHENTICATION_FAILED` - Invalid credentials
- `INVALID_TOKEN` - Token expired or invalid
- `PERMISSION_DENIED` - Insufficient permissions
- `RESOURCE_NOT_FOUND` - Resource doesn't exist
- `VALIDATION_ERROR` - Invalid request data
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_SERVER_ERROR` - Server error

## Rate Limiting

All endpoints have rate limiting:

- **Unauthenticated**: 100 requests per hour
- **Authenticated**: 1000 requests per hour
- **Admin**: 5000 requests per hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1705768200
```

## Examples

### Complete a Repair Flow

1. **Create Repair**
   ```bash
   curl -X POST http://localhost:8000/api/repairs \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "client_id": "...",
       "device": "iPhone",
       "issue": "Screen broken",
       "priority": "high"
     }'
   ```

2. **Create Quote**
   ```bash
   curl -X POST http://localhost:8000/api/quotes \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "repair_id": "...",
       "items": [{"description": "Screen", "quantity": 1, "unit_price": 150}]
     }'
   ```

3. **Send Quote**
   ```bash
   curl -X POST http://localhost:8000/api/quotes/{quote_id}/send \
     -H "Authorization: Bearer $TOKEN"
   ```

4. **Update Repair Status**
   ```bash
   curl -X PUT http://localhost:8000/api/repairs/{repair_id} \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"status": "in_progress", "technician_id": "..."}'
   ```

5. **Complete Repair**
   ```bash
   curl -X POST http://localhost:8000/api/repairs/{repair_id}/complete \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "final_cost": 150.00,
       "notes": "Repair completed successfully"
     }'
   ```

## Webhooks

Subscribe to events via webhooks:

**POST** `/api/webhooks/subscribe`

```json
{
  "event": "repair.completed",
  "url": "https://your-server.com/webhook",
  "secret": "webhook-secret-key"
}
```

### Webhook Events

- `repair.created` - New repair created
- `repair.started` - Repair started
- `repair.completed` - Repair completed
- `appointment.scheduled` - New appointment
- `appointment.cancelled` - Appointment cancelled
- `quote.sent` - Quote sent to client
- `quote.approved` - Quote approved

## SDK / Client Libraries

### JavaScript/TypeScript

```bash
npm install cirujano-sdk
```

```typescript
import { CirujanoClient } from 'cirujano-sdk'

const client = new CirujanoClient({
  baseUrl: 'https://api.cirujano.app',
  token: 'your-token'
})

const repairs = await client.repairs.list()
const repair = await client.repairs.create({...})
```

### Python

```bash
pip install cirujano-sdk
```

```python
from cirujano import CirujanoClient

client = CirujanoClient(
    base_url='https://api.cirujano.app',
    token='your-token'
)

repairs = client.repairs.list()
repair = client.repairs.create(...)
```

## Support

For API support:
- Email: api-support@cirujano.app
- Documentation: https://docs.cirujano.app
- Status: https://status.cirujano.app
