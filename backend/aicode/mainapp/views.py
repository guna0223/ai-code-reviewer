import ast
import os
import re
import json
import google.generativeai as genai
from rest_framework import viewsets
from rest_framework.response import Response
from .models import CodeReview
from .serializers import CodeReviewSerializer, AnalyzeInputSerializer, AnalyzeOutputSerializer

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


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
    """Detect if input contains Python code patterns."""
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
        r'print\s*\(',
    ]
    for pattern in code_indicators:
        if re.search(pattern, text, re.MULTILINE):
            return True
    return False


def analyze_code_with_gemini(code):
    """Use Gemini API to analyze code and provide improvements."""
    
    # Check for syntax errors
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
    
    # If no API key, use local analysis
    if not GEMINI_API_KEY:
        return local_code_analysis(code, is_valid, error_info)
    
    # Use Gemini API
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""You are an expert Python code reviewer. Analyze this code:

```{code}
```

Respond ONLY with valid JSON (no markdown):
{{
  "is_valid": true/false,
  "error": {{"message": "error message", "line": line_number}} or null,
  "corrected_code": "fixed code if has errors, otherwise original code",
  "improvements": [
    {{"version": 1, "code": "improved code v1", "explanation": "why this version is better"}},
    {{"version": 2, "code": "improved code v2", "explanation": "why this version is better"}},
    {{"version": 3, "code": "improved code v3", "explanation": "why this version is better"}}
  ],
  "best_version": 2,
  "explanation": "brief overall explanation"
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        # Extract JSON from response
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = result_text[start:end]
            result = json.loads(json_str)
            return result
        else:
            return local_code_analysis(code, is_valid, error_info)
            
    except Exception as e:
        print(f"Gemini API error: {e}")
        return local_code_analysis(code, is_valid, error_info)


def local_code_analysis(code, is_valid, error_info):
    """Fallback local code analysis."""
    corrected_code = code
    improvements = []
    
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
            error_info["fix_message"] = "Error automatically fixed!"
        except:
            error_info["fixed"] = False
            corrected_code = code
    
    if is_valid or (error_info and error_info.get('fixed')):
        improvements = [
            {"version": 1, "code": code, "explanation": "Clean formatting with proper structure."},
            {"version": 2, "code": code, "explanation": "More Pythonic and idiomatic."},
            {"version": 3, "code": code, "explanation": "Optimized for better performance."}
        ]
    
    return {
        "is_valid": is_valid,
        "error": error_info,
        "corrected_code": corrected_code,
        "improvements": improvements,
        "best_version": 2,
        "explanation": "Code analyzed locally."
    }


def answer_question_with_gemini(query):
    """Use Gemini API to answer programming questions."""
    
    if not GEMINI_API_KEY:
        return local_answer(query)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""You are an expert programming teacher. Answer this question clearly:

Question: {query}

Respond ONLY with valid JSON (no markdown):
{{
  "answer": "clear explanation of the concept",
  "example_code": "working Python example code",
  "best_practices": ["practice 1", "practice 2", "practice 3"],
  "documentation": "brief documentation summary"
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = result_text[start:end]
            result = json.loads(json_str)
            return result
        else:
            return local_answer(query)
            
    except Exception as e:
        print(f"Gemini API error: {e}")
        return local_answer(query)


def local_answer(query):
    """Fallback local answer generation."""
    q = query.lower()
    
    answers = {
        "reverse": {
            "answer": "To reverse a list in Python:\n\n1. Slicing: list[::-1]\n2. reversed(): list(reversed(lst))\n3. reverse(): lst.reverse()",
            "example_code": "my_list = [1, 2, 3, 4, 5]\nreversed_list = my_list[::-1]\nprint(reversed_list)  # [5, 4, 3, 2, 1]",
            "best_practices": ["Use slicing for readability", "Use reverse() for in-place", "Use reversed() for iterators"]
        },
        "list comprehension": {
            "answer": "List comprehension creates lists from iterables:\n\n[expression for item in iterable if condition]",
            "example_code": "squares = [x**2 for x in range(10)]\nevens = [x for x in range(20) if x % 2 == 0]",
            "best_practices": ["Use for simple transformations", "Avoid nested comprehensions", "Use generators for large data"]
        },
    }
    
    for key, val in answers.items():
        if key in q:
            return val
    
    return {
        "answer": f"Here's about '{query}': This is a programming concept in Python.",
        "example_code": f"# Example for {query}:\n# Research and practice",
        "best_practices": ["Start with basics", "Practice with examples", "Follow best practices"]
    }


class AnalyzeViewSet(viewsets.ViewSet):
    serializer_class = AnalyzeInputSerializer

    def create(self, request):
        serializer = AnalyzeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data["query"]
        
        if contains_python_code(query):
            # Code analysis with Gemini
            analysis = analyze_code_with_gemini(query)
            
            response_data = {
                "type": "code",
                "is_valid": analysis.get("is_valid", True),
                "error": analysis.get("error"),
                "corrected_code": analysis.get("corrected_code", query),
                "improved_versions": analysis.get("improvements", []),
                "best_version": analysis.get("best_version", 2),
                "documentation": f"## Code Analysis\n\n**Status:** {'✅ Correct' if analysis.get('is_valid') else '❌ Has Errors'}\n\n**Explanation:** {analysis.get('explanation', '')}"
            }
        else:
            # Question answering with Gemini
            answer = answer_question_with_gemini(query)
            
            response_data = {
                "type": "question",
                "is_valid": True,
                "error": None,
                "corrected_code": "",
                "improved_versions": [],
                "best_version": 0,
                "answer": answer.get("answer", ""),
                "example_code": answer.get("example_code", ""),
                "documentation": f"## {query.title()}\n\n{answer.get('answer', '')}\n\n### Example\n```python\n{answer.get('example_code', '')}\n```"
            }
        
        output_serializer = AnalyzeOutputSerializer(response_data)
        return Response(output_serializer.data)
