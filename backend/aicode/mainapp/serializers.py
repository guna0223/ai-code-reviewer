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


class AnalyzeOutputSerializer(serializers.Serializer):
    type = serializers.CharField()
    error = serializers.CharField(required=False, allow_blank=True)
    corrected_code = serializers.CharField(required=False, allow_blank=True)
    improved_versions = ImprovedVersionSerializer(many=True, required=False)
    best_version = serializers.IntegerField(required=False)
    answer = serializers.CharField(required=False, allow_blank=True)
    example_code = serializers.CharField(required=False, allow_blank=True)
    best_practices = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    explanation = serializers.CharField(required=False, allow_blank=True)
    documentation = serializers.CharField(required=False, allow_blank=True)
