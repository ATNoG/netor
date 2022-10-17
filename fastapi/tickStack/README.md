# Requirements
1. docker
2. docker-compose

# Environment variables needed

| Variable Name           | Description                                                                                           | Example               |
|-------------------------|-------------------------------------------------------------------------------------------------------|-----------------------|
| ORGANIZATION            | Organization's name                                                                                   | 5gasp             |
| INFLUXDB_ADMIN_USER     | The name of the admin user to be created                                                              | admin                 |
| INFLUXDB_ADMIN_PASSWORD | The password for the admin user configured with  `$INFLUXDB_ADMIN_USER`                                 | *******               |
| METRIC_DB               | Metrics DB name                                                                                       | metrics               |
| INFLUXDB_USER           | The name of a user to be created with read and write permissions for `$METRIC_DB` and `chronograf DB` | netor_user        |
| INFLUXDB_USER_PASSWORD  | The password for the user configured with  $INFLUXDB_USER                                             | *******               |
| INFLUXDB_URL            | InfluxDB http URL                                                                                     | http://influxdb:8086  |
| KAPACITOR_URL           | Kapacitor http URL                                                                                    | http://kapacitor:9092 |

## Defining environment variables
1. Defining and exporting all variables on bash shell
2. Create a .env file as described in <https://www.techrepublic.com/article/how-to-use-docker-env-file/>

# Running services
> :warning: **Volumes path defined in docker-compose files need to be fully created before running any command**

1. Run `influxdb` | `kapacitor` | `chronograf` services
```bash
docker-compose -f ick_stack.yml up -d
```

2. Run `telegraf` service
```bash
docker-compose -f telegraf.yml up -d
```

