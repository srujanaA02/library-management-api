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
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

## Project Structure

```
library-management-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── book.py             # Book model
│   │   ├── member.py           # Member model
│   │   ├── transaction.py       # Transaction model
│   │   └── fine.py             # Fine model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── book.py             # Book schemas
│   │   ├── member.py           # Member schemas
│   │   ├── transaction.py       # Transaction schemas
│   │   └── fine.py             # Fine schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── book_service.py      # Book business logic
│   │   ├── member_service.py    # Member business logic
│   │   ├── transaction_service.py # Transaction and borrowing logic
│   │   └── fine_service.py      # Fine calculation logic
│   └── api/
│       ├── __init__.py
│       ├── books.py             # Book endpoints
│       ├── members.py           # Member endpoints
│       ├── transactions.py       # Transaction endpoints
│       └── fines.py             # Fine endpoints
├── requirements.txt
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
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
# Configure your PostgreSQL connection in config.py
python -c "from app.database import init_db; init_db()"
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

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

## Error Handling

The API returns appropriate HTTP status codes and error messages:
- `400 Bad Request` - Invalid input data
- `404 Not Found` - Resource not found
- `409 Conflict` - Business rule violation
- `500 Internal Server Error` - Server error

## Testing

Test the endpoints using Postman or curl:

```bash
# Create a book
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{"isbn": "978-0-123456-78-9", "title": "Sample Book", "author": "John Doe", "category": "Fiction", "total_copies": 5}'

# Create a member
curl -X POST http://localhost:8000/members \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Smith", "email": "jane@example.com"}'

# Borrow a book
curl -X POST http://localhost:8000/transactions/borrow \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1, "member_id": 1}'
```

## Database Schema

### Books Table
- id (PK)
- isbn (UNIQUE)
- title
- author
- category
- status (available, borrowed, reserved, maintenance)
- total_copies
- available_copies
- created_at
- updated_at

### Members Table
- id (PK)
- name
- email
- membership_number (UNIQUE)
- status (active, suspended)
- created_at
- updated_at

### Transactions Table
- id (PK)
- book_id (FK)
- member_id (FK)
- borrowed_at
- due_date
- returned_at (nullable)
- status (active, returned, overdue)
- created_at
- updated_at

### Fines Table
- id (PK)
- member_id (FK)
- transaction_id (FK)
- amount
- paid_at (nullable)
- created_at
- updated_at

## License

MIT
