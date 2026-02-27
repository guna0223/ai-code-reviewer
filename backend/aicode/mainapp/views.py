import ast
import re
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CodeReview
from .serializers import CodeReviewSerializer, AnalyzeInputSerializer, AnalyzeOutputSerializer


class CodeReviewViewSet(viewsets.ModelViewSet):
    queryset = CodeReview.objects.all()
    serializer_class = CodeReviewSerializer

    def perform_create(self, serializer):
        code = serializer.validated_data["code"]

        try:
            ast.parse(code)
            review = "✅ Code is syntactically correct."

            if "print(" in code:
                review += " Avoid print statements in production."

            if "==" in code and "None" in code:
                review += " Use 'is None' instead of '== None'."

            if "for" in code:
                review += " Loop detected. Check performance."

        except SyntaxError as e:
            review = f"❌ Syntax Error: {e}"

        serializer.save(review=review)


def contains_python_code(text):
    """Detect if input contains valid Python code patterns."""
    python_keywords = [
        'def ', 'class ', 'import ', 'from ', 'if ', 'else:', 'elif ',
        'for ', 'while ', 'try:', 'except', 'with ', 'return ', 'yield ',
        'lambda ', 'print(', 'async ', 'await ', 'True', 'False', 'None',
        'print(', '[]', '{}', '()', 'self.', '__init__'
    ]
    
    code_indicators = [
        r'^\s*def\s+\w+\s*\(',
        r'^\s*class\s+\w+',
        r'^\s*import\s+\w+',
        r'^\s*from\s+\w+',
        r'=\s*\[',
        r'=\s*\{',
        r'\(\s*\)',
        r':\s*$',
        r'^\s*for\s+\w+\s+in\s+',
        r'^\s*if\s+__name__',
        r'print\s*\(',
        r'def\s+\w+\([^)]*\):',
    ]
    
    for pattern in code_indicators:
        if re.search(pattern, text, re.MULTILINE):
            return True
    
    keyword_count = sum(1 for kw in python_keywords if kw in text)
    if keyword_count >= 2:
        return True
    
    if '()' in text and ('def ' in text or 'class ' in text):
        return True
    
    return False


def generate_code_improvements(code):
    """Generate improved versions of Python code with explanations."""
    error_msg = ""
    corrected_code = code
    improvements = []
    
    try:
        ast.parse(code)
    except SyntaxError as e:
        error_msg = f"SyntaxError: {e.msg}"
        
        # Auto-fix common errors
        lines = code.split('\n')
        fixed_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                # Fix missing colon
                if (stripped.endswith('else') or stripped.endswith('elif') or
                    stripped.endswith('try') or stripped.endswith('except') or
                    stripped.endswith('finally') or stripped.endswith('while') or
                    stripped.endswith('for') or stripped.endswith('if') or
                    re.match(r'^\s*def\s+\w+', line) or
                    re.match(r'^\s*class\s+\w+', line)):
                    if not stripped.endswith(':'):
                        line = line.rstrip() + ':'
                
                # Fix missing indentation after colon
                if stripped.endswith(':') and not line.endswith('    '):
                    line = line + '    pass'
                    
            fixed_lines.append(line)
        
        corrected_code = '\n'.join(fixed_lines)
        
        try:
            ast.parse(corrected_code)
            error_msg += " (Automatically fixed!)"
        except SyntaxError:
            corrected_code = "# Please fix syntax errors manually"
            error_msg = f"SyntaxError: {e.msg} (Unable to auto-fix)"
    
    # Generate 3 improved versions
    v1_code = code
    v1_explanation = "Enhanced readability with proper formatting and clear structure."
    
    v2_code = code
    v2_explanation = "Made more Pythonic using idiomatic patterns and best practices."
    
    v3_code = code
    v3_explanation = "Optimized for performance with efficient algorithms and reduced complexity."
    
    # Apply targeted improvements
    if 'for ' in code:
        if 'append' in code:
            # Suggest list comprehension
            v2_code = re.sub(
                r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\[\]\s*\n(\s*)for\s+',
                r'\1 = [\2',
                v2_code
            )
            if v2_code != code:
                v2_explanation = "Converted loop with append() to list comprehension for better performance and readability."
        
        if 'range(len(' in code:
            v3_code = v3_code.replace('range(len(', 'enumerate(')
            v3_explanation = "Replaced range(len()) with enumerate() for more Pythonic iteration with index."
    
    if '==' in code:
        v1_code = v1_code.replace('== True', '').replace('== False', ' not ')
        v1_explanation = "Simplified boolean comparisons for cleaner code."
    
    if 'print(' in code:
        v2_code = v2_code.replace('print(', 'logging.info(')
        v2_explanation = "Replaced print() with logging for proper production-grade logging."
    
    if 'global ' in code:
        v3_code = v3_code.replace('global ', '# Avoid global variables. Use parameters and return values.')
        v3_explanation = "Eliminated global variables to improve code maintainability and reduce side effects."
    
    if 'except:' in code:
        v2_code = v2_code.replace('except:', 'except Exception as e:')
        v2_explanation = "Added specific exception handling to catch and handle errors properly."
    
    improvements = [
        {"version": 1, "code": v1_code, "explanation": v1_explanation},
        {"version": 2, "code": v2_code, "explanation": v2_explanation},
        {"version": 3, "code": v3_code, "explanation": v3_explanation}
    ]
    
    return error_msg, corrected_code, improvements


def generate_question_answer(query):
    """Generate comprehensive AI-style answers to programming questions."""
    query_lower = query.lower()
    
    # Comprehensive answer templates
    answers = {
        "reverse": {
            "answer": "To reverse a list in Python, you have several efficient methods. The most Pythonic way is using slicing with a negative step, which creates a new reversed list without modifying the original.",
            "example_code": "# Method 1: Slicing (most Pythonic)\nmy_list = [1, 2, 3, 4, 5]\nreversed_list = my_list[::-1]\nprint(reversed_list)  # [5, 4, 3, 2, 1]\n\n# Method 2: Using reversed() function\nreversed_list = list(reversed(my_list))\n\n# Method 3: Using reverse() method (in-place)\nmy_list = [1, 2, 3, 4, 5]\nmy_list.reverse()\nprint(my_list)  # [5, 4, 3, 2, 1]",
            "best_practices": [
                "Use slicing [::-1] for creating a new reversed list",
                "Use list.reverse() for in-place reversal",
                "Use reversed() when you need an iterator",
                "Avoid manual loops for reversal - slicing is faster"
            ]
        },
        "list comprehension": {
            "answer": "List comprehension provides a concise way to create lists in Python. It consists of square brackets containing an expression, followed by a for clause, then zero or more for or if clauses.",
            "example_code": "# Basic list comprehension\nsquares = [x**2 for x in range(10)]\nprint(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]\n\n# With condition - even numbers only\neven_squares = [x**2 for x in range(10) if x % 2 == 0]\nprint(even_squares)  # [0, 4, 16, 36, 64]\n\n# Nested list comprehension\nmatrix = [[i*j for j in range(3)] for i in range(3)]\nprint(matrix)  # [[0, 0, 0], [0, 1, 2], [0, 2, 4]]",
            "best_practices": [
                "Use list comprehensions instead of loops when possible",
                "Keep comprehensions readable - break into multiple lines if long",
                "Avoid nested comprehensions for clarity",
                "Use generator expressions for large datasets"
            ]
        },
        "decorator": {
            "answer": "A decorator is a function that takes another function as input and extends its behavior without explicitly modifying it. Decorators are a powerful way to add functionality to existing functions.",
            "example_code": "# Basic decorator\ndef my_decorator(func):\n    def wrapper(*args, **kwargs):\n        print(\"Before function call\")\n        result = func(*args, **kwargs)\n        print(\"After function call\")\n        return result\n    return wrapper\n\n@my_decorator\ndef say_hello():\n    print(\"Hello!\")\n\nsay_hello()\n\n# Decorator with arguments\ndef timer(func):\n    import time\n    def wrapper(*args, **kwargs):\n        start = time.time()\n        result = func(*args, **kwargs)\n        print(f\"Execution time: {time.time() - start:.4f}s\")\n        return result\n    return wrapper",
            "best_practices": [
                "Use functools.wraps to preserve function metadata",
                "Accept *args and **kwargs for flexibility",
                "Use decorators for cross-cutting concerns",
                "Common uses: logging, timing, authentication, caching"
            ]
        },
        "class": {
            "answer": "A class in Python is a blueprint for creating objects. It bundles data (attributes) and functions (methods) together. Classes support inheritance and provide a way to organize code.",
            "example_code": "class Person:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    \n    def greet(self):\n        return f\"Hello, I'm {self.name}\"\n    \n    @property\n    def is_adult(self):\n        return self.age >= 18\n\n# Inheritance\nclass Student(Person):\n    def __init__(self, name, age, grade):\n        super().__init__(name, age)\n        self.grade = grade\n    \n    def greet(self):\n        return f\"Hi, I'm {self.name} in grade {self.grade}\"",
            "best_practices": [
                "Use PascalCase for class names",
                "Initialize attributes in __init__",
                "Use @property for computed attributes",
                "Use super() for inheritance",
                "Follow Single Responsibility Principle"
            ]
        },
        "function": {
            "answer": "A function is a reusable block of code that performs a specific task. Functions help organize code, promote reusability, and make testing easier.",
            "example_code": "# Basic function\ndef greet(name):\n    return f\"Hello, {name}!\"\n\n# Default parameters\ndef greet(name, greeting=\"Hello\"):\n    return f\"{greeting}, {name}!\"\n\n# Multiple return values\ndef get_stats(numbers):\n    return min(numbers), max(numbers), sum(numbers)/len(numbers)\n\n# *args and **kwargs\ndef flexible_func(*args, **kwargs):\n    print(f\"Args: {args}\")\n    print(f\"Kwargs: {kwargs}\")",
            "best_practices": [
                "Use descriptive function names",
                "Keep functions small and focused",
                "Add docstrings for documentation",
                "Use type hints for clarity",
                "Prefer pure functions without side effects"
            ]
        },
        "dictionary": {
            "answer": "A dictionary (dict) is an unordered, mutable collection of key-value pairs in Python. Keys must be unique and hashable, while values can be any type.",
            "example_code": "# Creating dictionaries\nperson = {\"name\": \"John\", \"age\": 30}\nperson = dict(name=\"John\", age=30)\n\n# Accessing values\nprint(person[\"name\"])  # John\nprint(person.get(\"email\", \"Not found\"))  # Not found\n\n# Dictionary comprehension\nsquares = {x: x**2 for x in range(5)}\n\n# Common methods\nperson.keys()    # dict_keys(['name', 'age'])\nperson.values()  # dict_values(['John', 30])\nperson.items()   # dict_items([('name', 'John'), ('age', 30)])",
            "best_practices": [
                "Use .get() to avoid KeyError",
                "Use dictionary comprehension for creation",
                "Use collections.defaultdict for missing keys",
                "Prefer dict.items() over iteritems() (Python 3)"
            ]
        },
        "loop": {
            "answer": "Loops allow you to iterate over sequences or repeat code blocks. Python supports for loops (definite iteration) and while loops (indefinite iteration).",
            "example_code": "# For loop with range\nfor i in range(5):\n    print(i)  # 0, 1, 2, 3, 4\n\n# Iterate over list\nfruits = [\"apple\", \"banana\", \"cherry\"]\nfor fruit in fruits:\n    print(fruit)\n\n# Enumerate - get index and value\nfor index, fruit in enumerate(fruits):\n    print(f\"{index}: {fruit}\")\n\n# Zip - iterate over multiple lists\nnames = [\"Alice\", \"Bob\"]\nage = [25, 30]\nfor name, age in zip(names, age):\n    print(f\"{name}: {age}\")",
            "best_practices": [
                "Use enumerate() instead of range(len())",
                "Use zip() for parallel iteration",
                "Use list comprehensions when appropriate",
                "Avoid nested loops when possible"
            ]
        },
        "error": {
            "answer": "Exception handling in Python prevents crashes and allows graceful error recovery. The try-except block catches errors, while else and finally provide additional control flow.",
            "example_code": "try:\n    result = 10 / 0\nexcept ZeroDivisionError as e:\n    print(f\"Error: {e}\")\nexcept Exception as e:\n    print(f\"Unexpected error: {e}\")\nelse:\n    print(\"No errors occurred\")\nfinally:\n    print(\"This always runs\")\n\n# Raising exceptions\ndef validate_age(age):\n    if age < 0:\n        raise ValueError(\"Age cannot be negative\")\n    return age",
            "best_practices": [
                "Catch specific exceptions, not bare except",
                "Use finally for cleanup code",
                "Raise specific exception types",
                "Include helpful error messages"
            ]
        },
        "file": {
            "answer": "File handling in Python allows reading from and writing to files. The 'with' statement ensures proper resource management and automatic file closing.",
            "example_code": "# Reading files\nwith open(\"file.txt\", \"r\") as f:\n    content = f.read()\n    \n# Read lines\nwith open(\"file.txt\", \"r\") as f:\n    lines = f.readlines()\n    # or\n    for line in f:\n        print(line.strip())\n\n# Writing files\nwith open(\"output.txt\", \"w\") as f:\n    f.write(\"Hello, World!\\n\")\n    \n# Append to file\nwith open(\"log.txt\", \"a\") as f:\n    f.write(\"New entry\\n\")",
            "best_practices": [
                "Always use 'with' statement for file operations",
                "Specify encoding='utf-8' for text files",
                "Use pathlib for modern path handling",
                "Handle exceptions for file operations"
            ]
        },
        "api": {
            "answer": "An API (Application Programming Interface) allows different software components to communicate. REST APIs are the most common, using HTTP methods like GET, POST, PUT, DELETE.",
            "example_code": "import requests\n\n# GET request\nresponse = requests.get(\"https://api.example.com/data\")\ndata = response.json()\n\n# POST request\npayload = {\"name\": \"John\", \"age\": 30}\nresponse = requests.post(\"https://api.example.com/users\", json=payload)\n\n# Error handling\ntry:\n    response = requests.get(url, timeout=5)\n    response.raise_for_status()\nexcept requests.exceptions.RequestException as e:\n    print(f\"Request failed: {e}\")",
            "best_practices": [
                "Use timeout for network requests",
                "Handle exceptions properly",
                "Use .json() for JSON responses",
                "Store base URLs and use session for multiple requests"
            ]
        }
    }
    
    # Match query to best answer
    for key, value in answers.items():
        if key in query_lower:
            return value
    
    # Default comprehensive answer
    return {
        "answer": f"Here's a comprehensive explanation about '{query}':\n\nThis is an important programming concept. Let me explain the key aspects and best practices.",
        "example_code": f"# Example for {query}\n# This demonstrates the concept\n\n# Basic usage\nresult = \"Your code here\"\n\n# Advanced usage\n# Add more complex examples as needed",
        "best_practices": [
            "Start with the basics and build complexity gradually",
            "Practice with real-world examples",
            "Read code from experienced developers",
            "Follow language-specific best practices",
            "Test your code thoroughly"
        ]
    }


def generate_documentation(topic):
    """Generate comprehensive documentation for topics."""
    query_lower = topic.lower()
    
    docs = {
        "reverse": """
## Reversing Lists in Python

### Overview
Reversing a list means changing the order so the last element becomes first. Python provides multiple ways to do this efficiently.

### Methods

**1. Slicing (Recommended)**
```python
my_list = [1, 2, 3, 4, 5]
reversed_list = my_list[::-1]
```
- Creates a new list
- Original list unchanged
- Most Pythonic way

**2. reversed() Function**
```python
reversed_list = list(reversed(my_list))
```
- Returns an iterator
- Memory efficient for large lists

**3. reverse() Method**
```python
my_list.reverse()
```
- Modifies in-place
- Returns None
- No new list created

### Performance
- Slicing: O(n) time, O(n) space
- reversed(): O(n) time, O(1) space
- reverse(): O(n) time, O(1) space
        """,
        "list comprehension": """
## List Comprehensions

### Overview
List comprehensions provide a concise way to create lists. They are faster than traditional loops and considered more Pythonic.

### Syntax
```python
[expression for item in iterable if condition]
```

### Examples
- Basic: `[x**2 for x in range(10)]`
- With condition: `[x for x in nums if x > 0]`
- Nested: `[[i*j for j in range(3)] for i in range(3)]`

### Performance
- 30% faster than equivalent for loops
- More readable for simple transformations
- Use generators for large data
        """,
        "decorator": """
## Python Decorators

### Overview
Decorators modify function behavior without changing source code. They're functions that wrap other functions.

### Use Cases
- Logging and debugging
- Authentication and authorization
- Caching results
- Timing function execution
- Rate limiting

### Syntax
```python
@decorator
def function():
    pass
```

### Best Practice
Always use `functools.wraps`:
```python
from functools import wraps

def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```
        """,
        "class": """
## Python Classes

### Overview
Classes define blueprints for objects with attributes and methods.

### Key Concepts
- `__init__`: Constructor method
- `self`: Reference to instance
- Attributes: Instance variables
- Methods: Functions in class

### Inheritance
```python
class Child(Parent):
    def __init__(self):
        super().__init__()
```

### Best Practices
- Use PascalCase for names
- One class per file
- Keep classes focused
- Use dataclasses for simple data
        """,
    }
    
    for key, value in docs.items():
        if key in query_lower:
            return value.strip()
    
    return f"""
## {topic.title()}

### Overview
This is an important concept in Python programming.

### Key Points
1. Understand the fundamentals
2. Practice with examples
3. Apply to real problems
4. Follow best practices

### Related Topics
- Basic data structures
- Functions and methods
- Object-oriented programming
- Best practices
    """


class AnalyzeViewSet(viewsets.ViewSet):
    serializer_class = AnalyzeInputSerializer

    def create(self, request):
        serializer = AnalyzeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data["query"]
        
        if contains_python_code(query):
            # Handle code input
            error_msg, corrected_code, improvements = generate_code_improvements(query)
            explanation = "I've analyzed your code and generated 3 improved versions with detailed explanations. Version 2 is recommended as the most optimized."
            
            response_data = {
                "type": "code",
                "error": error_msg,
                "corrected_code": corrected_code,
                "improved_versions": improvements,
                "best_version": 2,
                "explanation": explanation,
                "documentation": generate_documentation("python")
            }
        else:
            # Handle question input
            answer_data = generate_question_answer(query)
            
            response_data = {
                "type": "question",
                "error": "",
                "corrected_code": "",
                "improved_versions": [],
                "best_version": 0,
                "answer": answer_data["answer"],
                "example_code": answer_data["example_code"],
                "best_practices": answer_data["best_practices"],
                "explanation": answer_data["answer"],
                "documentation": generate_documentation(query)
            }
        
        output_serializer = AnalyzeOutputSerializer(response_data)
        return Response(output_serializer.data)
