import os
import time
from supabase import create_client, Client
from openai import OpenAI

# 1. Boot up and load your environment secret keys
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Missing Supabase connection keys in environment.")
    exit(1)

# Initialize cloud database connections
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("⚡ ShadowPostclips Engine initialized successfully.")

def check_for_video_jobs():
    """Scans your Supabase database for queued automation tasks"""
    print("🔍 Scanning database for 'queued' rendering tasks...")
    
    # Query the video_jobs table we built in Step 1A
    jobs = supabase.table("video_jobs").select("*").eq("status", "queued").execute()
    
    if len(jobs.data) == 0:
        print("😴 No video jobs waiting in queue.")
        return
        
    for job in jobs.data:
        job_id = job["id"]
        topic = job["topic"]
        print(f"🚀 Found job {job_id} for topic: '{topic}'. Processing...")
        
        # Update status to processing so engines don't overlap
        supabase.table("video_jobs").update({"status": "processing"}).eq("id", job_id).execute()
        
        # (Media compilation and generation workflows will execute here next)
        time.sleep(2) 
        
        # Complete the job pipeline
        supabase.table("video_jobs").update({"status": "completed"}).eq("id", job_id).execute()
        print(f"✅ Job {job_id} successfully rendered and closed.")

if __name__ == "__main__":
    # Run a continuous loop checking for new requests every 10 seconds
    while True:
        try:
            check_for_video_jobs()
        except Exception as e:
            print(f"⚠️ Worker Error: {e}")
        time.sleep(10)
