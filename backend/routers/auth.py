from fastapi import APIRouter, Depends, HTTPException, status
from models import UserCreate, UserLogin, UserResponse
from auth import get_password_hash, verify_password, create_access_token
from database.connection import get_db
import asyncpg

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate, db=Depends(get_db)):
    async with db.acquire() as conn:
        # Check if user exists
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1",
            user_data.email
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        user = await conn.fetchrow(
            """
            INSERT INTO users (email, password_hash, full_name, role)
            VALUES ($1, $2, $3, 'cliente')
            RETURNING id, email, full_name, role, created_at
            """,
            user_data.email, hashed_password, user_data.full_name
        )
        
        # Create token
        token = create_access_token(str(user['id']), user['email'], user['role'])
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": dict(user)
        }

@router.post("/login", response_model=dict)
async def login(credentials: UserLogin, db=Depends(get_db)):
    async with db.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, email, password_hash, full_name, role FROM users WHERE email = $1",
            credentials.email
        )
        
        if not user or not verify_password(credentials.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Update last login
        await conn.execute(
            "UPDATE users SET last_login = NOW() WHERE id = $1",
            user['id']
        )
        
        token = create_access_token(str(user['id']), user['email'], user['role'])
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user['id']),
                "email": user['email'],
                "full_name": user['full_name'],
                "role": user['role']
            }
        }