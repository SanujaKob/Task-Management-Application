# Task Management Application

## Configuration

Settings are read from environment variables. Notable options include:

- `REMINDER_INTERVAL_SECONDS`: Interval (in seconds) between reminder checks for
  upcoming tasks. Defaults to `60`.

See `app/core/config.py` for a full list of configurable options.

## Running

Start the development server with an ASGI server such as Uvicorn:

```bash
uvicorn server:app --reload
```

The application instance is exposed as `app` in `server.py`.
