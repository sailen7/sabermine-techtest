# sabermine-techtest

A simple task management app with a RESTful API, using SQLModel and FastAPI.

- **Github repository**: <https://github.com/sailen7/sabermine-techtest/>
- **Documentation** <https://sailen7.github.io/sabermine-techtest/>

As stated at the bottom cookiecutter-uv was used to inintate a tamplate empty project. This creates a uv project with a lot of what you would want to configure for a production codebase out the box e.g. pre-commit hooks, mypy, pre-configured ruff, basic dockerfile etc.


## Getting started with your project locally

### Prerequisites

This project uses uv to manage the project and packages if you do not have it installed follow the relevant guide [here](https://docs.astral.sh/uv/getting-started/installation/).

make is also required to run the provided scripts. If it's not available, or if you're on Windows you may need to install it, alternatively you can look into the Makefile and copy and manually enter the relevant commands.


### Set Up Your Development Environment

Then, install the environment and the pre-commit hooks with:

```bash
make install
```
This will install the packages via uv and run the pre-commit hooks (which also run on commit as in given by the name).


### Testing

To test the code with a codecov report run:

```bash
make test
```

### Code quality checks

To run the configured code-quality checks use:

```bash
make check
```
Which runs the mypy and the pre-commit linters e.g. ruff check and format

### Commiting the changes

The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

To enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-uv/features/codecov/).


## Docker deployment

To build and run the Docker image, execute the following commands:

```bash
docker build -t sabermine-techtest .
docker run -p 8000:8000 sabermine-techtest
```
The -p flag maps port 8000 on your host machine to port 8000 inside the container. Once the container is running, you can access the application at `http://localhost:8000` if you're on your local machine. The interactive Swagger documentation will be available at `http://localhost:8000/docs`. If you're running the container on a remote server, replace localhost with the server's IP address (e.g. `http://{IP_ADDRESS}:8000`).

---

## Example API Requests

**Note:** The following examples assume the application is running locally on `http://localhost:8000`. See the generated Swagger docs for more detailed information and example responses (`http://localhost:8000/docs` in this case).

### Create a task

```bash
curl -X POST \
  http://localhost:8000/tasks/ \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "My Task",
    "description": "This is my first task",
    "priority": "high",
    "completed": false
  }'
```

### Read tasks

```bash
curl http://localhost:8000/tasks/?completed=true&priority=1
```

### Read a specific task

```bash
curl http://localhost:8000/tasks/1
```

### Update a task

```bash
curl -X PUT \
  http://localhost:8000/tasks/1 \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "My Updated Task",
    "completed": true
  }'
```

### Delete a task

```bash
curl -X DELETE http://localhost:8000/tasks/1
```

Repository initiated with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).
