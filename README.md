# bevy-test

Dependencies are managed with pipenv witch is required for running the app, the app has been developed and tested under Python 3.9:
- [Pipenv](https://pipenv.pypa.io/en/latest/)

When running the app for the first time, set environment variables values on `.env.example` and rename it to `.env`, then run the following commands:
- `pipenv install`
- `pipenv shell` # This will load env vars into the shell
- `python manage.py migrate`
- `python manage.py createsuperuser` # We can use this user for testing

Also, a Twilio and Sendgrid account are required. Get an API key from your SendGrid account. You will need your Twilio account sid and auth token, as well
as a phone number purchased.

For the simplicity of this project, Huey has been used instead of celery with an SQLite dB for scheduling tasks, also the app uses SQLite.
In a production app, we may use Celery, Redis, PostgreSQL, docker for the development environment, and so on.

When running the app we need two shells, one for running the tasks workers and another one for the app.
The API uses Basic Auth so a user must be created first for testing.

- `python manage.py run_huey` for running workers
- `python manage.py runserver` for running the API

## API Endpoints
- GET `/api/notification/`: Return a list of notifcation for the authenticated user.
- POST `/api/notification/`: Creates a new notification
  - title
  - text
  - send_at (optional): If provided notificatoin is scheduled to be sent, otherwise is sent right away.
- GET `/api/notification/preferences`: Return notification preferences for the authenticated user.
- PUT `/api/notification/preferences`: Allows to update notification preferences.
