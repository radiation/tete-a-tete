from django.apps import apps
from restapi.tasks import serializers_dict


def mock_create_or_update_record(validated_data, model_name, create=True):
    Model = apps.get_model("restapi", model_name)
    SerializerClass = serializers_dict[model_name]

    if create:
        serializer = SerializerClass(data=validated_data)
    else:
        instance = Model.objects.get(pk=validated_data["id"])
        serializer = SerializerClass(instance, data=validated_data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()
