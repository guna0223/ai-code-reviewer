import ast
import os
import re
import json
import sys
import io
import google.generativeai as genai
from rest_framework import viewsets
from rest_framework.response import Response
from .models import CodeReview
from .serializers import CodeReviewSerializer, AnalyzeInputSerializer, AnalyzeOutputSerializer

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def execute_python_code(code):
    """Execute Python code and return the output."""
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()
    
    try:
        # Execute the code
        exec(code, {})
        output = captured_output.getvalue()
        sys.stdout = old_stdout
        
        if output:
            return {"success": True, "output": output.strip()}
        else:
            return {"success": True, "output": "(No output)"}
    except Exception as e:
        sys.stdout = old_stdout
        return {"success": False, "error": str(e)}


class CodeReviewViewSet(viewsets.ModelViewSet):
    queryset = CodeReview.objects.all()
    serializer_class = CodeReviewSerializer

    def perform_create(self, serializer):
        code = serializer.validated_data["code"]
        try:
            ast.parse(code)
            review = "✅ Code is syntactically correct."
        except SyntaxError as e:
            review = f"❌ Syntax Error: {e}"
        serializer.save(review=review)


# ============== INTELLIGENT INPUT DETECTION ==============

def is_greeting(text):
    """Detect if input is a greeting."""
    greetings = ['hi', 'hello', 'hey', 'hai', 'hallo', 'hiya', 'greetings', 'sup', 'yo']
    text_lower = text.lower().strip()
    return text_lower in greetings or len(text_lower) < 4


def is_general_knowledge(text):
    """Detect if input is general knowledge question (not programming)."""
    general_patterns = [
        r'^who (is|was|are|were)\s+',
        r'^what (is|was|are|were)\s+',
        r'^when\s+',
        r'^where\s+',
        r'^why\s+',
        r'^how\s+',
        r'^explain\s+',
        r'^tell me about\s+',
    ]
    text_lower = text.lower().strip()
    
    # Programming-related keywords that should NOT be treated as general knowledge
    programming_keywords = ['python', 'javascript', 'java', 'code', 'function', 'class', 'variable', 
                          'array', 'list', 'string', 'loop', 'syntax', 'programming', 'algorithm',
                          'def ', 'import ', 'const ', 'let ', 'var ', 'function ', '=>', '->']
    
    for keyword in programming_keywords:
        if keyword in text_lower:
            return False
    
    for pattern in general_patterns:
        if re.match(pattern, text_lower):
            return True
    
    return False


def contains_python_code(text):
    """Detect if input contains Python code patterns."""
    # More comprehensive detection
    code_indicators = [
        r'\bdef\s+\w+\s*\(',
        r'\bclass\s+\w+',
        r'\bimport\s+\w+',
        r'\bfrom\s+\w+\s+import',
        r'\bif\s+.*:\s*


def is_code_request(query):
    """Detect if user wants code to be written/generated."""
    code_keywords = [
        'write code', 'create code', 'generate code', 'make code',
        'how to write', 'how to create', 'how to make',
        'write a program', 'create a program', 'build a program',
        'implement', 'function that', 'program that',
        'code for', 'write python', 'create python',
        # New patterns
        'give me', 'show me', 'write a', 'create a',
        'python code', 'java code', 'javascript code',
        'how to', 'can you', 'i need', 'need a',
        'basic', 'simple', 'example',
    ]
    query_lower = query.lower()
    for keyword in code_keywords:
        if keyword in query_lower:
            return True
    return False


def detect_input_type(query):
    """
    Intelligently detect the type of user input.
    Returns: "greeting" | "general" | "programming" | "code" | "code_request"
    """
    query = query.strip()
    
    # 1. Check for greeting
    if is_greeting(query):
        return "greeting"
    
    # 2. Try to parse as Python code
    if contains_python_code(query):
        try:
            ast.parse(query)
            return "code"  # Valid Python code
        except:
            return "code"  # Invalid code, still treat as code
    
    # 3. Check if user wants code to be written
    if is_code_request(query):
        return "code_request"
    
    # 4. Check for general knowledge question
    if is_general_knowledge(query):
        return "general"
    
    # 5. Default to programming question
    return "programming"


# ============== RESPONSE HANDLERS ==============

def handle_greeting():
    """Handle greeting with friendly response."""
    greetings = [
        "Hello! 👋 How can I help you today?",
        "Hi there! 🚀 What can I assist you with?",
        "Hey! 😊 Ready to help with coding or any questions!",
        "Hello! I'm here to help with code, questions, or anything else!",
    ]
    import random
    return {
        "type": "greeting",
        "response": random.choice(greetings),
        "error": None,
        "corrected_code": "",
        "improved_versions": [],
        "documentation": ""
    }


def handle_general_knowledge(query):
    """Handle general knowledge questions with natural response."""
    
    if not GEMINI_API_KEY:
        return {
            "type": "general",
            "response": f"I can help you with that! But for the best answer about '{query}', please ask a specific question.",
            "error": None,
            "corrected_code": "",
            "improved_versions": [],
            "documentation": ""
        }
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""You are a helpful AI assistant. Answer this question naturally and clearly:

{query}

Provide a friendly, informative response. If relevant, you can include a small code example, but don't force it.
JSON format:
{{
  "response": "your answer here"
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = result_text[start:end]
            result = json.loads(json_str)
            return {
                "type": "general",
                "response": result.get("response", ""),
                "error": None,
                "corrected_code": "",
                "improved_versions": [],
                "documentation": f"## {query}\n\n{result.get('response', '')}"
            }
    except Exception as e:
        print(f"Gemini error: {e}")
    
    return {
        "type": "general",
        "response": f"That's an interesting question about '{query}'. I'd be happy to help with coding-related topics!",
        "error": None,
        "corrected_code": "",
        "improved_versions": [],
        "documentation": ""
    }


def handle_programming_question(query):
    """Handle programming questions with explanation and examples."""
    
    if not GEMINI_API_KEY:
        # Better fallback for programming questions
        fallback_responses = {
            "list": "A list in Python is an ordered, mutable collection that can store items of different types.\n\n```python\nfruits = ['apple', 'banana', 'cherry']\nprint(fruits)\n```",
            "dictionary": "A dictionary is a collection of key-value pairs. It's unordered, mutable, and indexed by keys.\n\n```python\nperson = {'name': 'John', 'age': 30}\nprint(person['name'])\n```",
            "function": "A function is a reusable block of code that performs a specific task.\n\n```python\ndef greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('World'))\n```",
            "loop": "A loop repeats code execution for each item in a sequence.\n\n```python\nfor i in range(5):\n    print(i)\n```",
            "class": "A class is a blueprint for creating objects.\n\n```python\nclass Dog:\n    def __init__(self, name):\n        self.name = name\n    def bark(self):\n        return 'Woof!'\n\nmy_dog = Dog('Buddy')\nprint(my_dog.bark())\n```",
            "string": "A string is a sequence of characters used to represent text.\n\n```python\nmessage = 'Hello, World!'\nprint(message.upper())\n```",
            "file": "Working with files in Python:\n\n```python\nwith open('file.txt', 'r') as f:\n    content = f.read()\n```",
        }
        
        query_lower = query.lower()
        for key, response in fallback_responses.items():
            if key in query_lower:
                return {
                    "type": "programming",
                    "response": response,
                    "error": None,
                    "corrected_code": "",
                    "improved_versions": [],
                    "documentation": f"## {query}\n\n{response}"
                }
        
        return {
            "type": "programming",
            "response": f"I'd be happy to help with '{query}'! However, I need a Gemini API key to provide a detailed explanation. Please add your API key to the .env file.",
            "error": None,
            "corrected_code": "",
            "improved_versions": [],
            "documentation": f"## {query}\n\nThis is a programming topic. Add your GEMINI_API_KEY for detailed explanations."
        }
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""You are a programming expert. Answer this question clearly with explanation and examples:

{query}

Provide:
1. Clear explanation
2. Code example (if relevant)
3. Best practices

JSON format:
{{
  "response": "explanation here",
  "example_code": "code example if relevant, empty string if not",
  "best_practices": ["practice 1", "practice 2"]
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = result_text[start:end]
            result = json.loads(json_str)
            
            docs = f"## {query}\n\n{result.get('response', '')}"
            if result.get('example_code'):
                docs += f"\n\n### Example Code\n\n```python\n{result.get('example_code')}\n```"
            if result.get('best_practices'):
                docs += f"\n\n### Best Practices\n" + "\n".join([f"- {p}" for p in result.get('best_practices', [])])
            
            return {
                "type": "programming",
                "response": result.get("response", ""),
                "error": None,
                "corrected_code": result.get("example_code", ""),
                "improved_versions": [],
                "documentation": docs
            }
    except Exception as e:
        print(f"Gemini error: {e}")
    
    return {
        "type": "programming",
        "response": f"Here's what I know about {query}:",
        "error": None,
        "corrected_code": "",
        "improved_versions": [],
        "documentation": f"## {query}"
    }


def generate_code_with_gemini(query):
    """Generate code directly when user asks for code."""
    
    if not GEMINI_API_KEY:
        # Better fallback - generate basic code examples
        query_lower = query.lower()
        
        code_examples = {
            # Common patterns
            "reverse": "def reverse_list(lst):\n    return lst[::-1]\n\n# Example\nprint(reverse_list([1, 2, 3, 4, 5]))",
            "sort": "def sort_list(lst):\n    return sorted(lst)\n\n# Example\nprint(sort_list([5, 2, 8, 1, 9]))",
            "prime": "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\n# Example\nprint(is_prime(17))",
            "fibonacci": "def fibonacci(n):\n    fib = [0, 1]\n    for i in range(2, n):\n        fib.append(fib[i-1] + fib[i-2])\n    return fib[:n]\n\n# Example\nprint(fibonacci(10))",
            "factorial": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)\n\n# Example\nprint(factorial(5))",
            "binary search": "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1\n\n# Example\nprint(binary_search([1, 2, 3, 4, 5], 3))",
            "list": "# Python List Operations\nmy_list = [1, 2, 3, 4, 5]\nmy_list.append(6)\nmy_list.pop()\nprint(my_list)",
            "dictionary": "# Python Dictionary Operations\nmy_dict = {'name': 'John', 'age': 30}\nmy_dict['city'] = 'NYC'\nprint(my_dict.get('name'))",
            "string": "# String Operations\ntext = 'Hello World'\nprint(text.upper())\nprint(text.split())\nprint(text.replace('World', 'Python'))",
            # Basic examples
            "basic": "# Basic Python Examples\n\n# Hello World\nprint('Hello, World!')\n\n# Variables\nname = 'John'\nage = 25\nprint(f'Name: {name}, Age: {age}')\n\n# List\nfruits = ['apple', 'banana', 'cherry']\nfor fruit in fruits:\n    print(fruit)",
            "simple": "# Simple Python Examples\n\n# Sum of numbers\nnumbers = [1, 2, 3, 4, 5]\ntotal = sum(numbers)\nprint(f'Sum: {total}')\n\n# Average\naverage = total / len(numbers)\nprint(f'Average: {average}')",
            "example": "# Python Examples\n\n# For loop\nfor i in range(5):\n    print(i)\n\n# While loop\ncount = 0\nwhile count < 5:\n    print(count)\n    count += 1\n\n# If-else\nx = 10\nif x > 5:\n    print('x is greater than 5')\nelse:\n    print('x is less than or equal to 5')",
        }
        
        for key, code in code_examples.items():
            if key in query_lower:
                return {
                    "answer": f"Here's Python code for {query}:",
                    "example_code": code,
                    "documentation": f"## Generated Code\n\n```python\n{code}\n```"
                }
        
        # Default fallback - basic program
        default_code = """# Python Basic Program\n\n# 1. Hello World\nprint('Hello, World!')\n\n# 2. Variables and Data Types\nname = 'Python'\nversion = 3.11\nis_awesome = True\n\nprint(f'Language: {name}')\nprint(f'Version: {version}')\nprint(f'Is Awesome: {is_awesome}')\n\n# 3. List\nlanguages = ['Python', 'JavaScript', 'Java']\nfor lang in languages:\n    print(f'I love {lang}')}\n\n# 4. Function\ndef greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('Developer'))\n\n# 5. Class\nclass Calculator:\n    def add(self, a, b):\n        return a + b\n    \n    def multiply(self, a, b):\n        return a * b\n\ncalc = Calculator()\nprint(f'5 + 3 = {calc.add(5, 3)}')\nprint(f'4 * 7 = {calc.multiply(4, 7)}')"""
        
        return {
            "answer": f"Here's Python basic code for you:",
            "example_code": default_code,
            "documentation": f"## Basic Python Code\n\n```python\n{default_code}\n```"
        }
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""You are a Python expert. Write clean, working Python code for this request:

Request: {query}

Rules:
- Write complete, working code
- Add brief comments
- Keep it simple and readable
- Return ONLY the code, no explanations

Respond with JSON:
{{
  "code": "the python code here",
  "explanation": "one sentence about what it does"
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = result_text[start:end]
            result = json.loads(json_str)
            return {
                "answer": result.get("explanation", ""),
                "example_code": result.get("code", ""),
                "documentation": f"## Generated Code\n\n```python\n{result.get('code', '')}\n```"
            }
    except Exception as e:
        print(f"Gemini error: {e}")
    
    return {
        "answer": "Here's the code you requested:",
        "example_code": "# Code generation",
        "documentation": "## Code"
    }


def analyze_code_with_gemini(code):
    """Use Gemini API to analyze code and provide improvements."""
    
    # First, try to parse and execute the code
    try:
        ast.parse(code)
        is_valid = True
        error_info = None
    except SyntaxError as e:
        is_valid = False
        error_info = {
            "message": str(e.msg) if hasattr(e, 'msg') else str(e),
            "line": e.lineno if hasattr(e, 'lineno') else None,
            "column": e.offset if hasattr(e, 'offset') else None,
            "text": e.text.strip() if hasattr(e, 'text') and e.text else None
        }
    
    # Execute code and get output
    execution_result = execute_python_code(code)
    code_output = execution_result.get("output", "") if execution_result.get("success") else ""
    
    # If code has errors, try to fix it
    if not is_valid:
        # Try local fix first
        fixed_code = local_fix_syntax(code, error_info)
        if fixed_code:
            # Try to execute fixed code
            fixed_result = execute_python_code(fixed_code)
            if fixed_result.get("success"):
                code = fixed_code
                is_valid = True
                error_info = {"message": "Fixed!", "fixed": True}
                code_output = fixed_result.get("output", "")
    
    if not GEMINI_API_KEY:
        result = local_code_analysis(code, is_valid, error_info)
        result["output"] = code_output
        return result
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Review this Python code:

```
{code}
```

Provide JSON with:
{{
  "is_valid": true/false,
  "error": {{"message": "", "line": null}} or null,
  "corrected_code": "fixed code",
  "improvements": [
    {{"version": 1, "code": "v1", "explanation": ""}},
    {{"version": 2, "code": "v2", "explanation": ""}},
    {{"version": 3, "code": "v3", "explanation": ""}}
  ],
  "best_version": 2
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = result_text[start:end]
            result = json.loads(json_str)
            return result
    except Exception as e:
        print(f"Gemini error: {e}")
    
    return local_code_analysis(code, is_valid, error_info)


def local_code_analysis(code, is_valid, error_info):
    """Fallback local code analysis."""
    corrected_code = code
    improvements = []
    code_output = ""
    
    # Execute original code to get output
    if is_valid:
        result = execute_python_code(code)
        if result.get("success"):
            code_output = result.get("output", "")
    
    if not is_valid and error_info:
        lines = code.split('\n')
        fixed_lines = []
        for i, line in enumerate(lines, 1):
            fixed_line = line
            if error_info.get('line') == i:
                stripped = line.strip()
                if (stripped.endswith('if') or stripped.endswith('else') or
                    stripped.endswith('elif') or stripped.endswith('for') or
                    stripped.endswith('while') or stripped.endswith('def') or
                    stripped.endswith('class') or stripped.endswith('try') or
                    stripped.endswith('except') or stripped.endswith('finally')):
                    if not stripped.endswith(':'):
                        fixed_line = line.rstrip() + ':'
            fixed_lines.append(fixed_line)
        
        corrected_code = '\n'.join(fixed_lines)
        
        try:
            ast.parse(corrected_code)
            error_info["fixed"] = True
            error_info["fix_message"] = "Fixed!"
            # Try to execute fixed code
            result = execute_python_code(corrected_code)
            if result.get("success"):
                code_output = result.get("output", "")
        except:
            error_info["fixed"] = False
            corrected_code = code
    
    if is_valid or (error_info and error_info.get('fixed')):
        improvements = [
            {"version": 1, "code": code, "explanation": "Original code"},
            {"version": 2, "code": code, "explanation": "More Pythonic version"},
            {"version": 3, "code": code, "explanation": "Optimized version"}
        ]
    
    return {
        "is_valid": is_valid,
        "error": error_info,
        "corrected_code": corrected_code,
        "improvements": improvements,
        "best_version": 2,
        "output": code_output
    }


def local_fix_syntax(code, error_info):
    """Try to fix syntax errors locally."""
    if not error_info:
        return None
    
    lines = code.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines, 1):
        fixed_line = line
        if error_info.get('line') == i:
            stripped = line.strip()
            # Add colon if missing
            if (stripped.endswith('if') or stripped.endswith('else') or
                stripped.endswith('elif') or stripped.endswith('for') or
                stripped.endswith('while') or stripped.endswith('def') or
                stripped.endswith('class') or stripped.endswith('try') or
                stripped.endswith('except') or stripped.endswith('finally') or
                stripped.endswith('with')):
                if not stripped.endswith(':'):
                    fixed_line = line.rstrip() + ':'
        fixed_lines.append(fixed_line)
    
    fixed_code = '\n'.join(fixed_lines)
    
    # Verify it works
    try:
        ast.parse(fixed_code)
        return fixed_code
    except:
        return None


# ============== MAIN VIEW SET ==============

class AnalyzeViewSet(viewsets.ViewSet):
    serializer_class = AnalyzeInputSerializer

    def create(self, request):
        serializer = AnalyzeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data["query"]
        
        # Detect input type intelligently
        input_type = detect_input_type(query)
        
        # Handle based on detected type
        if input_type == "greeting":
            result = handle_greeting()
        elif input_type == "general":
            result = handle_general_knowledge(query)
        elif input_type == "code_request":
            code_result = generate_code_with_gemini(query)
            result = {
                "type": "code",
                "is_valid": True,
                "error": None,
                "corrected_code": code_result.get("example_code", ""),
                "improved_versions": [],
                "best_version": 0,
                "response": code_result.get("answer", ""),
                "answer": code_result.get("answer", ""),
                "example_code": code_result.get("example_code", ""),
                "documentation": code_result.get("documentation", ""),
                "output": ""
            }
        elif input_type == "code":
            analysis = analyze_code_with_gemini(query)
            result = {
                "type": "code",
                "is_valid": analysis.get("is_valid", True),
                "error": analysis.get("error"),
                "corrected_code": analysis.get("corrected_code", query),
                "improved_versions": analysis.get("improvements", []),
                "best_version": analysis.get("best_version", 2),
                "response": "",
                "answer": "",
                "example_code": analysis.get("corrected_code", ""),
                "documentation": f"## Code Analysis\n\nStatus: {'✅ Correct' if analysis.get('is_valid') else '❌ Has Errors'}",
                "output": analysis.get("output", "")
            }
        else:  # programming
            result = handle_programming_question(query)
        
        # Build response for API
        response_data = {
            "type": result.get("type", "general"),
            "is_valid": result.get("is_valid", True),
            "error": result.get("error"),
            "corrected_code": result.get("corrected_code", ""),
            "improved_versions": result.get("improved_versions", []),
            "best_version": result.get("best_version", 0),
            "answer": result.get("response", ""),
            "example_code": result.get("example_code", ""),
            "documentation": result.get("documentation", ""),
            "output": result.get("output", "")
        }
        
        output_serializer = AnalyzeOutputSerializer(response_data)
        return Response(output_serializer.data)
,
        r'\bfor\s+\w+\s+in\s+',
        r'\bwhile\s+',
        r'\breturn\s+',
        r'\bprint\s*\(',
        r'\b\w+\s*=\s*\[',
        r'\b\w+\s*=\s*\{',
        r'\b\w+\s*=\s*\(',
        r'\bprint\s*\(',
        r'\blen\s*\(',
        r'\brange\s*\(',
        r'\[.*\].*for\s+',
        r'=.*\[.*\]',
    ]
    
    # Check each pattern
    for pattern in code_indicators:
        if re.search(pattern, text):
            return True
    
    # Also check for common Python syntax elements
    if ':' in text and ('=' in text or 'for' in text or 'if' in text or 'def' in text):
        return True
    
    return False


def is_code_request(query):
    """Detect if user wants code to be written/generated."""
    code_keywords = [
        'write code', 'create code', 'generate code', 'make code',
        'how to write', 'how to create', 'how to make',
        'write a program', 'create a program', 'build a program',
        'implement', 'function that', 'program that',
        'code for', 'write python', 'create python',
        # New patterns
        'give me', 'show me', 'write a', 'create a',
        'python code', 'java code', 'javascript code',
        'how to', 'can you', 'i need', 'need a',
        'basic', 'simple', 'example',
    ]
    query_lower = query.lower()
    for keyword in code_keywords:
        if keyword in query_lower:
            return True
    return False


def detect_input_type(query):
    """
    Intelligently detect the type of user input.
    Returns: "greeting" | "general" | "programming" | "code" | "code_request"
    """
    query = query.strip()
    
    # 1. Check for greeting
    if is_greeting(query):
        return "greeting"
    
    # 2. Try to parse as Python code
    if contains_python_code(query):
        try:
            ast.parse(query)
            return "code"  # Valid Python code
        except:
            return "code"  # Invalid code, still treat as code
    
    # 3. Check if user wants code to be written
    if is_code_request(query):
        return "code_request"
    
    # 4. Check for general knowledge question
    if is_general_knowledge(query):
        return "general"
    
    # 5. Default to programming question
    return "programming"


# ============== RESPONSE HANDLERS ==============

def handle_greeting():
    """Handle greeting with friendly response."""
    greetings = [
        "Hello! 👋 How can I help you today?",
        "Hi there! 🚀 What can I assist you with?",
        "Hey! 😊 Ready to help with coding or any questions!",
        "Hello! I'm here to help with code, questions, or anything else!",
    ]
    import random
    return {
        "type": "greeting",
        "response": random.choice(greetings),
        "error": None,
        "corrected_code": "",
        "improved_versions": [],
        "documentation": ""
    }


def handle_general_knowledge(query):
    """Handle general knowledge questions with natural response."""
    
    if not GEMINI_API_KEY:
        return {
            "type": "general",
            "response": f"I can help you with that! But for the best answer about '{query}', please ask a specific question.",
            "error": None,
            "corrected_code": "",
            "improved_versions": [],
            "documentation": ""
        }
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""You are a helpful AI assistant. Answer this question naturally and clearly:

{query}

Provide a friendly, informative response. If relevant, you can include a small code example, but don't force it.
JSON format:
{{
  "response": "your answer here"
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = result_text[start:end]
            result = json.loads(json_str)
            return {
                "type": "general",
                "response": result.get("response", ""),
                "error": None,
                "corrected_code": "",
                "improved_versions": [],
                "documentation": f"## {query}\n\n{result.get('response', '')}"
            }
    except Exception as e:
        print(f"Gemini error: {e}")
    
    return {
        "type": "general",
        "response": f"That's an interesting question about '{query}'. I'd be happy to help with coding-related topics!",
        "error": None,
        "corrected_code": "",
        "improved_versions": [],
        "documentation": ""
    }


def handle_programming_question(query):
    """Handle programming questions with explanation and examples."""
    
    if not GEMINI_API_KEY:
        # Better fallback for programming questions
        fallback_responses = {
            "list": "A list in Python is an ordered, mutable collection that can store items of different types.\n\n```python\nfruits = ['apple', 'banana', 'cherry']\nprint(fruits)\n```",
            "dictionary": "A dictionary is a collection of key-value pairs. It's unordered, mutable, and indexed by keys.\n\n```python\nperson = {'name': 'John', 'age': 30}\nprint(person['name'])\n```",
            "function": "A function is a reusable block of code that performs a specific task.\n\n```python\ndef greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('World'))\n```",
            "loop": "A loop repeats code execution for each item in a sequence.\n\n```python\nfor i in range(5):\n    print(i)\n```",
            "class": "A class is a blueprint for creating objects.\n\n```python\nclass Dog:\n    def __init__(self, name):\n        self.name = name\n    def bark(self):\n        return 'Woof!'\n\nmy_dog = Dog('Buddy')\nprint(my_dog.bark())\n```",
            "string": "A string is a sequence of characters used to represent text.\n\n```python\nmessage = 'Hello, World!'\nprint(message.upper())\n```",
            "file": "Working with files in Python:\n\n```python\nwith open('file.txt', 'r') as f:\n    content = f.read()\n```",
        }
        
        query_lower = query.lower()
        for key, response in fallback_responses.items():
            if key in query_lower:
                return {
                    "type": "programming",
                    "response": response,
                    "error": None,
                    "corrected_code": "",
                    "improved_versions": [],
                    "documentation": f"## {query}\n\n{response}"
                }
        
        return {
            "type": "programming",
            "response": f"I'd be happy to help with '{query}'! However, I need a Gemini API key to provide a detailed explanation. Please add your API key to the .env file.",
            "error": None,
            "corrected_code": "",
            "improved_versions": [],
            "documentation": f"## {query}\n\nThis is a programming topic. Add your GEMINI_API_KEY for detailed explanations."
        }
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""You are a programming expert. Answer this question clearly with explanation and examples:

{query}

Provide:
1. Clear explanation
2. Code example (if relevant)
3. Best practices

JSON format:
{{
  "response": "explanation here",
  "example_code": "code example if relevant, empty string if not",
  "best_practices": ["practice 1", "practice 2"]
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = result_text[start:end]
            result = json.loads(json_str)
            
            docs = f"## {query}\n\n{result.get('response', '')}"
            if result.get('example_code'):
                docs += f"\n\n### Example Code\n\n```python\n{result.get('example_code')}\n```"
            if result.get('best_practices'):
                docs += f"\n\n### Best Practices\n" + "\n".join([f"- {p}" for p in result.get('best_practices', [])])
            
            return {
                "type": "programming",
                "response": result.get("response", ""),
                "error": None,
                "corrected_code": result.get("example_code", ""),
                "improved_versions": [],
                "documentation": docs
            }
    except Exception as e:
        print(f"Gemini error: {e}")
    
    return {
        "type": "programming",
        "response": f"Here's what I know about {query}:",
        "error": None,
        "corrected_code": "",
        "improved_versions": [],
        "documentation": f"## {query}"
    }


def generate_code_with_gemini(query):
    """Generate code directly when user asks for code."""
    
    if not GEMINI_API_KEY:
        # Better fallback - generate basic code examples
        query_lower = query.lower()
        
        code_examples = {
            # Common patterns
            "reverse": "def reverse_list(lst):\n    return lst[::-1]\n\n# Example\nprint(reverse_list([1, 2, 3, 4, 5]))",
            "sort": "def sort_list(lst):\n    return sorted(lst)\n\n# Example\nprint(sort_list([5, 2, 8, 1, 9]))",
            "prime": "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\n# Example\nprint(is_prime(17))",
            "fibonacci": "def fibonacci(n):\n    fib = [0, 1]\n    for i in range(2, n):\n        fib.append(fib[i-1] + fib[i-2])\n    return fib[:n]\n\n# Example\nprint(fibonacci(10))",
            "factorial": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)\n\n# Example\nprint(factorial(5))",
            "binary search": "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1\n\n# Example\nprint(binary_search([1, 2, 3, 4, 5], 3))",
            "list": "# Python List Operations\nmy_list = [1, 2, 3, 4, 5]\nmy_list.append(6)\nmy_list.pop()\nprint(my_list)",
            "dictionary": "# Python Dictionary Operations\nmy_dict = {'name': 'John', 'age': 30}\nmy_dict['city'] = 'NYC'\nprint(my_dict.get('name'))",
            "string": "# String Operations\ntext = 'Hello World'\nprint(text.upper())\nprint(text.split())\nprint(text.replace('World', 'Python'))",
            # Basic examples
            "basic": "# Basic Python Examples\n\n# Hello World\nprint('Hello, World!')\n\n# Variables\nname = 'John'\nage = 25\nprint(f'Name: {name}, Age: {age}')\n\n# List\nfruits = ['apple', 'banana', 'cherry']\nfor fruit in fruits:\n    print(fruit)",
            "simple": "# Simple Python Examples\n\n# Sum of numbers\nnumbers = [1, 2, 3, 4, 5]\ntotal = sum(numbers)\nprint(f'Sum: {total}')\n\n# Average\naverage = total / len(numbers)\nprint(f'Average: {average}')",
            "example": "# Python Examples\n\n# For loop\nfor i in range(5):\n    print(i)\n\n# While loop\ncount = 0\nwhile count < 5:\n    print(count)\n    count += 1\n\n# If-else\nx = 10\nif x > 5:\n    print('x is greater than 5')\nelse:\n    print('x is less than or equal to 5')",
        }
        
        for key, code in code_examples.items():
            if key in query_lower:
                return {
                    "answer": f"Here's Python code for {query}:",
                    "example_code": code,
                    "documentation": f"## Generated Code\n\n```python\n{code}\n```"
                }
        
        # Default fallback - basic program
        default_code = """# Python Basic Program\n\n# 1. Hello World\nprint('Hello, World!')\n\n# 2. Variables and Data Types\nname = 'Python'\nversion = 3.11\nis_awesome = True\n\nprint(f'Language: {name}')\nprint(f'Version: {version}')\nprint(f'Is Awesome: {is_awesome}')\n\n# 3. List\nlanguages = ['Python', 'JavaScript', 'Java']\nfor lang in languages:\n    print(f'I love {lang}')}\n\n# 4. Function\ndef greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('Developer'))\n\n# 5. Class\nclass Calculator:\n    def add(self, a, b):\n        return a + b\n    \n    def multiply(self, a, b):\n        return a * b\n\ncalc = Calculator()\nprint(f'5 + 3 = {calc.add(5, 3)}')\nprint(f'4 * 7 = {calc.multiply(4, 7)}')"""
        
        return {
            "answer": f"Here's Python basic code for you:",
            "example_code": default_code,
            "documentation": f"## Basic Python Code\n\n```python\n{default_code}\n```"
        }
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""You are a Python expert. Write clean, working Python code for this request:

Request: {query}

Rules:
- Write complete, working code
- Add brief comments
- Keep it simple and readable
- Return ONLY the code, no explanations

Respond with JSON:
{{
  "code": "the python code here",
  "explanation": "one sentence about what it does"
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = result_text[start:end]
            result = json.loads(json_str)
            return {
                "answer": result.get("explanation", ""),
                "example_code": result.get("code", ""),
                "documentation": f"## Generated Code\n\n```python\n{result.get('code', '')}\n```"
            }
    except Exception as e:
        print(f"Gemini error: {e}")
    
    return {
        "answer": "Here's the code you requested:",
        "example_code": "# Code generation",
        "documentation": "## Code"
    }


def analyze_code_with_gemini(code):
    """Use Gemini API to analyze code and provide improvements."""
    
    # First, try to parse and execute the code
    try:
        ast.parse(code)
        is_valid = True
        error_info = None
    except SyntaxError as e:
        is_valid = False
        error_info = {
            "message": str(e.msg) if hasattr(e, 'msg') else str(e),
            "line": e.lineno if hasattr(e, 'lineno') else None,
            "column": e.offset if hasattr(e, 'offset') else None,
            "text": e.text.strip() if hasattr(e, 'text') and e.text else None
        }
    
    # Execute code and get output
    execution_result = execute_python_code(code)
    code_output = execution_result.get("output", "") if execution_result.get("success") else ""
    
    # If code has errors, try to fix it
    if not is_valid:
        # Try local fix first
        fixed_code = local_fix_syntax(code, error_info)
        if fixed_code:
            # Try to execute fixed code
            fixed_result = execute_python_code(fixed_code)
            if fixed_result.get("success"):
                code = fixed_code
                is_valid = True
                error_info = {"message": "Fixed!", "fixed": True}
                code_output = fixed_result.get("output", "")
    
    if not GEMINI_API_KEY:
        result = local_code_analysis(code, is_valid, error_info)
        result["output"] = code_output
        return result
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Review this Python code:

```
{code}
```

Provide JSON with:
{{
  "is_valid": true/false,
  "error": {{"message": "", "line": null}} or null,
  "corrected_code": "fixed code",
  "improvements": [
    {{"version": 1, "code": "v1", "explanation": ""}},
    {{"version": 2, "code": "v2", "explanation": ""}},
    {{"version": 3, "code": "v3", "explanation": ""}}
  ],
  "best_version": 2
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = result_text[start:end]
            result = json.loads(json_str)
            return result
    except Exception as e:
        print(f"Gemini error: {e}")
    
    return local_code_analysis(code, is_valid, error_info)


def local_code_analysis(code, is_valid, error_info):
    """Fallback local code analysis."""
    corrected_code = code
    improvements = []
    code_output = ""
    
    # Execute original code to get output
    if is_valid:
        result = execute_python_code(code)
        if result.get("success"):
            code_output = result.get("output", "")
    
    if not is_valid and error_info:
        lines = code.split('\n')
        fixed_lines = []
        for i, line in enumerate(lines, 1):
            fixed_line = line
            if error_info.get('line') == i:
                stripped = line.strip()
                if (stripped.endswith('if') or stripped.endswith('else') or
                    stripped.endswith('elif') or stripped.endswith('for') or
                    stripped.endswith('while') or stripped.endswith('def') or
                    stripped.endswith('class') or stripped.endswith('try') or
                    stripped.endswith('except') or stripped.endswith('finally')):
                    if not stripped.endswith(':'):
                        fixed_line = line.rstrip() + ':'
            fixed_lines.append(fixed_line)
        
        corrected_code = '\n'.join(fixed_lines)
        
        try:
            ast.parse(corrected_code)
            error_info["fixed"] = True
            error_info["fix_message"] = "Fixed!"
            # Try to execute fixed code
            result = execute_python_code(corrected_code)
            if result.get("success"):
                code_output = result.get("output", "")
        except:
            error_info["fixed"] = False
            corrected_code = code
    
    if is_valid or (error_info and error_info.get('fixed')):
        improvements = [
            {"version": 1, "code": code, "explanation": "Original code"},
            {"version": 2, "code": code, "explanation": "More Pythonic version"},
            {"version": 3, "code": code, "explanation": "Optimized version"}
        ]
    
    return {
        "is_valid": is_valid,
        "error": error_info,
        "corrected_code": corrected_code,
        "improvements": improvements,
        "best_version": 2,
        "output": code_output
    }


def local_fix_syntax(code, error_info):
    """Try to fix syntax errors locally."""
    if not error_info:
        return None
    
    lines = code.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines, 1):
        fixed_line = line
        if error_info.get('line') == i:
            stripped = line.strip()
            # Add colon if missing
            if (stripped.endswith('if') or stripped.endswith('else') or
                stripped.endswith('elif') or stripped.endswith('for') or
                stripped.endswith('while') or stripped.endswith('def') or
                stripped.endswith('class') or stripped.endswith('try') or
                stripped.endswith('except') or stripped.endswith('finally') or
                stripped.endswith('with')):
                if not stripped.endswith(':'):
                    fixed_line = line.rstrip() + ':'
        fixed_lines.append(fixed_line)
    
    fixed_code = '\n'.join(fixed_lines)
    
    # Verify it works
    try:
        ast.parse(fixed_code)
        return fixed_code
    except:
        return None


# ============== MAIN VIEW SET ==============

class AnalyzeViewSet(viewsets.ViewSet):
    serializer_class = AnalyzeInputSerializer

    def create(self, request):
        serializer = AnalyzeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data["query"]
        
        # Detect input type intelligently
        input_type = detect_input_type(query)
        
        # Handle based on detected type
        if input_type == "greeting":
            result = handle_greeting()
        elif input_type == "general":
            result = handle_general_knowledge(query)
        elif input_type == "code_request":
            code_result = generate_code_with_gemini(query)
            result = {
                "type": "code",
                "is_valid": True,
                "error": None,
                "corrected_code": code_result.get("example_code", ""),
                "improved_versions": [],
                "best_version": 0,
                "response": code_result.get("answer", ""),
                "answer": code_result.get("answer", ""),
                "example_code": code_result.get("example_code", ""),
                "documentation": code_result.get("documentation", ""),
                "output": ""
            }
        elif input_type == "code":
            analysis = analyze_code_with_gemini(query)
            result = {
                "type": "code",
                "is_valid": analysis.get("is_valid", True),
                "error": analysis.get("error"),
                "corrected_code": analysis.get("corrected_code", query),
                "improved_versions": analysis.get("improvements", []),
                "best_version": analysis.get("best_version", 2),
                "response": "",
                "answer": "",
                "example_code": analysis.get("corrected_code", ""),
                "documentation": f"## Code Analysis\n\nStatus: {'✅ Correct' if analysis.get('is_valid') else '❌ Has Errors'}",
                "output": analysis.get("output", "")
            }
        else:  # programming
            result = handle_programming_question(query)
        
        # Build response for API
        response_data = {
            "type": result.get("type", "general"),
            "is_valid": result.get("is_valid", True),
            "error": result.get("error"),
            "corrected_code": result.get("corrected_code", ""),
            "improved_versions": result.get("improved_versions", []),
            "best_version": result.get("best_version", 0),
            "answer": result.get("response", ""),
            "example_code": result.get("example_code", ""),
            "documentation": result.get("documentation", ""),
            "output": result.get("output", "")
        }
        
        output_serializer = AnalyzeOutputSerializer(response_data)
        return Response(output_serializer.data)
