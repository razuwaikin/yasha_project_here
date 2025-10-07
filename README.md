# Printing House Information System

A secure relational database system for managing printing house operations, built with Django, Django REST Framework, and PostgreSQL (or SQLite for development).

## Features

- **Secure Database**: Relational database with proper constraints and validations
- **Role-Based Access Control**: Different permissions for clients, managers, couriers, and owners
- **REST API**: Endpoints for querying orders, deliveries, employees, and more
- **Docker Support**: Containerized deployment

## Database Schema

### Models

1. **Contacts**: Client information linked to Django User
2. **Premises**: Printing facilities
3. **Employees**: Staff linked to Django User
4. **Access**: Employee access levels
5. **Service**: Printing services offered
6. **DeliveryStatus**: Status of deliveries
7. **Order**: Printing orders
8. **Delivery**: Delivery information
9. **Review**: Client reviews

### Relationships

- Order ↔ Contacts (client)
- Order ↔ Service
- Order ↔ Delivery (one-to-one)
- Order ↔ Premises
- Order ↔ Review (one-to-one)
- Employees ↔ Premises
- Employees ↔ Access (one-to-one)
- Delivery ↔ Employees (courier)
- Delivery ↔ DeliveryStatus

## API Endpoints

All endpoints require authentication.

### Employee Queries

- `GET /api/employees/average-salary/` - Average salary (Manager/Owner only)
  - Response: `{"average_salary": 50000.00}`

### Delivery Queries

- `GET /api/deliveries/delivered/` - Delivered deliveries
  - Courier: Own deliveries
  - Manager/Owner: All delivered deliveries

- `GET /api/deliveries/by-courier/{employee_id}/` - Deliveries by courier
  - Courier: Own deliveries
  - Manager/Owner: All deliveries for the employee

### Order Queries

- `GET /api/orders/by-service/{service_id}/` - Orders by service (Manager/Owner only)

- `GET /api/orders/completed/` - Completed orders (Manager/Owner only)

### Review Management

- `POST /api/reviews/` - Create review
  - Client: For own orders
  - Manager/Owner: For any order
  - Body: `{"order": 1, "review_text": "Good service"}`

## Setup and Testing Guide

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

4. Run server:
   ```bash
   python manage.py runserver
   ```

### Docker

1. Build and run:
   ```bash
   docker-compose up --build
   ```

2. add fixtures:
   ```bash
   python manage.py loaddata printing_house_app/fixtures/fixtures.json
   ```

## Manual Testing Guide

### 1. Web Interface Testing
The system now includes a complete web interface for users to interact with.

#### Access the Application
- Go to `http://localhost:8000/`
- You'll be redirected to login if not authenticated

#### Create Test Users and Data
1. Go to `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Create test data:
   - **Users**: Create users and assign to groups (client, manager, courier, owner)
   - **Contacts**: Link to users in 'client' group
   - **Employees**: Link to users in 'manager/courier' group
   - **Premises**: Create printing facilities
   - **Services**: Create printing services
   - **DeliveryStatus**: Create statuses like 'Pending', 'Delivered'
   - **Orders**: Create orders with deliveries

#### Test User Roles
- **Client**: Can view their orders and leave reviews
- **Manager/Owner**: Can view all orders, create orders, see statistics
- **Courier**: Can view their assigned deliveries

### 2. API Testing

#### API Endpoints
All API endpoints are available under `/api/` prefix.

#### Authentication for API
Use Basic Authentication or session authentication.

#### Test Endpoints with curl

1. **Average Salary** (Manager/Owner only):
   ```bash
   curl -H "Authorization: Basic <base64 username:password>" http://localhost:8000/api/employees/average-salary/
   ```

2. **Delivered Deliveries**:
   ```bash
   curl -H "Authorization: Basic <base64 username:password>" http://localhost:8000/api/deliveries/delivered/
   ```

3. **Orders by Service** (Manager/Owner):
   ```bash
   curl -H "Authorization: Basic <base64 username:password>" http://localhost:8000/api/orders/by-service/1/
   ```

4. **Deliveries by Courier**:
   ```bash
   curl -H "Authorization: Basic <base64 username:password>" http://localhost:8000/api/deliveries/by-courier/1/
   ```

5. **Create Review**:
   ```bash
   curl -X POST -H "Authorization: Basic <base64 username:password>" \
        -H "Content-Type: application/json" \
        -d '{"order": 1, "review_text": "Good service"}' \
        http://localhost:8000/api/reviews/
   ```

6. **Completed Orders** (Manager/Owner):
   ```bash
   curl -H "Authorization: Basic <base64 username:password>" http://localhost:8000/api/orders/completed/
   ```

#### Base64 Encoding for Basic Auth
```bash
echo -n "username:password" | base64
```

### 3. Using Postman
- Import the API endpoints
- Set Authorization to Basic Auth
- Test each endpoint with appropriate user roles

### 4. Sample Test Data
Create in admin:
- User: client1 (group: client), Contact linked
- User: manager1 (group: manager), Employee linked
- User: courier1 (group: courier), Employee linked
- Premises, Service, Order with Delivery status "Delivered"

### 6. Expected Results
- Unauthorized requests return 401/403
- Authorized requests return JSON data
- Invalid data returns validation errors

## Authentication

- Uses Django's built-in authentication
- Roles managed via Django groups: 'client', 'manager', 'courier', 'owner'
- Assign users to appropriate groups in admin panel

## Security

- Database constraints enforced
- Role-based permissions
- Input validation
- Authentication required for all API endpoints

## Technologies

- Django 4.2
- Django REST Framework 3.14
- PostgreSQL (production) / SQLite (development)
- Docker