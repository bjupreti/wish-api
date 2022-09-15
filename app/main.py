from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange

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
    rating: str | None = None

@app.get("/")
async def root():
    return {"message": "Hello world"}

@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict["id"] = randrange(0, 100000)
    my_posts.append(post_dict)
    return {"data": post_dict}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post_by_id(id)
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post with id: {id} doesn't exist."}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesn't exist.")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # deleting post
    # find the index in the array that has required ID
    # myposts.pop(index)
    index =  find_index_of_post(id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesn't exist.")

    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_of_post(id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesn't exist.")
    post_dict = post.dict()
    post_dict["id"] = id
    my_posts[index] = post_dict
    return {"data": post_dict}