from src.producer import send_record


if __name__ == '__main__':
    print("Starting Kafka producer and publishing a message:")
    # "2021-12-12T17:16:19.996Z"
    # 1639336320505
    send_record(
        'aggregator.order',
        {"id": 9, "title": "India", "created": 1639336320505},
        10
    )

