# Kafka Connect Postgresql consumer

See also [the Google document](https://docs.google.com/document/d/1Wv229EfTRCdWMAaEdJdKEaVPt_v30g8Tu-5-kWYTsw8/edit?usp=sharing)

The project runs a number of Docker containers that:
- host 2 databases: the source (“sennder”, port 5437) and the target (“aggregator”, port 5436),
- set up a Kafka pipe from the source (JDBC Source) to the destination (JDBC Sink),
- host a simple GUI for Kafka (http://localhost:8085/ui/docker-kafka-server),
- implement a simple Python producer usage example for populating the target DB from code.


## Running the Docker containers
Run `docker/build_images.sh` script to build debezium/connect + JDBC connect image.
Then run `docker-compose up` command.

## DB setup
Run the following script:

```sh
psql --host localhost --port 5437 -U postgres -f "data/source_schema.txt"
psql --host localhost --port 5436 -U postgres -f "data/target_schema.txt"
```

(password is "postgres")
Connect to the source / target DB with the following:

```sh
psql --host localhost --port 5437 -U postgres -d sennder
psql --host localhost --port 5436 -U postgres -d aggregator
```

## Create / delete / modify connectors

```sh
curl -i -XPOST -H "Content-Type: application/json" -d @connectors/source_conn.json http://localhost:8083/connectors
curl -i -XPOST -H "Content-Type: application/json" -d @connectors/sink_conn.json http://localhost:8083/connectors

curl -i http://localhost:8083/connectors/source-connector/status
curl -i http://localhost:8083/connectors/sink-connector/status

curl -i -XDELETE http://localhost:8083/connectors/source-connector
curl -i -XDELETE http://localhost:8083/connectors/sink-connector
```

## Check the topic

```sh
docker exec -it kafka_aggregator_kafka_1 /bin/bash

./bin/kafka-console-consumer.sh \
  --bootstrap-server kafka:9092 \
  --from-beginning \
  --property print.key=true \
  --topic aggregator.order > message.txt
```

## AKHQ Kafka GUI

[http://localhost:8085/ui/docker-kafka-server](http://localhost:8085/ui/docker-kafka-server/connect/connect/create)