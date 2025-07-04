from fastapi import FastAPI, Response, status
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "title of post 2", "content": "content of post 2", "id": 2}]
@app.get("/")
async def root():
    return {"message": "Hello!"}

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

@app.post("/posts")
def create_posts(post: Post):
    # print(post.model_dump())
    # print(post.rating)
    post_dict = post.model_dump()
    post_dict['id'] = randrange(0,1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

# @app.get("/posts/latest")
# def get_latest_post():
#     return {"data": my_posts[len(my_posts)-1]}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    print(id)
    for post in my_posts:
        if post['id'] == id:
            return {"data": post}
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'message': f"Post with id: {id} does not exist!"}
