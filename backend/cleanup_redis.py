"""
Cleanup script to remove corrupted jobs from Redis
"""
import redis

REDIS_HOST = "redis-10817.crce217.ap-south-1-1.ec2.cloud.redislabs.com"
REDIS_PORT = 10817
REDIS_USERNAME = "default"
REDIS_PASSWORD = "XEA5vbzE4ilKDvdCpfK6tEYCNWk6o6SY"

print("🧹 Cleaning up Redis...")
print("=" * 60)

# Connect with decode_responses=False (binary mode - for RQ)
redis_conn = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=False,
)

try:
    # Test connection
    redis_conn.ping()
    print("✓ Connected to Redis")
    
    # Get all keys related to RQ
    print("\n📋 Finding RQ-related keys...")
    keys = redis_conn.keys("rq:*")
    print(f"   Found {len(keys)} RQ keys")
    
    if keys:
        print("\n🗑️  Deleting keys...")
        deleted = redis_conn.delete(*keys)
        print(f"   ✓ Deleted {deleted} keys")
    
    # Also clear the specific job that's corrupted
    print("\n🗑️  Clearing corrupted job...")
    job_key = b"rq:job:test-job-123"
    if redis_conn.exists(job_key):
        redis_conn.delete(job_key)
        print(f"   ✓ Deleted {job_key}")
    else:
        print(f"   ℹ️  Job key doesn't exist")
    
    # Clear the queue
    print("\n🗑️  Clearing ocr_queue...")
    queue_key = b"rq:queue:ocr_queue"
    if redis_conn.exists(queue_key):
        redis_conn.delete(queue_key)
        print(f"   ✓ Cleared queue")
    else:
        print(f"   ℹ️  Queue is already empty")
    
    print("\n" + "=" * 60)
    print("✅ Cleanup complete!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("1. Make sure redis_queue.py has decode_responses=False")
    print("2. Restart any running workers")
    print("3. Try uploading a new document")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    redis_conn.close()