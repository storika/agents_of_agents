"""
Video Generation Test - Generate short-form video from existing image

This example demonstrates:
1. Loading an existing generated image
2. Creating a motion/cinematography concept
3. Generating an 8-second vertical video (9:16) using Veo 3
4. Saving the video to artifacts/

Usage:
    python examples/video_generation_test.py
    python examples/video_generation_test.py --image artifacts/generated_image_20251011_220355.png
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from post_agent.sub_agents import generate_video_concept
from post_agent.tools import generate_video_from_image


def main():
    """
    Test video generation from existing image
    """

    print("=" * 80)
    print("Video Generation Test - Veo 3 Image-to-Video")
    print("=" * 80)
    print()

    # Find the most recent generated image
    artifacts_dir = Path("artifacts")

    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Find most recent generated image
        image_files = sorted(artifacts_dir.glob("generated_image_*.png"), reverse=True)

        if not image_files:
            print("❌ No generated images found in artifacts/")
            print()
            print("Please run the CMO agent first to generate an image:")
            print("  python examples/cmo_with_x_posting.py")
            print()
            print("Or specify an image path:")
            print("  python examples/video_generation_test.py artifacts/your_image.png")
            return

        image_path = str(image_files[0])

    print(f"📸 Using image: {image_path}")
    print()

    # Check if image exists
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return

    # Define video generation parameters
    topic = "AI Agents"
    tone = "engaging"
    concept = "Visual representation of AI agents and automation, modern tech aesthetic with vibrant colors"

    print("🎬 Video Generation Parameters:")
    print(f"  Topic: {topic}")
    print(f"  Tone: {tone}")
    print(f"  Duration: 8 seconds")
    print(f"  Aspect Ratio: 9:16 (vertical)")
    print()
    print("=" * 80)
    print()

    # Step 1: Generate video concept
    print("📝 Step 1: Generating motion/cinematography concept...")
    print()

    concept_result = generate_video_concept(
        image_concept=concept,
        topic=topic,
        tone=tone
    )

    if concept_result['status'] != 'success':
        print(f"❌ Failed to generate video concept: {concept_result.get('reason', 'Unknown error')}")
        return

    motion_prompt = concept_result['motion_prompt']
    print(f"✅ Motion Prompt: {motion_prompt}")
    print()
    print("=" * 80)
    print()

    # Step 2: Generate video from image
    print("🎥 Step 2: Generating 8-second video with Veo 3...")
    print()
    print("⏱️  This may take 11 seconds to 6 minutes...")
    print("   (Typical: 1-3 minutes for 8-second video)")
    print()

    video_result = generate_video_from_image(
        image_path=image_path,
        motion_prompt=motion_prompt,
        aspect_ratio="9:16",
        duration=8
    )

    print()
    print("=" * 80)
    print()

    # Display results
    if video_result['status'] == 'success':
        print("✅ VIDEO GENERATION SUCCESSFUL!")
        print()
        print(f"📹 Video Path: {video_result['video_path']}")
        print(f"⏱️  Generation Time: {video_result['generation_time']:.1f}s")
        print(f"📐 Aspect Ratio: {video_result['aspect_ratio']}")
        print(f"⏱️  Duration: {video_result['duration']}s")
        print()
        print("🎬 Motion Prompt Used:")
        print(f"   {video_result['motion_prompt']}")
        print()
        print("=" * 80)
        print()
        print("📌 Next Steps:")
        print("  - View the video in artifacts/ directory")
        print("  - Use the video_path for social media posting")
        print("  - Integrate video generation into CMO agent workflow")
        print()
    else:
        print("❌ VIDEO GENERATION FAILED")
        print()
        print(f"Error: {video_result.get('reason', 'Unknown error')}")
        print(f"Generation Time: {video_result.get('generation_time', 0):.1f}s")
        print()
        print("=" * 80)
        print()
        print("💡 Troubleshooting:")
        print("  - Check that GOOGLE_API_KEY is set in .env")
        print("  - Verify Veo 3 API access is enabled")
        print("  - Try with a different image or simpler concept")
        print("  - Check generation time didn't timeout (>10 min)")
        print()


if __name__ == "__main__":
    main()
