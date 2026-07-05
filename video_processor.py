import os
import random
from openai import OpenAI
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

class VideoProcessor:
    def __init__(self):
        # Authenticate with OpenAI for voice audio generation
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Map our exact folder paths
        self.bg_dir = os.path.join("assets", "backgrounds")
        self.audio_dir = os.path.join("assets", "audio")
        self.output_dir = os.path.join("assets", "output")

    def generate_voiceover(self, text_script, job_id):
        """Converts raw text scripts into studio-grade voice tracks using AI"""
        print(f"🎙️ Generating voiceover for job {job_id} using OpenAI TTS...")
        audio_path = os.path.join(self.audio_dir, f"{job_id}.mp3")
        
        # Request a high-retention vertical narration voice (Onyx voice profile)
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text_script
        )
        
        # Save the audio binary directly to our asset bin
        response.stream_to_file(audio_path)
        print(f"💾 Voiceover file saved securely to: {audio_path}")
        return audio_path

    def compile_short(self, audio_path, job_id):
        """Slices backgrounds and stitches media elements together into a vertical 9:16 short"""
        print("🎬 Initiating video synthesis timeline...")
        output_path = os.path.join(self.output_dir, f"{job_id}_final.mp4")
        
        # 1. Load your gameplay track background asset
        bg_video_path = os.path.join(self.bg_dir, "gameplay.mp4")
        if not os.path.exists(bg_video_path):
            raise FileNotFoundError("❌ Crucial asset missing: Please drop a gameplay.mp4 into assets/backgrounds/")
            
        video_clip = VideoFileClip(bg_video_path)
        audio_clip = AudioFileClip(audio_path)
        
        # 2. Match timing precisely so background isn't too long or short
        audio_duration = audio_clip.duration
        if video_clip.duration > audio_duration:
            # Pick a random start window inside your gameplay loop to keep shorts feeling fresh
            start_time = random.uniform(0, video_clip.duration - audio_duration)
            video_clip = video_clip.subclip(start_time, start_time + audio_duration)
        else:
            # Loop the clip if your background asset is shorter than the voice track
            video_clip = video_clip.loop(duration=audio_duration)
            
        # Bind the generated voiceover audio track to the video timeline
        video_clip = video_clip.set_audio(audio_clip)
        
        # 3. Format the clip into standard vertical dimensions (1080 width x 1920 height)
        # Crops horizontal footage from the exact center automatically
        video_vertical = video_clip.resize(height=1920).crop(x_center=video_clip.w/2, width=1080)
        
        # 4. Render and bake out the final video compilation
        print("⏳ Rendering engine output (this utilizes local CPU processing matrix)...")
        video_vertical.write_videofile(
            output_path,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            logger=None
        )
        
        # Clean background memory caches safely
        video_clip.close()
        audio_clip.close()
        video_vertical.close()
        
        print(f"🚀 Render complete! File sitting ready at: {output_path}")
        return output_path
