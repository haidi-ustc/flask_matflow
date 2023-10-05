# Matflow Flask Application

This is a Flask-based web application for Matflow. The application integrates with various tools such as Flask-JWT-Extended, Flask-PyMongo, Flask-Bcrypt, and Celery for background processing.

## Prerequisites

- Python 3.9
- MongoDB 5.0.8
- Redis (for Celery) 3.2.12 
- Celery v5.3.4

## Setup & Installation

1. **Clone the repository**

```bash
git clone https://gitee.com/haidi-hfut/flask_matflow/tree/master
cd flask_matflow
```

2. **Set up a virtual environment** (Optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Environment Variables**

    Before running the application, ensure you set necessary environment variables. You can do this using a `.env` file or exporting directly in your terminal.

```env
SECRET_KEY=mysecretkey
JWT_SECRET_KEY=myjwtsecretkey
DEVELOPMENT_MONGO_URI=mongodb://user:password@localhost:27017/matflow
PRODUCTION_MONGO_URI=mongodb://user:password@localhost:27017/proddatabase
```

5. **Running the Application**

```bash
python manage.py
```

    The application should be accessible at `http://0.0.0.0:1234/`

## Using Celery for Background Tasks

The application integrates with Celery for processing background tasks. Ensure you have Redis set up as it's used as the broker.

1. **Starting the Celery Worker**

```bash
cd flask_matflow
celery -A task.celery worker --loglevel=info
```

## Directory Structure

```
matflow-1/
│
├── app.py - Main application file where Flask app is created and blueprints are registered.
├── manage.py - Entrypoint to run the Flask app.
│
├── api/ - Blueprint for API routes.
|   └── views.py - Views related to api.
├── main/ - Blueprint for main routes.
|   └── views.py - Views related to index.html.
└── task/ - Blueprint for tasks and includes Celery configurations.
    ├── celery.py - Configuration for Celery.
    ├── test.py - Sample Celery tasks.
    └── views.py - Views related to tasks.
```

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT License](LICENSE)


