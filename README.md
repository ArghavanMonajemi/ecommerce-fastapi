# 🛒 E-commerce Backend API

A scalable, async backend API for an e-commerce application, built using **FastAPI**, **Async SQLAlchemy**, and **PostgreSQL**, with full support for JWT-based authentication and real-time cart and stock management.

## 🚀 Features

- ✅ User registration and login
- 🔐 JWT-based OAuth2 authentication
- 📦 Product management
- 🛒 Shopping cart with item tracking
- 📊 Real-time stock updates
- 🔄 Efficient relationship loading with `selectinload`
- 📁 Modular and scalable project structure
- 🐘 PostgreSQL + Docker support
- 📃 Interactive API docs via Swagger and ReDoc

## 🧰 Tech Stack

- FastAPI
- PostgreSQL (via Docker)
- Async SQLAlchemy
- Alembic (migrations)
- Pydantic
- Docker & Docker Compose

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ecommerce-api.git
cd ecommerce-api
```
### 2. Configure Environment Variables
Create a .env file:
```
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/ecommerce
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
### 3. Run with Docker
Ensure Docker is installed, then:
```bash
docker-compose up --build
```
#### ▶️ Running Locally
If you’re running outside Docker:
```bash
uvicorn app.main:app --reload
```
## 📋 API Documentation
Once the server is running, open:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

## 🔐 Authentication
Use the /token endpoint to obtain a JWT. In Swagger UI, click Authorize, and provide:

- username: (user’s email)

- password: (user’s password)

- Leave client_id and client_secret empty unless you’re using OAuth clients

## 📁 Project Structure
```bash
.
├── app/
│   ├── routers/
│   ├── utils/
│   ├── crud.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── main.py
├── alembic/
├── docker-compose.yml
├── .env
├── requirements.txt
└── README.md
```