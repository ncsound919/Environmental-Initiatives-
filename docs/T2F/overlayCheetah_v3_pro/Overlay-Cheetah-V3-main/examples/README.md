# Example Prompts for Overlay Cheetah V3

This directory contains example prompts that demonstrate the capabilities of Overlay Cheetah.

## Basic Examples

### prompt_example.txt
A simple example that generates a binary search implementation in Python.

## Usage

```bash
overlay-cheetah generate --input examples/prompt_example.txt --output output.py
```

## Tips for Writing Effective Prompts

1. **Be Specific**: Clearly describe what you want the code to do
2. **Include Details**: Mention specific requirements like error handling, type hints, etc.
3. **Specify Style**: If you have style preferences, mention them in the prompt
4. **Provide Context**: Include information about the broader application if relevant

## More Examples

You can create your own prompts following these templates:

### Web Application
```
Create a Flask web application with user authentication.
Include login, logout, and registration endpoints.
Use SQLAlchemy for database operations.
Add proper error handling and validation.
```

### Data Processing
```
Create a Python script that processes CSV files.
The script should:
- Read data from input.csv
- Filter rows based on a condition
- Calculate statistics (mean, median, std)
- Export results to output.csv
```

### Algorithm Implementation
```
Implement a graph traversal algorithm in Python.
Use breadth-first search (BFS) approach.
Include proper documentation and examples.
Handle edge cases like empty graphs.
```
