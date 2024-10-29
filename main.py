from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg
import os

app = FastAPI()

DB_URL = os.getenv("DB_URL")

class Product(BaseModel):
    name: str
    price: float
    description: str
    article: str


async def init_db():
    conn = await asyncpg.connect(DB_URL)

    await conn.execute('''CREATE TABLE IF NOT EXISTS products (
        name TEXT,
        price NUMERIC,
        description TEXT,
        article VARCHAR(255)
    )''')
    await conn.execute('''INSERT INTO products (name, price, description, article) VALUES
        ('Google Pixel', 37000, 'Описание Google Pixel', 'GPX123'),
        ('Redmi', 10000, 'Описание Redmi', 'RDM456'),
        ('Samsung Galaxy', 60000, 'Описание Samsung Galaxy', 'SGZ789');
    ''')

    await conn.close()


async def create_product(product: Product):
    conn = await asyncpg.connect(DB_URL)
    await conn.execute('''
        INSERT INTO products (name, price, description, article) 
        VALUES ($1, $2, $3, $4)
    ''', product.name, product.price, product.description, product.article)

    await conn.close()


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/products")
async def get_products() -> list[Product]:
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch('SELECT * FROM products')
    await conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No products found")
    
    return [Product(**p) for p in rows]


@app.post("/products", status_code=201)
async def create_product(product: Product):
    conn = await asyncpg.connect(DB_URL)

    await conn.execute('''
        INSERT INTO products (name, price, description, article) 
        VALUES ($1, $2, $3, $4)
    ''', product.name, product.price, product.description, product.article)

    await conn.close()
