"""Library Management System API

A comprehensive RESTful API for managing library operations.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
import enum

# Database Configuration
# NEW CODE - PASTE THIS:
DATABASE_URL = "sqlite:///./library.db"
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class BookStatus(str, enum.Enum):
    available = "available"
    borrowed = "borrowed"
    reserved = "reserved"
    maintenance = "maintenance"

class MemberStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"

class TransactionStatus(str, enum.Enum):
    active = "active"
    returned = "returned"
    overdue = "overdue"

# Database Models
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    isbn = Column(String, unique=True)
    title = Column(String)
    author = Column(String)
    category = Column(String)
    status = Column(SQLEnum(BookStatus), default=BookStatus.available)
    total_copies = Column(Integer)
    available_copies = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    membership_number = Column(String, unique=True)
    status = Column(SQLEnum(MemberStatus), default=MemberStatus.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    member_id = Column(Integer, ForeignKey("members.id"))
    borrowed_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    returned_at = Column(DateTime, nullable=True)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Fine(Base):
    __tablename__ = "fines"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    amount = Column(Float)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Schemas
class BookBase(BaseModel):
    isbn: str
    title: str
    author: str
    category: str
    total_copies: int

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    status: BookStatus
    available_copies: int
    class Config:
        from_attributes = True

class MemberBase(BaseModel):
    name: str
    email: str

class MemberCreate(MemberBase):
    pass

class MemberResponse(MemberBase):
    id: int
    membership_number: str
    status: MemberStatus
    class Config:
        from_attributes = True

class BorrowRequest(BaseModel):
    book_id: int
    member_id: int

class TransactionResponse(BaseModel):
    id: int
    book_id: int
    member_id: int
    borrowed_at: datetime
    due_date: datetime
    returned_at: Optional[datetime]
    status: TransactionStatus
    class Config:
        from_attributes = True

class FineResponse(BaseModel):
    id: int
    member_id: int
    transaction_id: int
    amount: float
    paid_at: Optional[datetime]
    class Config:
        from_attributes = True

# FastAPI App
app = FastAPI(title="Library Management API", version="1.0.0")

# Create database tables on startup
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Book Endpoints
@app.post("/books", response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        category=book.category,
        total_copies=book.total_copies,
        available_copies=book.total_copies
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books", response_model=List[BookResponse])
def get_all_books(db: Session = Depends(get_db)):
    return db.query(Book).all()

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.get("/books/available", response_model=List[BookResponse])
def get_available_books(db: Session = Depends(get_db)):
    return db.query(Book).filter(Book.status == BookStatus.available).all()

# Member Endpoints
@app.post("/members", response_model=MemberResponse)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    import uuid
    db_member = Member(
        name=member.name,
        email=member.email,
        membership_number=str(uuid.uuid4())
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@app.get("/members", response_model=List[MemberResponse])
def get_all_members(db: Session = Depends(get_db)):
    return db.query(Member).all()

@app.get("/members/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member

# Transaction Endpoints
@app.post("/transactions/borrow", response_model=TransactionResponse)
def borrow_book(request: BorrowRequest, db: Session = Depends(get_db)):
    # Business logic validations
    member = db.query(Member).filter(Member.id == request.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    book = db.query(Book).filter(Book.id == request.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book.status != BookStatus.available or book.available_copies == 0:
        raise HTTPException(status_code=409, detail="Book not available")
    
    # Check borrowing limit
    active_borrows = db.query(Transaction).filter(
        Transaction.member_id == request.member_id,
        Transaction.status == TransactionStatus.active
    ).count()
    
    if active_borrows >= 3:
        raise HTTPException(status_code=409, detail="Maximum borrowing limit reached")
    
    # Check unpaid fines
    unpaid_fines = db.query(Fine).filter(
        Fine.member_id == request.member_id,
        Fine.paid_at == None
    ).count()
    
    if unpaid_fines > 0:
        raise HTTPException(status_code=409, detail="Member has unpaid fines")
    
    # Create transaction
    due_date = datetime.utcnow() + timedelta(days=14)
    transaction = Transaction(
        book_id=request.book_id,
        member_id=request.member_id,
        due_date=due_date
    )
    
    book.available_copies -= 1
    if book.available_copies == 0:
        book.status = BookStatus.borrowed
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@app.post("/transactions/{transaction_id}/return", response_model=TransactionResponse)
def return_book(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    book = db.query(Book).filter(Book.id == transaction.book_id).first()
    
    transaction.returned_at = datetime.utcnow()
    transaction.status = TransactionStatus.returned
    
    book.available_copies += 1
    if book.available_copies > 0:
        book.status = BookStatus.available
    
    # Calculate fine if overdue
    if transaction.returned_at > transaction.due_date:
        days_overdue = (transaction.returned_at - transaction.due_date).days
        fine_amount = days_overdue * 0.50
        fine = Fine(
            member_id=transaction.member_id,
            transaction_id=transaction.id,
            amount=fine_amount
        )
        db.add(fine)
    
    db.commit()
    db.refresh(transaction)
    return transaction

@app.get("/transactions/overdue", response_model=List[TransactionResponse])
def get_overdue_transactions(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    return db.query(Transaction).filter(
        Transaction.status == TransactionStatus.active,
        Transaction.due_date < now
    ).all()


# Update Book
@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db_book.isbn = book.isbn
    db_book.title = book.title
    db_book.author = book.author
    db_book.category = book.category
    db_book.total_copies = book.total_copies
    db_book.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_book)
    return db_book

# Delete Book
@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully"}

# Update Member
@app.put("/members/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, member: MemberCreate, db: Session = Depends(get_db)):
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    db_member.name = member.name
    db_member.email = member.email
    db_member.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_member)
    return db_member

# Delete Member
@app.delete("/members/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(db_member)
    db.commit()
    return {"message": "Member deleted successfully"}

# Fine Endpoints
@app.post("/fines/{fine_id}/pay", response_model=FineResponse)
def pay_fine(fine_id: int, db: Session = Depends(get_db)):
    fine = db.query(Fine).filter(Fine.id == fine_id).first()
    if not fine:
        raise HTTPException(status_code=404, detail="Fine not found")
    
    fine.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(fine)
    return fine

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
