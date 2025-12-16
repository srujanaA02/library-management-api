# Library Management System API

A RESTful API for managing library operations, including book borrowing, member management, transactions, and fine calculation.

## Features

- **Book Management**: Full CRUD operations for books
- **Member Management**: Full CRUD operations for library members
- **Borrowing System**: Borrow and return books with automatic due date calculation
- **Fine Calculation**: Automatic fine calculation for overdue books ($0.50 per day)
- **State Management**: Proper state transitions for books and transactions
- **Business Logic Enforcement**: Max 3 simultaneous borrowings, suspension for overdue books

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (default) or PostgreSQL (optional)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

## Project Structure

```
library-management-api/
├── app/
│   ├── __init__.py
│   └── main.py                 # FastAPI application with all models, schemas, and endpoints
├── venv/                        # Virtual environment
├── library.db                   # SQLite database (auto-generated on first run)
├── requirements.txt             # Project dependencies
├── .gitignore
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/srujanaA02/library-management-api.git
cd library-management-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows Git Bash
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python -m uvicorn app.main:app --reload
```

The API will start on `http://localhost:8000`

The SQLite database (`library.db`) will be automatically created when you run the app for the first time.

## API Documentation

Once the app is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Books
- `POST /books` - Create a new book
- `GET /books` - Get all books
- `GET /books/{id}` - Get book by ID
- `PUT /books/{id}` - Update book
- `DELETE /books/{id}` - Delete book
- `GET /books/available` - Get all available books

### Members
- `POST /members` - Create a new member
- `GET /members` - Get all members
- `GET /members/{id}` - Get member by ID
- `PUT /members/{id}` - Update member
- `DELETE /members/{id}` - Delete member
- `GET /members/{id}/borrowed` - Get books borrowed by member

### Transactions
- `POST /transactions/borrow` - Borrow a book
- `POST /transactions/{id}/return` - Return a borrowed book
- `GET /transactions/overdue` - Get all overdue transactions

### Fines
- `POST /fines/{id}/pay` - Mark fine as paid

## Business Rules

1. **Borrowing Limit**: Members can borrow maximum 3 books simultaneously
2. **Loan Period**: Standard loan period is 14 days
3. **Overdue Fine**: $0.50 per day for each overdue book
4. **Unpaid Fines**: Members with unpaid fines cannot borrow new books
5. **Suspension**: Members with 3+ concurrent overdue books are automatically suspended
6. **Book Status**: A book cannot be borrowed if its status is not 'available'

## Database Setup

### SQLite (Recommended for Testing)
No additional setup required! SQLite automatically creates `library.db` when you run the app.

### PostgreSQL (Optional for Production)
If you want to use PostgreSQL instead:

1. Install PostgreSQL
2. Create database and user:
```bash
psql -U postgres
CREATE DATABASE library_db;
CREATE USER library_user WITH PASSWORD 'your_password';
ALTER ROLE library_user SET client_encoding TO 'utf8';
ALTER ROLE library_user SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE library_db TO library_user;
\q
```

3. Update `app/main.py` line 16:
```python
DATABASE_URL = "postgresql://library_user:your_password@localhost:5432/library_db"
```

## Testing with Swagger UI

1. Open http://localhost:8000/docs
2. Try the endpoints:

**Create a Book:**
```json
{
  "isbn": "978-0-123456-78-9",
  "title": "Python Basics",
  "author": "John Doe",
  "category": "Programming",
  "total_copies": 5
}
```

**Create a Member:**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com"
}
```

**Borrow a Book:**
```json
{
  "book_id": 1,
  "member_id": 1
}
```

## Testing Business Rules

1. **Max 3 Books**: Try borrowing 4 books from same member → should get error
2. **Book Availability**: Try borrowing book with 0 copies → should get error
3. **Unpaid Fines**: Create fine, don't pay, try to borrow → should get error
4. **Overdue Calculation**: Return book 5 days late → should create $2.50 fine

## Database Schema

### Books Table
- id (Primary Key)
- isbn (Unique)
- title
- author
- category
- status (available, borrowed, reserved, maintenance)
- total_copies
- available_copies
- created_at, updated_at

### Members Table
- id (Primary Key)
- name
- email (Unique)
- membership_number (Unique)
- status (active, suspended)
- created_at, updated_at

### Transactions Table
- id (Primary Key)
- book_id (Foreign Key → Books)
- member_id (Foreign Key → Members)
- borrowed_at
- due_date
- returned_at (Nullable)
- status (active, returned, overdue)
- created_at, updated_at

### Fines Table
- id (Primary Key)
- member_id (Foreign Key → Members)
- transaction_id (Foreign Key → Transactions)
- amount
- paid_at (Nullable)
- created_at, updated_at

## Error Handling

The API returns appropriate HTTP status codes:
- `400 Bad Request` - Invalid input data
- `404 Not Found` - Resource not found
- `409 Conflict` - Business rule violation
- `500 Internal Server Error` - Server error

## License

MIT
