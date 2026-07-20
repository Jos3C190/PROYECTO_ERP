"""Domain port interfaces (abstract repositories / services).

Each port is a `Protocol` or `ABC` declared in the domain layer and implemented
in `app.infrastructure.repositories`. Use cases depend on these ports, never on
concrete SQLAlchemy repositories.
"""