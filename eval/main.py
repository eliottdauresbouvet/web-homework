from sqlmodel import SQLModel, Field, Relationship

class Enrollment(SQLModel, table = True):
    user_id : int = Field(foreign_key="user.id", primary_key = True)
    group_id : int = Field(foreign_key="group.id", primary_key = True)

class User(SQLModel, table = True):
    id : int | None = Field(default=None, primary_key=True)
    name : str

    groups : list["Group"] = Relationship(back_populates="users", link_model=Enrollment)

class Group(SQLModel, table = True):
    id : int | None = Field(default=None, primary_key=True)
    name : str
    users : list["User"] = Relationship(back_populates="groups", link_model=Enrollment)

class Message(SQLModel, table=True):
    id : int | None = Field(default=None, primary_key=True)
    content : str
    user_id : int = Field(foreign_key="user.id")
    group_id : int = Field(foreign_key="group.id")