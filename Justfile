@defalt:
    just -l

lint:
    ruff check ./build.py

fmt:
    ruff format ./build.py