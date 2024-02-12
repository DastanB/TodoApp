from fastapi import FastAPI
from starlette import status
import models
from database import engine
from routers import auth, todos, admin, users

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.get('/health', status_code=status.HTTP_200_OK)
def health_check():
    return {'is_healthy': True}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
