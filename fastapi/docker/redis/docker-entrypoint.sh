#!/bin/bash
# @Author: Daniel Gomes
# @Date:   2022-10-26 15:20:56
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-18 11:33:41
#!/bin/sh
set -e

# first arg is `-f` or `--some-option`
# or first arg is `something.conf`
if [ "${1#-}" != "$1" ] || [ "${1%.conf}" != "$1" ]; then
	set -- redis-server "$@"
fi

# allow the container to be started with `--user`
if [ "$1" = 'redis-server' -a "$(id -u)" = '0' ]; then
	find . \! -user redis -exec chown redis '{}' +
	exec gosu redis "$0" "$@"
fi

# set an appropriate umask (if one isn't set already)
# - https://github.com/docker-library/redis/issues/305
# - https://github.com/redis/redis/blob/bb875603fb7ff3f9d19aad906bd45d7db98d9a39/utils/systemd-redis_server.service#L37
um="$(umask)"
if [ "$um" = '0022' ]; then
	umask 0077
fi

# save ip in an environment variable
export HOST=$IMAGE_NAME-$(hostname)
# Run metric collector - telegraf
eval  "telegraf --config redis_telegraf.conf &"
echo "running telegraf..."

exec "$@"
