# Kafka Connect Postgresql consumer

https://debezium.io/blog/2017/09/25/streaming-to-another-database/
https://habr.com/ru/company/flant/blog/523510/

## Running the Docker swarm
Run `docker/build_images.sh` script to build debezium/connect + JDBC connect image.
Then run `docker-compose up` command.

# Target (aggregation) DB setup
Run the following script:

```sh
psql --host localhost --port 5436 -U postgres -f "data/account_users_schema.txt"
```

This script will:
- create the "aggregator" DB,
- create the MS DB schema in the aggregator DB.

## Source DB setup
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

## Create / delete / modify connectors

```sh
curl -i -XPOST -H "Content-Type: application/json" -d @connectors/aggregator_sink_conn.json http://localhost:8083/connectors
curl -i -XPOST -H "Content-Type: application/json" -d @connectors/ms_conn.json http://localhost:8083/connectors

curl -i -XDELETE http://localhost:8083/connectors/ms-connector
curl -i -XDELETE http://localhost:8083/connectors/aggregator-sink-connector
  
curl -i http://localhost:8083/connectors/ms-connector/status
curl -i http://localhost:8083/connectors/aggregator-sink-connector/status
```

## Check the topic

```sh
docker exec -it kafka_connect_kafka_1 /bin/bash

./bin/kafka-console-consumer.sh \
  --bootstrap-server kafka:9092 \
  --from-beginning \
  --property print.key=true \
  --topic data.ms.sennder
```