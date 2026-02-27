import ast
from rest_framework import viewsets
from .models import CodeReview
from .serializers import CodeReviewSerializer


class CodeReviewViewSet(viewsets.ModelViewSet):
    queryset = CodeReview.objects.all()
    serializer_class = CodeReviewSerializer

    def perform_create(self, serializer):
        code = serializer.validated_data["code"]

        try:
            # Check syntax
            ast.parse(code)
            review = "✅ Code is syntactically correct."

            # Simple checks
            if "print(" in code:
                review += " Avoid print statements in production."

            if "==" in code and "None" in code:
                review += " Use 'is None' instead of '== None'."

            if "for" in code:
                review += " Loop detected. Check performance."

        except SyntaxError as e:
            review = f"❌ Syntax Error: {e}"

        serializer.save(review=review)