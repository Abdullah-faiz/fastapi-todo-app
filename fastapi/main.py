from typing import Optional, List
import databases, sqlalchemy, datetime, uuid
from fastapi import FastAPI
from pydantic import BaseModel, Field



database_url = 'postgres://postgres:12345678@localhost:5432/todo'
database = databases.Database(database_url)
metadata = sqlalchemy.MetaData()

todos = sqlalchemy.Table(
    "py_todos",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("created_at", sqlalchemy.String),
    sqlalchemy.Column("updated_at", sqlalchemy.String)
)

engine = sqlalchemy.create_engine(
    database_url
)
metadata.create_all(engine)

class TodosList(BaseModel):

    id: str
    title: str
    description: str
    created_at: str
    updated_at: str

class TodosEntry(BaseModel):

    title: str = Field(..., example="title here")
    description: str = Field(..., example="description here")
    created_at: str = Field(..., example="created date here")
    updated_at: str = Field(..., example="updated date here")

class TodosUpdate(BaseModel):

    id: str = Field(..., example="title here")
    title: str = Field(..., example="title here")
    description: str = Field(..., example="description here")
    created_at: str = Field(..., example="created date here")
    updated_at: str = Field(..., example="updated date here")

class TodosDelete(BaseModel):
    id: str = Field(..., example="enter todo id here")

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/todos", response_model=List[TodosList])
async def find_all_todos():
    query = todos.select()
    return await database.fetch_all(query)

@app.post("/todos", response_model=TodosList)
async def create_todo(todo: TodosEntry):
    gID = str(uuid.uuid1())
    gdate = str(datetime.datetime.now())
    query = todos.insert().values(
        id = gID,
        title = todo.title,
        description = todo.description,
        created_at = todo.created_at,
        updated_at = todo.updated_at
    )

    await database.execute(query)
    return {
        "id": gID,
        **todo.dict(),
        "created_at": gdate
    }

@app.get("/todos/{todoId}", response_model=TodosList)
async def find_todo_by_id(todoId: str):
    query = todos.select().where(todos.c.id == todoId)
    return await database.fetch_one(query)

@app.put("/todos", response_model=TodosList)
async def update_todo(todo: TodosUpdate):
    gdate = str(datetime.datetime.now())
    query = todos.update().\
        where (todos.c.id == todo.id).\
            values(
                title = todo.title,
                description = todo.description,
                updated_at = todo.updated_at
            )
    await database.execute(query)
    return await find_todo_by_id(todo.id)

@app.delete("/todos/{todoId}")
async def delete_todo(todo: TodosDelete):
    query = todos.delete().where(todos.c.id == todo.id)
    await database.execute(query
    )
    return {
        "status": True,
        "result": "This todo has been deleted successfully!"
    }