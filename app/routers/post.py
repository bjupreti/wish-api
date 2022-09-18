from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from ..models.post import Post as PostModel
from ..schemas.post import PostCreate, PostResponse, PostUpdate
from ..database import get_db

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hello world"}

@router.get("/posts", response_model=list[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(PostModel).all()
    return posts


@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_posts(post: PostCreate, db: Session = Depends(get_db)):
    new_post = PostModel(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/posts/{id}", response_model=PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(PostModel).filter_by(id=str(id)).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesn't exist.")
    return post

@router.delete("/posts/{id}")
def delete_post(id: int, db: Session = Depends(get_db)):
    post_query = db.query(PostModel).filter_by(id=str(id))
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesn't exist.")
    else:
        post_query.delete(synchronize_session=False)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/posts/{id}", response_model=PostResponse)
def update_post(id: int, post: PostUpdate, db: Session = Depends(get_db)):
    post_query = db.query(PostModel).filter_by(id=str(id))
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesn't exist.")
    else:
        post_query.update(post.dict(), synchronize_session=False)
        db.commit()
    return post_query.first()
