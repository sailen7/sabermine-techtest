import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.database import get_session
from src.main import app
from src.models import PriorityLevel, Task

# region Fixtures


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# endregion

# region create_task tests


def test_create_task(client: TestClient):
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "priority": PriorityLevel.High,
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["priority"] == PriorityLevel.High
    assert not data["completed"]
    assert data["id"] is not None


def test_create_task_incomplete(client: TestClient):
    # No description
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "priority": PriorityLevel.High,
        },
    )
    assert response.status_code == 422


def test_create_task_invalid(client: TestClient):
    # priority has an invalid type
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "priority": "invalid",
        },
    )
    assert response.status_code == 422


# endregion


# region read_tasks tests
def test_read_tasks(session: Session, client: TestClient):
    task_1 = Task(
        title="Task 1",
        description="Description 1",
        priority=PriorityLevel.High,
        completed=False,
    )
    task_2 = Task(
        title="Task 2",
        description="Description 2",
        priority=PriorityLevel.Low,
        completed=True,
    )
    session.add(task_1)
    session.add(task_2)
    session.commit()

    response = client.get("/tasks/")
    data = response.json()

    assert response.status_code == 200

    assert len(data) == 2
    assert data[0]["title"] == task_1.title
    assert data[0]["description"] == task_1.description
    assert data[0]["priority"] == task_1.priority
    assert data[0]["completed"] == task_1.completed
    assert data[0]["id"] == task_1.id
    assert data[1]["title"] == task_2.title
    assert data[1]["description"] == task_2.description
    assert data[1]["priority"] == task_2.priority
    assert data[1]["completed"] == task_2.completed
    assert data[1]["id"] == task_2.id


def test_read_tasks_filter_completed(session: Session, client: TestClient):
    task_1 = Task(
        title="Task 1",
        description="Description 1",
        priority=PriorityLevel.High,
        completed=False,
    )
    task_2 = Task(
        title="Task 2",
        description="Description 2",
        priority=PriorityLevel.Low,
        completed=True,
    )
    session.add(task_1)
    session.add(task_2)
    session.commit()

    response = client.get("/tasks/?completed=true")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["title"] == task_2.title


def test_read_tasks_filter_priority(session: Session, client: TestClient):
    task_1 = Task(
        title="Task 1",
        description="Description 1",
        priority=PriorityLevel.High,
        completed=False,
    )
    task_2 = Task(
        title="Task 2",
        description="Description 2",
        priority=PriorityLevel.Low,
        completed=True,
    )
    session.add(task_1)
    session.add(task_2)
    session.commit()

    response = client.get("/tasks/?priority=3")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["title"] == task_2.title


def test_read_tasks_filter_invalid_priority(client: TestClient):
    response = client.get("/tasks/?priority=invalid")
    assert response.status_code == 422


def test_read_tasks_filter_limit(session: Session, client: TestClient):
    task_1 = Task(
        title="Task 1",
        description="Description 1",
        priority=PriorityLevel.High,
        completed=False,
    )
    task_2 = Task(
        title="Task 2",
        description="Description 2",
        priority=PriorityLevel.Low,
        completed=True,
    )
    session.add(task_1)
    session.add(task_2)
    session.commit()

    response = client.get("/tasks/?limit=1")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1


def test_read_tasks_filter_offset(session: Session, client: TestClient):
    task_1 = Task(
        title="Task 1",
        description="Description 1",
        priority=PriorityLevel.High,
        completed=False,
    )
    task_2 = Task(
        title="Task 2",
        description="Description 2",
        priority=PriorityLevel.Low,
        completed=True,
    )
    session.add(task_1)
    session.add(task_2)
    session.commit()

    response = client.get("/tasks/?offset=1")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["title"] == task_2.title


# endregion


# region read_task tests
def test_read_task(session: Session, client: TestClient):
    task_1 = Task(
        title="Task 1",
        description="Description 1",
        priority=PriorityLevel.High,
        completed=False,
    )
    session.add(task_1)
    session.commit()

    response = client.get(f"/tasks/{task_1.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == task_1.title
    assert data["description"] == task_1.description
    assert data["priority"] == task_1.priority
    assert data["completed"] == task_1.completed
    assert data["id"] == task_1.id


def test_read_task_invalid_id(session: Session, client: TestClient):
    task_1 = Task(
        title="Task 1",
        description="Description 1",
        priority=PriorityLevel.High,
        completed=False,
    )
    session.add(task_1)
    session.commit()

    response = client.get(f"/tasks/{12}")
    assert response.status_code == 404


# endregion


# region update_task tests
def test_update_task(session: Session, client: TestClient):
    task_1 = Task(
        title="Task 1",
        description="Description 1",
        priority=PriorityLevel.High,
        completed=False,
    )
    session.add(task_1)
    session.commit()

    response = client.put(f"/tasks/{task_1.id}", json={"title": "Updated Task"})
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == "Updated Task"
    assert data["description"] == "Description 1"
    assert data["priority"] == PriorityLevel.High
    assert not data["completed"]
    assert data["id"] == task_1.id


def test_update_task_invalid_priority(session: Session, client: TestClient):
    task_1 = Task(
        title="Task 1",
        description="Description 1",
        priority=PriorityLevel.High,
        completed=False,
    )
    session.add(task_1)
    session.commit()

    response = client.put(f"/tasks/{task_1.id}", json={"priority": 5})
    assert response.status_code == 422


def test_update_task_invalid_id(session: Session, client: TestClient):
    task_1 = Task(
        title="Task 1",
        description="Description 1",
        priority=PriorityLevel.High,
        completed=False,
    )
    session.add(task_1)
    session.commit()

    response = client.put(f"/tasks/{12}", json={"title": "Updated Task"})
    assert response.status_code == 404


# endregion


# region delete_task tests
def test_delete_task(session: Session, client: TestClient):
    task_1 = Task(
        title="Task 1",
        description="Description 1",
        priority=PriorityLevel.High,
        completed=False,
    )
    session.add(task_1)
    session.commit()

    response = client.delete(f"/tasks/{task_1.id}")

    task_in_db = session.get(Task, task_1.id)

    assert response.status_code == 200

    assert task_in_db is None


def test_delete_task_invalid_id(session: Session, client: TestClient):
    task_1 = Task(
        title="Task 1",
        description="Description 1",
        priority=PriorityLevel.High,
        completed=False,
    )
    session.add(task_1)
    session.commit()

    response = client.delete(f"/tasks/{12}")
    assert response.status_code == 404


# endregion
