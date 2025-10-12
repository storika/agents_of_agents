# Video Generation Agent - Guide

Generate 8-second short-form vertical videos (9:16) from images using Google Gemini Veo 3 API.

## 🎯 Overview

The Video Generation Agent extends the CMO Agent's image generation capabilities by creating short-form videos optimized for:
- Instagram Reels
- TikTok
- YouTube Shorts
- Twitter/X videos

**Key Features**:
- ✅ **Image-to-Video**: Generate videos from generated images
- ✅ **Text-to-Video**: Generate videos directly from prompts
- ✅ **Vertical Format**: 9:16 aspect ratio for social media stories
- ✅ **Professional Quality**: 720p/1080p resolution, 24fps
- ✅ **Smooth Cinematography**: AI-generated camera movements and effects

## 📋 Prerequisites

### 1. Google API Setup

You need a Google API key with Veo 3 access:

1. Get API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Ensure Veo 3 API access is enabled in your account
3. Add to `.env` file:

```bash
GOOGLE_API_KEY=your_api_key_here
```

### 2. Dependencies

Video generation requires:
- `google-generativeai>=0.8.5` (already in project)
- `google-adk` for agent orchestration

Dependencies are already configured in `pyproject.toml`.

## 🚀 Usage

### Method 1: Standalone Video Generation Test

Generate a video from an existing image:

```bash
# Use most recent generated image
python examples/video_generation_test.py

# Or specify an image
python examples/video_generation_test.py artifacts/generated_image_20251011_220355.png
```

**Workflow**:
1. Loads existing image from `artifacts/`
2. Generates motion/cinematography concept
3. Calls Veo 3 API for video generation
4. Polls operation until complete (11s-6min)
5. Downloads video to `artifacts/generated_video_TIMESTAMP.mp4`

### Method 2: Python API

```python
import asyncio
from video_generation_agent.tools import (
    generate_video_concept,
    generate_video_from_image
)

async def generate_video():
    # Step 1: Create motion concept
    concept_result = await generate_video_concept(
        image_concept="Modern AI agents visualization with vibrant colors",
        topic="AI Agents",
        tone="engaging",
        tool_context=tool_context
    )

    motion_prompt = concept_result['motion_prompt']

    # Step 2: Generate video from image
    video_result = await generate_video_from_image(
        image_path="artifacts/generated_image.png",
        motion_prompt=motion_prompt,
        tool_context=tool_context,
        aspect_ratio="9:16",
        duration=8
    )

    print(f"Video saved to: {video_result['video_path']}")

asyncio.run(generate_video())
```

### Method 3: Integrate with CMO Agent

The video generator is already integrated into CMO Agent as an optional step:

```python
from cmo_agent.sub_agents import create_video_generator_agent

# Create video generator agent
video_agent = create_video_generator_agent()

# Agent will automatically generate video after image generation
# (if user requests video or if it adds significant value)
```

## 📐 Video Specifications

| Property | Value |
|----------|-------|
| Duration | 8 seconds |
| Aspect Ratio | 9:16 (vertical) |
| Resolution | 720p or 1080p |
| Frame Rate | 24fps |
| Format | MP4 |
| Model | Veo 3 (veo-3.0-generate-001) |

## 🎬 Motion Concept Examples

**Good Motion Prompts**:
- "Slow zoom in on subject with smooth cinematic motion, maintaining center framing"
- "Gentle pan from left to right, revealing the AI visualization gradually, soft lighting"
- "Static shot with text overlays fading in and out, professional and clean"
- "Dynamic zoom out revealing full scene, energetic and uplifting mood"

**Bad Motion Prompts**:
- "Lots of cuts and fast movements" (too jarring)
- "Camera spinning wildly" (not suitable for social media)
- "Random effects" (lacks direction)

## ⏱️ Generation Time

Video generation takes **11 seconds to 6 minutes** depending on:
- Server load
- Prompt complexity
- Video length (8s is maximum)
- Resolution requested

**Typical Times**:
- Simple motion: 1-2 minutes
- Complex cinematography: 3-4 minutes
- High resolution: 4-6 minutes

## 🏗️ Architecture

```
video_generation_agent/
├── __init__.py           # Package exports
├── agent.py              # Video orchestrator agent
├── tools.py              # Veo 3 API integration
│   ├── generate_video_concept()       # Create motion prompt
│   ├── generate_video_from_image()    # Image-to-video (main)
│   └── generate_video_from_text()     # Text-to-video
└── schemas.py            # Input/output models
```

## 📊 API Workflow

```
1. Input: image_path + concept + topic + tone
   ↓
2. generate_video_concept()
   → Creates detailed motion/cinematography prompt
   ↓
3. generate_video_from_image()
   → Uploads image to Veo 3
   → Sends generation request
   → Returns operation handle
   ↓
4. Poll Operation (every 10s)
   → Check if operation.done
   → Max 60 polls (10 minutes timeout)
   ↓
5. Download Video
   → Get generated video from operation.response
   → Save to artifacts/generated_video_TIMESTAMP.mp4
   → Save to ADK artifacts for UI
   ↓
6. Output: video_path + metadata
```

## 🔧 Configuration

**Environment Variables**:
```bash
# Required
GOOGLE_API_KEY=your_api_key

# Optional (defaults shown)
VIDEO_MODEL=veo-3.0-generate-001
VIDEO_ASPECT_RATIO=9:16
VIDEO_DURATION=8
```

**Python Configuration**:
```python
# In video_generation_agent/tools.py

# Change default aspect ratio
aspect_ratio = "16:9"  # Horizontal instead of vertical

# Change default duration
duration = 5  # Shorter video (max 8 seconds)

# Change poll timeout
max_polls = 30  # 5 minutes max instead of 10
```

## ⚠️ Important Notes

### Video Retention
- **Videos are retained for only 2 days** on Veo API
- Always download immediately after generation
- Videos are automatically saved to local `artifacts/` directory

### Cost Considerations
- Veo 3 video generation incurs API costs
- Check [Google AI pricing](https://ai.google.dev/pricing) for current rates
- Each 8-second video = 1 generation request

### Generation Failures
Common causes:
- Prompt violates safety filters
- API rate limits exceeded
- Timeout (>10 minutes)
- Invalid image format
- Network connectivity issues

### File Size
- 8-second 1080p video: ~5-10 MB
- May need compression for some platforms
- X/Twitter supports videos up to 512 MB

## 🎯 Use Cases

### 1. Product Launches
Generate announcement videos from product images:
```python
# Image: Product hero shot
# Motion: Slow zoom revealing features
# Result: 8s product reveal video
```

### 2. Tutorial Snippets
Create educational content:
```python
# Image: Code screenshot or diagram
# Motion: Pan across with text overlays
# Result: 8s tutorial teaser
```

### 3. Behind-the-Scenes
Show process/workflow:
```python
# Image: Team workspace or tool interface
# Motion: Dynamic zoom with energetic mood
# Result: 8s BTS video
```

### 4. Trending Content
React to trends quickly:
```python
# Image: Trend visualization
# Motion: Fast-paced zoom with overlays
# Result: 8s trend reaction video
```

## 📝 Example Output

**Successful Generation**:
```json
{
  "status": "success",
  "video_path": "artifacts/generated_video_20251012_143022.mp4",
  "duration": 8,
  "aspect_ratio": "9:16",
  "motion_prompt": "Slow cinematic zoom in on AI agent visualization...",
  "generation_time": 127.3,
  "image_path": "artifacts/generated_image_20251012_142855.png"
}
```

**Failed Generation**:
```json
{
  "status": "failed",
  "reason": "Video generation timed out after 600s",
  "generation_time": 601.2
}
```

## 🔮 Future Enhancements

**Planned Features**:
1. **Dual Output Mode**: Generate both image (3:4) and video (9:16) simultaneously
2. **Text Overlays**: Add dynamic text/captions via Gemini
3. **Multi-Platform Export**: Support 16:9 (YouTube), 1:1 (Instagram Feed)
4. **Audio Integration**: Add background music or voiceover
5. **Batch Generation**: Create multiple video variations
6. **X Video Posting**: Direct upload to Twitter/X

## 🐛 Troubleshooting

### Video Generation Timeout
**Problem**: "Video generation timed out after 600s"

**Solutions**:
- Simplify the motion prompt
- Reduce video duration (if possible)
- Try during off-peak hours
- Check API status page

### No Video Generated
**Problem**: "No video generated in response"

**Solutions**:
- Verify prompt doesn't violate safety filters
- Check image format is supported (PNG, JPEG)
- Ensure image size is reasonable (<10 MB)
- Try text-to-video instead of image-to-video

### API Authentication Error
**Problem**: "401 Unauthorized" or "API key invalid"

**Solutions**:
- Verify GOOGLE_API_KEY in .env file
- Check API key has Veo 3 access enabled
- Regenerate API key if expired
- Check API quotas/limits

### Generation Quality Issues
**Problem**: Video quality is poor or doesn't match expectations

**Solutions**:
- Improve motion prompt with more detail
- Use higher quality source image
- Specify cinematography style (cinematic, professional)
- Add mood descriptors (uplifting, dramatic, calm)

## 📞 Support

For issues or questions:
1. Check [Google Gemini API docs](https://ai.google.dev/gemini-api/docs/video)
2. Review Veo 3 [best practices](https://ai.google.dev/gemini-api/docs/video)
3. See example scripts in `examples/`
4. Check project README.md

## 🎓 Learn More

- [Google Veo 3 Documentation](https://ai.google.dev/gemini-api/docs/video)
- [Prompt Engineering for Video](https://ai.google.dev/gemini-api/docs/video#prompting)
- [Video API Reference](https://ai.google.dev/api/generate-videos)
