import redis
from rq import Queue

REDIS_HOST = "redis-10817.crce217.ap-south-1-1.ec2.cloud.redislabs.com"
REDIS_PORT = 10817
REDIS_USERNAME = "default"
REDIS_PASSWORD = "XEA5vbzE4ilKDvdCpfK6tEYCNWk6o6SY"

redis_conn = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=True,
)

ocr_queue = Queue(
    name="ocr_queue",
    connection=redis_conn
)
