from enum import IntEnum

from sqlmodel import Field, SQLModel


class PriorityLevel(IntEnum):
    High = 1
    Medium = 2
    Low = 3


# if changed update the relevant OpenAPI examples below
class TaskBase(SQLModel):
    title: str = Field(description="Title of the task")
    description: str = Field(description="Description of the task")
    priority: PriorityLevel = Field(
        description="Priority level of the task where High=1, Medium=2, Low=3",
    )
    completed: bool = Field(False, description="Status of the task")


class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: int = Field(default=None, primary_key=True, index=True)


class TaskCreate(TaskBase):
    pass


class TaskPublic(TaskBase):
    id: int = Field(description="The generated unique identifier for the task")


# if changed update the relevant OpenAPI examples below
class TaskUpdate(SQLModel):
    title: str | None = Field(default=None, description="Title of the task")
    description: str | None = Field(default=None, description="Description of the task")
    priority: PriorityLevel | None = Field(
        default=None,
        description="Priority level of the task where High=1, Medium=2, Low=3",
    )
    completed: bool | None = Field(default=None, description="Status of the task")


# region OpenAPI Examples

# These examples are used in the OpenAPI documentation to illustrate how to use the API endpoints.
# I found using the examples through pydantics config dict did not allow to name the examples and did not get passed throuhg to swagger UI.
# Instead the examples here are passed into the body param.

TASK_CREATE_OPENAPI_EXAMPLES = {
    "valid": {
        "summary": "Create a valid task that works correctly",
        "description": "This example shows how to create a task with all required fields.",
        "value": {
            "title": "Sample Task",
            "description": "This is a sample task description.",
            "priority": PriorityLevel.Medium,
            "completed": False,
        },
    },
    "invalid": {
        "summary": "Create a task with invalid priority",
        "description": "Invalid data is rejected with an error as priority can only have be 1, 2 or 3 corresponding to High, Medium and.",
        "value": {
            "title": "Incomplete Task",
            "description": "This task has an invalid priority level.",
            "priority": 4,  # Invalid priority level
            "completed": False,
        },
    },
}


TASK_UPDATE_OPENAPI_EXAMPLES = {
    "full": {
        "summary": "Update a task with all fields provided",
        "description": "This example shows how to update a task with all fields.",
        "value": {
            "title": "Updated Task Title",
            "description": "Updated description for the task.",
            "priority": PriorityLevel.Low,
            "completed": True,
        },
    },
    "partial": {
        "summary": "Update a task with only some fields provided as all are optional",
        "description": "This example shows how to update only the title and description of a task.",
        "value": {
            "title": "Updated Task Title",
            "description": "Updated description for the task.",
        },
    },
}

# endregion
