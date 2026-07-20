"""Application layer: use cases / application services.

Each use case is a small class with an async `execute(...)` method. It depends
on domain ports (injected), not on concrete infrastructure. The API layer
constructs use cases via `app.api.v1.deps` providers.
"""