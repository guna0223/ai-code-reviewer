from rest_framework import serializers
from .models import CodeReview


class CodeReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeReview
        fields = "__all__"


class AnalyzeInputSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)


class ImprovedVersionSerializer(serializers.Serializer):
    version = serializers.IntegerField()
    code = serializers.CharField()
    explanation = serializers.CharField()


class ErrorInfoSerializer(serializers.Serializer):
    message = serializers.CharField(required=False)
    line = serializers.IntegerField(required=False)
    column = serializers.IntegerField(required=False)
    text = serializers.CharField(required=False)
    fixed = serializers.BooleanField(required=False)
    fix_message = serializers.CharField(required=False)


class AnalyzeOutputSerializer(serializers.Serializer):
    type = serializers.CharField()
    is_valid = serializers.BooleanField()
    error = ErrorInfoSerializer(required=False)
    corrected_code = serializers.CharField(required=False, allow_blank=True)
    improved_versions = ImprovedVersionSerializer(many=True, required=False)
    best_version = serializers.IntegerField(required=False)
    answer = serializers.CharField(required=False, allow_blank=True)
    example_code = serializers.CharField(required=False, allow_blank=True)
    documentation = serializers.CharField(required=False, allow_blank=True)
