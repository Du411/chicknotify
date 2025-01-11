FROM redis:latest

COPY redis.conf /usr/local/etc/redis/redis.conf

RUN chmod 777 /home/redis/

CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]