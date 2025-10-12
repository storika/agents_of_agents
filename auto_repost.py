#!/usr/bin/env python3
"""
Auto-Repost Tool - Complete Workflow
Searches posts, selects one, generates LLM comment, and quote tweets
"""

import sys
from x_api_tools import auto_repost_workflow, print_workflow_result


def main():
    """Interactive auto-repost tool"""

    print("\n" + "🤖" * 30)
    print("AUTO-REPOST TOOL - X/Twitter")
    print("🤖" * 30)
    print("\nComplete workflow: search → pick → generate comment → repost\n")

    # Get search query
    print("="*60)
    default_query = "AI agents OR multi-agent systems"
    query = input(f"🔍 Search query [default: {default_query}]:\n> ").strip()
    if not query:
        query = default_query

    # Number of results
    max_results_input = input("\n📊 Max results to search? [default: 10]:\n> ").strip()
    try:
        max_results = int(max_results_input) if max_results_input else 10
        max_results = max(1, min(100, max_results))
    except:
        max_results = 10

    # Auto-select or manual
    auto_select_input = input("\n🎯 Auto-select top post by engagement? [Y/n]:\n> ").strip().lower()
    auto_select = auto_select_input != 'n'

    # Comment length
    comment_length_input = input("\n📏 Max comment length? [default: 200]:\n> ").strip()
    try:
        comment_length = int(comment_length_input) if comment_length_input else 200
        comment_length = max(50, min(280, comment_length))
    except:
        comment_length = 200

    # Dry run
    dry_run_input = input("\n⚠️  Dry run mode (don't actually post)? [Y/n]:\n> ").strip().lower()
    dry_run = dry_run_input != 'n'

    # Run workflow
    print("\n" + "="*60)
    print("⚙️  Starting workflow...")
    print("="*60)

    result = auto_repost_workflow(
        query=query,
        max_search_results=max_results,
        auto_select=auto_select,
        comment_max_length=comment_length,
        dry_run=dry_run
    )

    # Print results
    print_workflow_result(result)

    # Next steps
    if result["status"] == "success":
        if dry_run:
            print("\n💡 Next Steps:")
            print("   1. Review the generated comment above")
            print("   2. Run again with dry_run=False to actually post")
            print("   3. Or manually copy the comment and post on X")
        else:
            print("\n✅ Posted! Check your X profile to see the quote tweet")

        # Save option
        save = input("\n💾 Save workflow results to JSON? [y/N]: ").strip().lower()
        if save == 'y':
            import json
            from datetime import datetime

            filename = f"auto_repost_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"✅ Saved to {filename}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
