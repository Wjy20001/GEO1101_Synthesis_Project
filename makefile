
PYTHON_FILES := code/*.py

# Linting
.PHONY: lint
lint:
	@echo "Running pylint..."
	poetry run flake8 $(PYTHON_FILES)

# Formatting
.PHONY: format
format:
	@echo "Running black..."
	poetry run black $(PYTHON_FILES)

# Sorting imports
.PHONY: sort
sort:
	@echo "Running isort..."
	poetry run isort $(PYTHON_FILES)

.PHONY: check
check:
	sort
	format
	lint

# Running the main script
# .PHONY: run
# run:
# 	@echo "Running main script..."
# 	python code/main.py

# Benchmarking
.PHONY: benchmark
benchmark:
	@echo "Running benchmarks..."
	poetry run pytest --benchmark-only

# Clean up
.PHONY: clean
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -r {} +
