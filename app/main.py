from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg
from psycopg.rows import dict_row
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None

while True:
    try:
        conn = psycopg.connect(
        "host=localhost dbname=fastapi user=postgres password=Sahle7##",
        row_factory=dict_row
        )

        cursor = conn.cursor()
        print("Database Connection Successfull!")
        break

    except Exception as err:
        print("Connection to database failed!")
        print("Error: ", err)
        time.sleep(2)

    

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "title of post 2", "content": "content of post 2", "id": 2}]

def find_post_ind(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


@app.get("/")
async def root():
    return {"message": "Hello!"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) 
    #                VALUES (%s, %s, %s)
    #                RETURNING *""", 
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}
    # post_dict = post.model_dump()
    # post_dict['id'] = randrange(0,1000000)
    # my_posts.append(post_dict)
    # return {"data": post_dict}

# @app.get("/posts/latest")
# def get_latest_post():
#     return {"data": my_posts[len(my_posts)-1]}

@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts
    #                WHERE id = %s""", (id,))
    # post = cursor.fetchone()
    # print(id)
    # for post in my_posts:
    #     if post['id'] == id:
    #         return {"data": post}
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id: {id} does not exist!")
    return {"data": post} 
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f"Post with id: {id} does not exist!"}

@app.delete("/posts/{id}",status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts
    #                WHERE id = %s
    #                RETURNING *""",(id,))
    # post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"Post with id: {id} does not exist!")
    
    # post.delete(synchronize_session=False)
    db.delete(post)
    db.commit()
    # ind = find_post_ind(id)
    # my_posts.pop(ind)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, updated_post: Post, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts
    #                 SET title = %s, content = %s, published = %s
    #                 WHERE id = %s
    #                 RETURNING *""", 
    #                 (post.title, post.content, post.published, id))
    # post = cursor.fetchone()
    # conn.commit()
    # ind = find_post_ind(id)
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"Post with id: {id} does not exist!")
    # post_dict = post.model_dump()
    # post_dict['id'] = id
    # my_posts[ind] = post_dict
    post_query.update(updated_post.model_dump(), synchronize_session = False)
    db.commit()
    return{'data': post_query.first()}

