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
- Faster execution
- Pythonic way to code
        """,
        "class": """
## Python Classes

Classes provide a way to bundle data and functionality together.

### Example:
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"Hello, I'm {self.name}"

person = Person("John", 30)
print(person.greet())
```

### Key Concepts:
- `__init__` - Constructor method
- `self` - Reference to instance
- Methods - Functions in class
- Inheritance - Create subclass
        """,
        "function": """
## Python Functions

Functions are reusable blocks of code that perform a specific task.

### Syntax:
```python
def function_name(parameters):
    # function body
    return value
```

### Example:
```python
def greet(name):
    return f"Hello, {name}!"

result = greet("World")
```

### Best Practices:
- Use descriptive names
- Keep functions small
- Add docstrings
- Use type hints
        """,
    }
    
    topic_lower = topic.lower()
    for key, value in docs.items():
        if key in topic_lower:
            return value.strip()
    
    return f"""
## {topic.title()}

This is a general programming concept. 

### Overview:
{topic} is an important concept in programming that helps you write better code.

### Common Use Cases:
- Data processing
- Algorithm implementation
- Application development

### Best Practices:
- Understand the fundamentals
- Practice with examples
- Apply to real-world problems
    """


def analyze_python_code(code):
    """Generate corrected code and 3 improved versions of Python code."""
    error_msg = ""
    corrected_code = code
    improvements = []
    
    try:
        ast.parse(code)
    except SyntaxError as e:
        error_msg = f"SyntaxError: {e.msg}"
        
        # Try to fix common errors
        lines = code.split('\n')
        fixed_lines = []
        for line in lines:
            # Fix missing colon after if/for/while/def/class
            if line.strip() and not line.strip().startswith('#'):
                if (line.strip().endswith('else') or 
                    line.strip().endswith('elif') or 
                    line.strip().endswith('try') or
                    line.strip().endswith('except') or
                    line.strip().endswith('finally') or
                    line.strip().endswith('while') or
                    line.strip().endswith('for') or
                    line.strip().endswith('if') or
                    re.match(r'^\s*def\s+\w+', line) or
                    re.match(r'^\s*class\s+\w+', line)):
                    if not line.strip().endswith(':'):
                        line = line + ':'
            fixed_lines.append(line)
        
        corrected_code = '\n'.join(fixed_lines)
        
        try:
            ast.parse(corrected_code)
            error_msg += " (Fixed!)"
        except SyntaxError as e2:
            corrected_code = "# Unable to auto-fix. Please correct manually."
    
    # Generate 3 improved versions
    v1_code = code
    v1_explanation = "Improved formatting and readability with proper spacing."
    
    v2_code = code
    v2_explanation = "Made more Pythonic with idiomatic patterns."
    
    v3_code = code
    v3_explanation = "Optimized for better performance."
    
    # Apply specific improvements
    if 'for ' in code and 'append' in code:
        v2_code = re.sub(
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\[\]\s*\n\s*for\s+',
            r'\1 = [',
            v2_code
        )
        if 'for' in v2_code and 'append' not in v2_code:
            v2_explanation = "Converted to list comprehension for better performance."
    
    if 'range(len(' in code:
        v3_code = v3_code.replace('range(len(', 'enumerate(')
        v3_explanation = "Replaced range(len()) with enumerate() for better iteration."
    
    if '==' in code:
        v1_code = v1_code.replace('== True', '').replace('== False', ' not ')
        v1_explanation = "Simplified boolean comparisons."
    
    if 'print(' in code:
        v2_code = v2_code.replace('print(', 'logging.info(')
        v2_explanation = "Replaced print with logging for production code."
    
    improvements = [
        {"version": 1, "code": v1_code, "explanation": v1_explanation},
        {"version": 2, "code": v2_code, "explanation": v2_explanation},
        {"version": 3, "code": v3_code, "explanation": v3_explanation}
    ]
    
    return error_msg, corrected_code, improvements


def generate_explanation(query):
    """Generate AI explanation for a query."""
    explanations = {
        "what is python list comprehension": "List comprehension is a concise way to create lists in Python. It consists of brackets containing an expression followed by a for clause, then zero or more for or if clauses.",
        "what is django": "Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. It follows the MTV (Model-Template-View) pattern.",
        "what is rest framework": "Django REST Framework (DRF) is a powerful toolkit for building Web APIs with serialization, authentication, ViewSets, and routers.",
        "what is react": "React is a JavaScript library for building user interfaces with a component-based architecture and virtual DOM.",
        "what is axios": "Axios is a promise-based HTTP client for JavaScript that works in browsers and Node.js.",
        "what is decorator": "A decorator is a function that takes another function as input and extends its behavior without explicitly modifying it.",
        "what is class": "A class is a blueprint for creating objects that bundles data and functionality together.",
        "what is function": "A function is a reusable block of code that performs a specific task.",
    }
    
    query_lower = query.lower()
    for key, value in explanations.items():
        if key in query_lower:
            return value, get_documentation(key)
    
    return f"Here's an explanation about '{query}': This is a general programming concept. Please provide more specific details for a detailed explanation.", get_documentation(query)


class AnalyzeViewSet(viewsets.ViewSet):
    serializer_class = AnalyzeInputSerializer

    def create(self, request):
        serializer = AnalyzeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data["query"]
        
        if contains_python_code(query):
            error_msg, corrected_code, improvements = analyze_python_code(query)
            documentation = get_documentation("python code")
            
            response_data = {
                "type": "code",
                "error": error_msg,
                "corrected_code": corrected_code,
                "improved_versions": improvements,
                "best_version": 2,
                "documentation": documentation
            }
        else:
            explanation, documentation = generate_explanation(query)
            
            response_data = {
                "type": "question",
                "error": "",
                "corrected_code": "",
                "improved_versions": [],
                "best_version": 0,
                "documentation": documentation
            }
        
        output_serializer = AnalyzeOutputSerializer(response_data)
        return Response(output_serializer.data)
