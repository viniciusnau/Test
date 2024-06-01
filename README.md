## Installation
Install the package manager [pip](https://pip.pypa.io/en/stable/)

Install [docker](https://docs.docker.com/) & [docker-compose](https://docs.docker.com/compose/).

Create a [virtualenv](https://virtualenv.pypa.io/en/latest/) and activate it.

```bash
sudo apt install virtualenv && virtualenv work_env && source work_env/bin/activate
```

Install [pre-commit](https://pre-commit.com/).

```bash
pip3 install pre-commit && pre-commit install
```

Create a .env file at the root with the following content. (ask the project manager to fill the fields)

```.env
SECRET_KEY=
DB_NAME=
DB_USER=
DB_PASS=
DB_HOST=
DB_PORT=
DEBUG=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
GOOGLE_OAUTH2_CLIENT_ID=
GOOGLE_OAUTH2_CLIENT_SECRET=
GOOGLE_OAUTH2_PROJECT_ID=
GOOGLE_REDIRECT_URL=
```

Build the server:
```bash
make build
```
Run the server:
```bash
make run
```
Log into the server shell by running:
```bash
make server-shell
```
Create a superuser:
```bash
python3 manage.py createsuperuser
```


## Swagger Documentation
To access documentation, follow these steps:

1. Ensure that the project is running and the API is accessible.
2. Click the button below to access the backend documentation and interact with the available APIs:
[![Documentation](https://img.shields.io/badge/Swagger-Documentation-blue.svg)](http://0.0.0.0:8000/swagger)
3. You will be presented with the Swagger UI, which lists all the available endpoints.
4. Explore the APIs by expanding the endpoints and clicking on them to view details such as request/response parameters, headers, and example payloads.
5. To test an endpoint, click on the "Try it out" button, enter the required input parameters, and click "Execute" to see the response.
6. Feel free to experiment with different inputs and explore the capabilities of the API.


## How To Run Pytest

```bash
make test
```

## How To Lint Project

```bash
make lint
```
