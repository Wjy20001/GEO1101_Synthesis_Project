
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

.PHONY: training
training:
	@echo "Running training..."
	poetry run python code/training.py

.PHONY:image
image:
	@echo "Running image..."
	poetry run python code/image.py

.PHONY: classify
classify:
	@echo "Running classification..."
	poetry run python code/classify.py
