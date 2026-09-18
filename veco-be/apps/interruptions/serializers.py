from rest_framework import serializers


class ScheduleEntrySerializer(serializers.Serializer):
    date_label = serializers.CharField()
    date_start = serializers.DateField()
    date_end = serializers.DateField()
    time = serializers.CharField()
    purpose = serializers.CharField()
    areas_affected = serializers.CharField()
    map_url = serializers.URLField(allow_null=True)


class LatestInterruptionSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    url = serializers.URLField()
    category = serializers.CharField(allow_blank=True)
    published_at = serializers.DateTimeField()
    image_url = serializers.URLField(allow_null=True)
    author = serializers.CharField(allow_blank=True)
    schedule = ScheduleEntrySerializer(many=True)


class InterruptionEventSerializer(ScheduleEntrySerializer):
    category = serializers.CharField(allow_blank=True)
    status = serializers.CharField(allow_blank=True)
    source_id = serializers.CharField()
    source_title = serializers.CharField()
    source_url = serializers.URLField()
    source_published_at = serializers.DateTimeField(allow_null=True)
