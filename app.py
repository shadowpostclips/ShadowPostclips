import os
import time
from supabase import create_client, Client
# Import your brand new video rendering logic!
from video_processor import VideoProcessor

# 1. Boot up and load your environment secret keys
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Missing Supabase connection keys in environment.")
    exit(1)

# Initialize cloud database and video processors
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
processor = VideoProcessor()
print("⚡ ShadowPostclips Engine initialized successfully.")

def check_for_video_jobs():
    """Scans your Supabase database for queued automation tasks"""
    print("🔍 Scanning database for 'queued' rendering tasks...")
    
    # Query the video_jobs table
    jobs = supabase.table("video_jobs").select("*").eq("status", "queued").execute()
    
    if len(jobs.data) == 0:
        print("😴 No video jobs waiting in queue.")
        return
        
    for job in jobs.data:
        job_id = job["id"]
        topic = job["topic"]
        print(f"🚀 Found job {job_id} for topic: '{topic}'. Processing...")
        
        try:
            # Update status to processing so engines don't overlap
            supabase.table("video_jobs").update({"status": "processing"}).eq("id", job_id).execute()
            
            # Step A: Synthesize the AI Voice Track using the topic text as the script
            audio_path = processor.generate_voiceover(topic, job_id)
            
            # Step B: Slice, crop, and compile the final short MP4 file
            final_mp4_path = processor.compile_short(audio_path, job_id)
            
            # Update database status to completed
            supabase.table("video_jobs").update({"status": "completed"}).eq("id", job_id).execute()
            print(f"✅ Job {job_id} successfully rendered and closed.")
            
        except Exception as job_error:
            print(f"❌ Failed rendering job {job_id}: {job_error}")
            supabase.table("video_jobs").update({"status": "failed"}).eq("id", job_id).execute()

if __name__ == "__main__":
    while True:
        try:
            check_for_video_jobs()
        except Exception as e:
            print(f"⚠️ Worker Error: {e}")
        time.sleep(10)
