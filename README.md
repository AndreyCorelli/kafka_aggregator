# Kafka Connect Postgresql consumer

https://debezium.io/blog/2017/09/25/streaming-to-another-database/
https://habr.com/ru/company/flant/blog/523510/

## Running the Docker swarm
Run `docker/build_images.sh` script to build debezium/connect + JDBC connect image.
Then run `docker-compose up` command.

This script will:
- create the "aggregator" DB,
- create the MS DB schema in the aggregator DB.

## Source DB setup
*This is not needed in the default configuration* as it has both the source and the target database services. 
First, check the MS DB connection detail in `connectors/ms_conn.json`.

Modify your DB to use "logical" [Write Ahead Log](https://www.postgresql.org/docs/9.6/runtime-config-wal.html) level.
For instance, in you docker-compose.yml file you may add the following commands to your target PostgreSQL DB service:
```yaml
  <DB service>:
    image: ...
    volumes:
      - ...    
    command:
      - "postgres"
      - "-c"
      - "wal_level=logical"
```

Also, your DB user has to belong to the `SUPERUSER` role (`REPLICATION` may do but not necessarily).

## DB setup
Run the following script:

```sh
psql --host localhost --port 5437 -U postgres -f "data/source_schema.txt"
psql --host localhost --port 5436 -U postgres -f "data/target_schema.txt"
```

Connect to the source / target DB with the following:

```sh
psql --host localhost --port 5437 -U postgres -d sennder
psql --host localhost --port 5436 -U postgres -d aggregator
```

## Create / delete / modify connectors

```sh
curl -i -XPOST -H "Content-Type: application/json" -d @connectors/sink_conn.json http://localhost:8083/connectors
curl -i -XPOST -H "Content-Type: application/json" -d @connectors/source_conn.json http://localhost:8083/connectors

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
  --topic connect.order
```

## AKHQ Kafka GUI

[http://localhost:8085/ui/docker-kafka-server](http://localhost:8085/ui/docker-kafka-server/connect/connect/create)