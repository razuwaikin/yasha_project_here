# Printing House Information System Architecture Plan

## Overview
This project implements a secure relational database system for a Printing House using Django, Docker, and PostgreSQL. The system manages orders, clients, employees, services, deliveries, reviews, premises, access control, and delivery statuses with role-based permissions.

## Technology Stack
- **Backend Framework**: Django with Django REST Framework
- **Database**: PostgreSQL
- **Containerization**: Docker and Docker Compose
- **Authentication**: Django's built-in auth with custom groups for roles

## Database Schema

### Models and Relationships

#### 1. Contacts (Контакты)
- **Fields**:
  - id: AutoField (Primary Key)
  - full_name: CharField (ФИО)
  - gender: CharField (пол)
  - age: IntegerField (возраст)
  - home_address: TextField (домашний адрес)
- **Relationships**:
  - One-to-Many with Order (client can have multiple orders)

#### 2. Premises (Помещения)
- **Fields**:
  - id: AutoField (Primary Key)
  - area: DecimalField (площадь)
  - machines_count: IntegerField (количество машин)
  - type: CharField (тип)
- **Relationships**:
  - One-to-Many with Employees
  - One-to-Many with Service

#### 3. Employees (Сотрудники)
- **Fields**:
  - id: AutoField (Primary Key, код сотрудника)
  - position: CharField (должность)
  - salary: DecimalField (зарплата)
  - premises: ForeignKey to Premises
- **Relationships**:
  - Many-to-One with Premises
  - One-to-One with Access
  - One-to-Many with Delivery (as courier)

#### 4. Access (Доступ)
- **Fields**:
  - id: AutoField (Primary Key)
  - access_level: CharField (уровень доступа)
  - employee_position: CharField (должность сотрудника)
  - password: CharField (пароль)
  - employee: OneToOneField to Employees
- **Relationships**:
  - One-to-One with Employees

#### 5. Service (Услуга)
- **Fields**:
  - id: AutoField (Primary Key)
  - package: CharField (пакет услуг)
  - material: CharField (материал)
  - premises: ForeignKey to Premises
  - type: CharField (вид)
  - cost: DecimalField (стоимость)
- **Relationships**:
  - Many-to-One with Premises
  - One-to-Many with Order

#### 6. DeliveryStatus (Статусы доставки)
- **Fields**:
  - id: AutoField (Primary Key)
  - status: CharField (статус)
  - count: IntegerField (количество - number of deliveries with this status)
- **Relationships**:
  - One-to-Many with Delivery

#### 7. Order (Заказ на печать)
- **Fields**:
  - id: AutoField (Primary Key, ID заказа)
  - client_name: CharField (ФИО - redundant with Contacts, but kept as per spec)
  - order_date: DateField (дата оформления)
  - print_date: DateField (дата печати)
  - service_package: CharField (пакет услуг - redundant with Service)
  - quantity: IntegerField (количество)
  - amount: DecimalField (сумма)
  - address: TextField (адрес)
  - client: ForeignKey to Contacts
  - service: ForeignKey to Service
  - delivery: OneToOneField to Delivery
  - premises: ForeignKey to Premises
  - review: OneToOneField to Review
- **Relationships**:
  - Many-to-One with Contacts
  - Many-to-One with Service
  - One-to-One with Delivery
  - Many-to-One with Premises
  - One-to-One with Review

#### 8. Delivery (Доставка)
- **Fields**:
  - id: AutoField (Primary Key, ID)
  - packaging_type: CharField (тип упаковки)
  - volume: DecimalField (объём)
  - weight: DecimalField (вес)
  - address: TextField (адрес)
  - order: OneToOneField to Order
  - employee: ForeignKey to Employees (courier)
  - status: ForeignKey to DeliveryStatus
- **Relationships**:
  - One-to-One with Order
  - Many-to-One with Employees
  - Many-to-One with DeliveryStatus

#### 9. Review (Отзывы)
- **Fields**:
  - id: AutoField (Primary Key)
  - review_text: TextField (отзыв клиента)
  - order: OneToOneField to Order
- **Relationships**:
  - One-to-One with Order

## API Endpoints

### Queries Implementation
1. **Average Salary of Employees**
   - Endpoint: `GET /api/employees/average-salary/`
   - Returns: JSON with average salary

2. **Deliveries with Status "Delivered"**
   - Endpoint: `GET /api/deliveries/delivered/`
   - Returns: List of deliveries with status "Delivered"

3. **Orders by Service**
   - Endpoint: `GET /api/orders/by-service/{service_id}/`
   - Returns: List of orders for the specified service

4. **Deliveries Assigned to Courier**
   - Endpoint: `GET /api/deliveries/by-courier/{employee_id}/`
   - Returns: List of deliveries assigned to the courier

5. **Record Reviews**
   - Endpoint: `POST /api/reviews/`
   - Body: order_id, review_text
   - Creates a new review for the order

6. **Completed Orders for Accounting**
   - Endpoint: `GET /api/orders/completed/`
   - Returns: List of orders where delivery status is "Delivered"

## Role-Based Access Control
- **Client**: Can view their own orders, deliveries, and submit reviews
- **Manager**: Can view all orders, deliveries, employees, and manage reviews
- **Courier**: Can view and update deliveries assigned to them
- **Owner**: Full access to all data

## Docker Setup
- **Dockerfile**: For Django application
- **docker-compose.yml**: With Django app, PostgreSQL database, and optional Redis for caching
- **Requirements**: Django, djangorestframework, psycopg2-binary

## Security Measures
- Database constraints enforced via Django models
- Role-based permissions using Django groups
- Authentication required for all endpoints
- Data validation and sanitization
- Logging of user actions

## Deployment
- Use Docker Compose for local development
- Environment variables for database credentials
- Migrations for database schema changes