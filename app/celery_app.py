# from celery import Celery

# celery_app = Celery(
#     "ticketing",
#     broker="amqp://guest:guest@localhost:5672//",
#     backend="rpc://",
# )

# celery_app.conf.update(
#     task_serializer="json",
#     accept_content=["json"],
#     result_serializer="json",
#     timezone="UTC",
#     enable_utc=True,
# )


from celery import Celery

# -----------------------------------------------------------------------------
# Create the Celery application instance.
#
# Think of this as the equivalent of:
#
#     app = FastAPI()
#
# for FastAPI applications.
#
# Every task, worker, and producer in your application will use this object.
# It acts as the central configuration and coordination point for Celery.
# -----------------------------------------------------------------------------
celery_app = Celery(

    # Name of the Celery application.
    #
    # This is mainly used for identification in logs, monitoring tools,
    # and debugging.
    #
    # It does NOT have to match your project name, but keeping it meaningful
    # makes debugging easier.
    "ticketing",

    # -------------------------------------------------------------------------
    # Broker URL
    #
    # The broker is responsible for transporting tasks from your FastAPI
    # application (producer) to Celery workers (consumers).
    #
    # In this case we're using RabbitMQ.
    #
    # When you execute:
    #
    #     send_email.delay(...)
    #
    # Celery DOES NOT immediately execute the function.
    #
    # Instead it serializes the task into a message and sends it to RabbitMQ.
    #
    # RabbitMQ stores the task until a worker picks it up.
    #
    # URL Breakdown:
    #
    # amqp://
    #     Protocol used to communicate with RabbitMQ.
    #
    # guest
    #     Username
    #
    # guest
    #     Password
    #
    # localhost
    #     RabbitMQ server address.
    #
    # 5672
    #     Default RabbitMQ port.
    #
    # //
    #     Default virtual host.
    #
    # In production this would usually come from environment variables.
    # -------------------------------------------------------------------------
    broker="amqp://guest:guest@localhost:5672//",

    # -------------------------------------------------------------------------
    # Result Backend
    #
    # Some Celery tasks return values.
    #
    # Example:
    #
    # result = add.delay(5, 10)
    #
    # Later:
    #
    # result.get()
    #
    # Celery needs somewhere to store that return value.
    #
    # The backend is responsible for storing:
    #
    # • Task state
    # • Task return value
    # • Success / Failure status
    #
    # "rpc://" uses RabbitMQ's Remote Procedure Call mechanism.
    #
    # For notification systems you often DON'T care about task return values,
    # so many production systems omit the backend entirely by setting:
    #
    # backend=None
    #
    # or use Redis if task results are actually needed.
    # -------------------------------------------------------------------------
    backend="rpc://",
)

# -----------------------------------------------------------------------------
# Celery Configuration
#
# These settings control how tasks are serialized, transmitted,
# and interpreted by workers.
# -----------------------------------------------------------------------------
celery_app.conf.update(

    # -------------------------------------------------------------------------
    # Task Serializer
    #
    # Before a task is sent over RabbitMQ it must be converted into bytes.
    #
    # Celery supports:
    #
    # • json
    # • pickle
    # • yaml
    # • msgpack
    #
    # JSON is recommended because:
    #
    # ✓ Human readable
    # ✓ Cross-language compatible
    # ✓ Safe
    #
    # Avoid pickle unless absolutely necessary because it can execute arbitrary
    # Python code during deserialization.
    # -------------------------------------------------------------------------
    task_serializer="json",

    # -------------------------------------------------------------------------
    # Accepted Content Types
    #
    # Workers will reject any task serialized in an unsupported format.
    #
    # Restricting this improves security.
    #
    # Here we're saying:
    #
    # "Only execute tasks that are serialized as JSON."
    #
    # This prevents accidentally executing pickle payloads.
    # -------------------------------------------------------------------------
    accept_content=["json"],

    # -------------------------------------------------------------------------
    # Result Serializer
    #
    # If a task returns a value:
    #
    #     return {"status": "success"}
    #
    # Celery also needs to serialize that result before storing it
    # in the result backend.
    #
    # Again JSON is the safest option.
    # -------------------------------------------------------------------------
    result_serializer="json",

    # -------------------------------------------------------------------------
    # Timezone
    #
    # Used for:
    #
    # • Scheduled tasks
    # • Celery Beat
    # • Logging
    # • Retry countdowns
    #
    # UTC is the industry standard because:
    #
    # ✓ No daylight savings issues
    # ✓ Consistent across servers
    # ✓ Easier debugging
    #
    # Convert to the user's local timezone only when displaying times.
    # -------------------------------------------------------------------------
    timezone="UTC",

    # -------------------------------------------------------------------------
    # Enable UTC
    #
    # Ensures Celery internally stores and calculates all timestamps in UTC.
    #
    # Without this, different servers running in different timezones could
    # schedule tasks incorrectly.
    #
    # Best practice:
    #
    # Database -> UTC
    # Celery   -> UTC
    # Logs     -> UTC
    #
    # Convert to local timezone only in the frontend/UI.
    # -------------------------------------------------------------------------
    enable_utc=True,
)

celery_app.conf.imports = (
    "app.modules.mailer.notifications",
)


# celery_app.autodiscover_tasks(
#     [
#         "app.notifications",
#     ]
# )