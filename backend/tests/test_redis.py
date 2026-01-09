<<<<<<< HEAD:backend/test_redis.py
"""
Test script to debug the queue setup
"""
from redis_queue import redis_conn, ocr_queue
from worker import process_document
from rq.job import Job
import time

print("=" * 60)
print("QUEUE DIAGNOSTICS")
print("=" * 60)

# Test 1: Redis Connection
print("\n1. Testing Redis Connection...")
try:
    if redis_conn.ping():
        print("   âœ Redis connection: OK")
    else:
        print("   âœ— Redis connection: FAILED")
except Exception as e:
    print(f"   âœ— Redis connection error: {e}")
    exit(1)

# Test 2: Queue Info
print("\n2. Queue Information:")
print(f"   Queue name: {ocr_queue.name}")
print(f"   Jobs in queue: {len(ocr_queue)}")
print(f"   Connection: {ocr_queue.connection}")

# Test 3: List existing jobs
print("\n3. Existing jobs in queue:")
job_ids = ocr_queue.job_ids
if job_ids:
    for job_id in job_ids[:5]:  # Show first 5
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            print(f"   - {job_id}: {job.get_status()}")
        except:
            print(f"   - {job_id}: (could not fetch)")
else:
    print("   No jobs in queue")

# Test 4: Test job enqueue
print("\n4. Testing job enqueue...")
try:
    # Create a test file (you need to have a test image)
    test_job = ocr_queue.enqueue(
        process_document,
        job_id="test-job-123",
        file_path="/path/to/test/image.jpg",  # Update this path
        job_timeout='5m'
    )
    print(f" Job enqueued successfully!")
    print(f"   Job ID: {test_job.id}")
    print(f"   Status: {test_job.get_status()}")
    
    # Wait a bit and check status
    print("\n   Waiting 2 seconds...")
    time.sleep(2)
    
    test_job.refresh()
    print(f"   Updated status: {test_job.get_status()}")
    
    if test_job.is_failed:
        print(f"   âœ— Job failed: {test_job.exc_info}")
    
except Exception as e:
    print(f"   âœ— Enqueue failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Check registries
print("\n5. Job Registries:")
from rq.registry import StartedJobRegistry, FinishedJobRegistry, FailedJobRegistry

started = StartedJobRegistry(queue=ocr_queue)
finished = FinishedJobRegistry(queue=ocr_queue)
failed = FailedJobRegistry(queue=ocr_queue)

print(f"   Started jobs: {started.count}")
print(f"   Finished jobs: {finished.count}")
print(f"   Failed jobs: {failed.count}")

if failed.count > 0:
    print("\n   Recent failed jobs:")
    for job_id in failed.get_job_ids()[:3]:
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            print(f"   - {job_id}")
            print(f"     Error: {job.exc_info}")
        except:
            pass

print("\n" + "=" * 60)
print("DIAGNOSTICS COMPLETE")
print("=" * 60)

print("\n📋 NEXT STEPS:")
print("1. If Redis connection OK but jobs failing:")
print("   - Check if worker.py is running: python worker.py")
print("   - Check file paths in your jobs")
print("   - Check if ai_engine.py is in the same directory")
print("\n2. If no worker is running:")
print("   - Start worker in separate terminal: python worker.py")
print("   - Keep it running in the background")
print("\n3. Check logs:")
print("   - Worker terminal will show processing logs")
print("   - Check for import errors or missing dependencies")
=======
from redis_queue import redis_conn

print(redis_conn.ping())
>>>>>>> 1de5ee8be36aa0996cddad88f7cf26af33429df7:backend/tests/test_redis.py
