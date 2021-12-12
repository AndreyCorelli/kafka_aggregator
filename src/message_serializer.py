import json

import avro
from confluent_kafka.avro.serializer.message_serializer import HAS_FAST, MessageSerializer

try:
    from fastavro import schemaless_reader, schemaless_writer
    from fastavro.schema import parse_schema

    HAS_FAST = True
except ImportError:
    pass


class JsonFriendlyMessageSerializer(MessageSerializer):
    """
    We need this hack because RecordSchema fails to be serialized and deserialized back
    before the schema query (src/confluent_kafka/avro/serializer/message_serializer.py,
    def _get_encoder_func(self, writer_schema) method).

    See also https://github.com/ffissore/confluent-kafka-python/commit/84f8d35b7f900d37ab141247e50cc36334f59849
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_encoder_func(self, writer_schema):
        if HAS_FAST:
            schema = json.loads(str(writer_schema))
            parsed_schema = parse_schema(schema)
            return lambda record, fp: schemaless_writer(fp, parsed_schema, record)
        writer = avro.io.DatumWriter(writer_schema)
        return lambda record, fp: writer.write(record, avro.io.BinaryEncoder(fp))

    @classmethod
    def extend_serializer(cls, obj):
        obj.__class__ = cls
        return obj
