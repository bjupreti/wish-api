from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

my_posts = [
    {"title": "Title 1", "content": "Content 1", "id": 1},
    {"title": "Title 2", "content": "Content 2", "id": 2}
]

def find_post_by_id(id):
    for post in my_posts:
        if post["id"] == id:
            return post

def find_index_of_post(id):
    for index, post in enumerate(my_posts):
        if post["id"] == id:
            return index

class Post(BaseModel):
    title: str
    content: str 
    published: bool = True
    # rating: str | None = None

while True:
    try:
        conn = psycopg2.connect(host="localhost", database="wish", user="postgres", password="postgres", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('Database connection successful!')
        break
    except Exception as error:
        print("Database connection failed!")
        print("Error :", error)
        time.sleep(2)


@app.get("/")
async def root():
    return {"message": "Hello world"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts """)
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts} 


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute(
        """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", 
        (post.title, post.content, post.published)
    )
    new_post = cursor.fetchone()
    # The above is all staged changes. We have to commit it to databases to actually finalize the changes.
    conn.commit()
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id)))
    post = cursor.fetchone()
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post with id: {id} doesn't exist."}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesn't exist.")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    p = cursor.execute("""DELETE FROM posts WHERE id = %s returning * """, (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesn't exist.")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s returning * """, 
        (post.title, post.content, post.published, str(id))
    )
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesn't exist.")
    return {"data": updated_post}