from src.producer import send_record


if __name__ == '__main__':
    print("Starting Kafka producer and publishing a message:")
    send_record(
        'aggregator.order',
        {"id": 4, "title": "Delta", "created": 1639336320505},
        5
    )

