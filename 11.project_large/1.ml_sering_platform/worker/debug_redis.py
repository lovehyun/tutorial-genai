import redis
import json
import sys
from app.core.config import settings
from worker.celery_app import celery_app

def clear_redis():
    """Clear all Redis queues and task data"""
    r = redis.from_url(settings.REDIS_URL)
    
    print("\n=== Clearing Redis Data ===")
    
    # Clear inference_tasks queue
    queue_length = r.llen("inference_tasks")
    if queue_length > 0:
        r.delete("inference_tasks")
        print(f"Cleared inference_tasks queue ({queue_length} items)")
    
    # Clear task statuses
    task_keys = r.keys("task:*")
    if task_keys:
        for key in task_keys:
            r.delete(key)
        print(f"Cleared {len(task_keys)} task status entries")
    
    # Clear task results
    result_keys = r.keys("task_result:*")
    if result_keys:
        for key in result_keys:
            r.delete(key)
        print(f"Cleared {len(result_keys)} task results")
    
    print("Redis data cleared successfully!")

def check_redis_queue():
    # Redis 연결
    r = redis.from_url(settings.REDIS_URL)
    
    print("\n=== Redis Connection Test ===")
    try:
        r.ping()
        print("Redis connection successful!")
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return
    
    print("\n=== Celery Configuration ===")
    print(f"Broker URL: {celery_app.conf.broker_url}")
    print(f"Result Backend: {celery_app.conf.result_backend}")
    
    print("\n=== Redis Queue Status ===")
    
    # inference_tasks 큐 확인
    queue_length = r.llen("inference_tasks")
    print(f"\nInference Tasks Queue Length: {queue_length}")
    
    if queue_length > 0:
        print("\nRecent Tasks in Queue:")
        tasks = r.lrange("inference_tasks", 0, -1)
        for task in tasks:
            task_data = json.loads(task)
            print(f"\nTask ID: {task_data.get('task_id')}")
            print(f"Model ID: {task_data.get('model_id')}")
            print(f"Input Data: {task_data.get('input_data')}")
    
    # task 상태 확인
    print("\nTask Statuses:")
    task_keys = r.keys("task:*")
    for key in task_keys:
        task_id = key.decode().split(":")[1]
        status = r.hgetall(key)
        print(f"\nTask {task_id}:")
        for k, v in status.items():
            print(f"  {k.decode()}: {v.decode()}")
    
    # task 결과 확인
    print("\nTask Results:")
    result_keys = r.keys("task_result:*")
    for key in result_keys:
        task_id = key.decode().split(":")[1]
        result = r.get(key)
        if result:
            print(f"\nTask {task_id} Result:")
            print(json.dumps(json.loads(result), indent=2))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_redis()
    else:
        check_redis_queue() 