import os
import pathlib
import uuid
from typing import Any, Dict

from confluent_kafka.avro import AvroProducer
from confluent_kafka import avro

from src.message_serializer import JsonFriendlyMessageSerializer


def load_avro_schema_from_file(schema_file: str):
    key_schema_string = """
    {"type": "int"}
    """
    key_schema = avro.loads(key_schema_string)
    cur_path = pathlib.Path(__file__).parent.resolve()
    schemas_path = os.path.join(cur_path, 'schemas')
    value_schema = avro.load(os.path.join(schemas_path, schema_file))
    return key_schema, value_schema


def send_record(
        topic: str,
        value: Dict[str, Any],
        record_key: int,
        schema_file: str = 'order.avsc',
        bootstrap_servers: str = 'localhost:9092',
        schema_registry: str = 'http://localhost:8081'):
    key_schema, value_schema = load_avro_schema_from_file(schema_file)
    # value_schema = JsonFriendlyRecordSchema.extend_schema(value_schema)

    producer_config = {
        "bootstrap.servers": bootstrap_servers,
        "schema.registry.url": schema_registry
    }

    producer = AvroProducer(producer_config, default_key_schema=key_schema, default_value_schema=value_schema)
    producer._serializer = JsonFriendlyMessageSerializer.extend_serializer(producer._serializer)

    key = record_key if record_key else str(uuid.uuid4())

    try:
        producer.produce(topic=topic, key=key, value=value)
    except Exception as e:
        print(f"Exception while producing record value - {value} to topic - {topic}: {e}")
    else:
        print(f"Successfully producing record value - {value} to topic - {topic}")

    producer.flush()
