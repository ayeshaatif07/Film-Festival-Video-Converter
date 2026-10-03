#!/usr/bin/env python
# coding: utf-8

# # Exercise 3 

# This Exercise builds a practical and automated system to check whether submitted films meet the Narbonne Online Film Festival’s technical requirements. The program first ensures that ffmpeg and ffprobe are available, then clearly defines the required format, including MP4 container, H.265 video codec, AAC audio, 25 FPS, 640×360 resolution, and 16:9 aspect ratio. It uses ffprobe to read each video’s technical details and compares them against these standards. If a video does not comply, the system automatically converts it using ffmpeg. The outputs show multiple files being analysed and successfully converted, proving the application works reliably and efficiently.

# # Project Header

# In[1]:


# Intelligent Signal Processing - Exercise 3
# Narbonne Online Film Festival - Video Format Checker and Converter

import subprocess
import json
import os
import sys
from datetime import datetime

print("="*70)
print("🎬 NARBONNE ONLINE FILM FESTIVAL")
print("   Video Format Checker & Converter")
print("="*70)


# # Install ffmpeg

# In[2]:


# ============================================================================
# Install and verify ffmpeg & ffprobe
# ============================================================================

# This function installs ffmpeg using apt-get (Linux environment)
# ffprobe is included with ffmpeg
# It also verifies installation after setup

def install_ffmpeg():
    
    print("\n📦 INSTALLING FFMPEG AND FFPROBE...")
    print("-" * 70)
    
    try:
        # Update system package list
        print("   Updating package list...")
        subprocess.run(['apt-get', 'update', '-qq'], 
                      check=True, 
                      capture_output=True)
        
        # Install ffmpeg package
        print("   Installing ffmpeg (includes ffprobe)...")
        subprocess.run(['apt-get', 'install', '-y', '-qq', 'ffmpeg'], 
                      check=True,
                      capture_output=True)
        
        print("   ✅ Installation successful!")
        
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # If installation fails (or apt-get is missing, e.g. macOS)
        print(f"   ⚠️  Installation failed: {e}")
        print("   Checking if ffmpeg is already installed...")
    
    # Verify that ffmpeg and ffprobe work
    try:
        ffmpeg_version = subprocess.run(['ffmpeg', '-version'], 
                                       capture_output=True, 
                                       text=True, 
                                       check=True)
        ffprobe_version = subprocess.run(['ffprobe', '-version'], 
                                        capture_output=True, 
                                        text=True, 
                                        check=True)
        
        print("\n✅ FFMPEG CONFIGURATION:")
        print(f"   {ffmpeg_version.stdout.split(chr(10))[0]}")
        print(f"\n✅ FFPROBE CONFIGURATION:")
        print(f"   {ffprobe_version.stdout.split(chr(10))[0]}")
        
        return True
        
    except FileNotFoundError:
        print("❌ ERROR: ffmpeg/ffprobe not found after installation attempt")
        return False


# Run installation function
if not install_ffmpeg():
    print("\n⚠️  WARNING: Proceeding without ffmpeg/ffprobe installation")


# # Required Format Specifications

# In[3]:


# ============================================================================
# Required video format specifications
# ============================================================================

# This dictionary defines the festival requirements
# Every video will be compared against these values

REQUIRED_FORMAT = {
    'container': 'mp4',
    'video_codec': 'hevc',      # H.265 codec
    'audio_codec': 'aac',
    'frame_rate': 25.0,
    'aspect_ratio': '16:9',
    'width': 640,
    'height': 360,
    'video_bitrate_min': 2_000_000,
    'video_bitrate_max': 5_000_000,
    'audio_bitrate_max': 256_000,
    'audio_channels': 2
}

# Display required specifications clearly
print("\n" + "="*70)
print("📋 REQUIRED VIDEO FORMAT SPECIFICATIONS")
print("="*70)
print(f"   Container Format:    {REQUIRED_FORMAT['container'].upper()}")
print(f"   Video Codec:         {REQUIRED_FORMAT['video_codec'].upper()} (H.265)")
print(f"   Audio Codec:         {REQUIRED_FORMAT['audio_codec'].upper()}")
print(f"   Frame Rate:          {REQUIRED_FORMAT['frame_rate']} FPS")
print(f"   Aspect Ratio:        {REQUIRED_FORMAT['aspect_ratio']}")
print(f"   Resolution:          {REQUIRED_FORMAT['width']}x{REQUIRED_FORMAT['height']}")
print("="*70)


# # Analyze the Video

# In[4]:


# ============================================================================
# Extract video metadata using ffprobe
# ============================================================================

# This function runs ffprobe command
# It extracts technical information from the video file
# The output is returned as a dictionary

def get_video_info(video_file):

    try:
        # ffprobe command to extract format + stream information
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_file
        ]
        
        # Execute command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        # Identify video and audio streams
        video_stream = None
        audio_stream = None
        
        for stream in data.get('streams', []):
            if stream['codec_type'] == 'video' and video_stream is None:
                video_stream = stream
            elif stream['codec_type'] == 'audio' and audio_stream is None:
                audio_stream = stream
        
        # If no video stream found → invalid file
        if not video_stream:
            return None
        
        # Extract resolution
        width = int(video_stream.get('width', 0))
        height = int(video_stream.get('height', 0))

        # Calculate frame rate
        fps_str = video_stream.get('r_frame_rate', '0/1')
        fps_parts = fps_str.split('/')
        frame_rate = float(fps_parts[0]) / float(fps_parts[1])

        # Return structured metadata dictionary
        return {
            'filename': os.path.basename(video_file),
            'filepath': video_file,
            'container': data['format']['format_name'],  # full list, e.g. "mov,mp4,m4a,3gp,3g2,mj2"
            'video_codec': video_stream.get('codec_name', 'unknown'),
            'audio_codec': audio_stream.get('codec_name', 'unknown') if audio_stream else 'none',
            'width': width,
            'height': height,
            'frame_rate': frame_rate
        }

    except Exception as e:
        print(f"   ❌ Error processing {video_file}: {e}")
        return None


# # Compliance Check

# In[5]:


# ============================================================================
# Check if video meets festival requirements
# ============================================================================

# This function compares extracted metadata
# with REQUIRED_FORMAT dictionary

def check_format_compliance(video_info):

    issues = []

    # Check container format (ffprobe lists several names for MP4/MOV, so also check the extension)
    is_mp4 = (REQUIRED_FORMAT['container'] in video_info['container'].split(',')
              and video_info['filename'].lower().endswith('.mp4'))
    if not is_mp4:
        issues.append("Container format mismatch")

    # Check video codec
    if video_info['video_codec'] != REQUIRED_FORMAT['video_codec']:
        issues.append("Video codec mismatch")

    # Check audio codec
    if video_info['audio_codec'] != REQUIRED_FORMAT['audio_codec']:
        issues.append("Audio codec mismatch")

    # Check resolution
    if video_info['width'] != REQUIRED_FORMAT['width'] or        video_info['height'] != REQUIRED_FORMAT['height']:
        issues.append("Resolution mismatch")

    # Check frame rate (allow slight tolerance)
    if abs(video_info['frame_rate'] - REQUIRED_FORMAT['frame_rate']) > 0.1:
        issues.append("Frame rate mismatch")

    return len(issues) == 0, issues


# # Convert Video

# In[6]:


# ============================================================================
# Convert non-compliant videos
# ============================================================================

# Uses ffmpeg to convert video into required format
# Applies H.265 codec and required resolution

def convert_video(input_file, output_file):

    try:
        print(f"\n   🔄 Converting: {os.path.basename(input_file)}")
        print("   ⏳ Please wait...")

        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-y',
            '-c:v', 'libx265',
            '-preset', 'medium',
            '-crf', '23',
            '-vf', f'scale={REQUIRED_FORMAT["width"]}:{REQUIRED_FORMAT["height"]},fps={REQUIRED_FORMAT["frame_rate"]}',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-ac', '2',
            '-f', 'mp4',
            '-movflags', '+faststart',
            output_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("   ✅ Conversion successful!")
            return True
        else:
            print("   ❌ Conversion failed!")
            return False

    except Exception as e:
        print(f"   ❌ Conversion error: {e}")
        return False


# # Main Processing

# In[7]:


# Process all videos in directory

def process_videos(video_directory='./Exercise3files'):

    if not os.path.exists(video_directory):
        print("Directory not found")
        return None

    video_files = [
        os.path.join(video_directory, f)
        for f in os.listdir(video_directory)
        if f.lower().endswith(('.mp4','.avi','.mov','.mkv','.flv','.wmv','.m4v'))
    ]

    results = []

    for video in video_files:
        print("\nProcessing:", os.path.basename(video))

        info = get_video_info(video)
        if not info:
            continue

        compliant, issues = check_format_compliance(info)

        if compliant:
            print("✅ Already compliant")
        else:
            print("❌ Not compliant:", issues)

            output = os.path.join(
                video_directory,
                os.path.splitext(info['filename'])[0] + "_formatOK.mp4"
            )

            convert_video(video, output)

        results.append(info['filename'])

    return results


# # Run Program

# In[8]:


# ============================================================================
# Run the full application
# ============================================================================

if __name__ == "__main__":
    
    # Set folder containing video files
    VIDEO_DIRECTORY = './Exercise3files'
    
    print(f"\n🎯 Target Directory: {VIDEO_DIRECTORY}")
    print(f"🎯 Absolute Path: {os.path.abspath(VIDEO_DIRECTORY)}")
    
    # Start processing
    results = process_videos(VIDEO_DIRECTORY)
    
    if results:
        print("\n" + "="*70)
        print("✅ APPLICATION COMPLETED SUCCESSFULLY")
        print("="*70)
    else:
        print("\n⚠️  No videos were processed")


# In[ ]:




