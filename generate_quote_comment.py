#!/usr/bin/env python3
"""
Simple CLI for generating repost comments
Usage: python generate_repost_comment.py
"""

from repost_comment_generator import generate_repost_comments, print_comment_options


def main():
    """Interactive CLI for generating repost comments"""

    print("\n" + "🤖" * 30)
    print("REPOST COMMENT GENERATOR - Interactive Mode")
    print("🤖" * 30)
    print("\nThis tool generates engaging comments for quote tweets/reposts.")
    print("You'll manually repost until X API integration is complete.\n")

    # Get input
    print("="*60)
    print("Enter the original post details:")
    print("="*60)

    original_post = input("\n📝 Original post text:\n> ").strip()

    if not original_post:
        print("❌ Post text is required!")
        return

    author = input("\n👤 Author handle (e.g., @username) [default: @unknown]:\n> ").strip()
    if not author:
        author = "@unknown"

    context = input("\n📊 Context (why is this trending/interesting?) [optional]:\n> ").strip()
    if not context:
        context = None

    num_options_input = input("\n🔢 How many comment options to generate? [default: 5]:\n> ").strip()
    try:
        num_options = int(num_options_input) if num_options_input else 5
        num_options = max(1, min(10, num_options))  # Clamp between 1-10
    except:
        num_options = 5

    max_length_input = input("\n📏 Max comment length? [default: 180]:\n> ").strip()
    try:
        max_length = int(max_length_input) if max_length_input else 180
        max_length = max(50, min(280, max_length))  # Clamp between 50-280
    except:
        max_length = 180

    # Generate comments
    print("\n" + "="*60)
    print("⚙️  Generating comments...")
    print("="*60)

    result = generate_repost_comments(
        original_post=original_post,
        author=author,
        context=context,
        num_options=num_options,
        max_length=max_length
    )

    # Display results
    print_comment_options(result)

    if result["status"] == "success":
        # Copy-paste ready
        print("\n" + "="*60)
        print("📋 COPY-PASTE READY (Recommended Comment):")
        print("="*60)
        print(f"\n{result['recommended']['comment']}\n")

        print("="*60)
        print("✅ Next Steps:")
        print("="*60)
        print("1. Copy the comment above (or choose from options)")
        print("2. Go to X/Twitter and find the original post")
        print("3. Click 'Repost with quote'")
        print("4. Paste the comment")
        print("5. Post!")
        print("\n💡 Tip: All generated comments are logged in Weave for tracking")

        # Save to file option
        save = input("\n💾 Save results to JSON file? [y/N]: ").strip().lower()
        if save == 'y':
            import json
            from datetime import datetime

            filename = f"repost_comments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"✅ Saved to {filename}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
