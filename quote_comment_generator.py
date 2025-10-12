"""
Repost Comment Generator - Standalone Tool
Generates engaging comments for quote tweets/reposts

This is the core comment generation (step 2) - assumes you have:
1. The original post data (manual for now)
3. Manual reposting (until X API integration)
"""

import os
import json
from dotenv import load_dotenv
import weave
from typing import Dict, List, Any, Optional

# Load environment
load_dotenv()

# Initialize Weave
WANDB_API_KEY = os.getenv("WANDB_API_KEY", "3875d64c87801e9a71318a5a8754a0ee2d556946")
os.environ['WANDB_API_KEY'] = WANDB_API_KEY

weave.init("mason-choi-storika/WeaveHacks2")
print("[INFO] 🐝 Weave initialized: mason-choi-storika/WeaveHacks2")

# Import Gemini for LLM generation
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_AI_STUDIO_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


def generate_repost_comments(
    original_post: str,
    author: str = "@unknown",
    context: Optional[str] = None,
    num_options: int = 5,
    max_length: int = 180
) -> Dict[str, Any]:
    """
    Generate engaging repost comments for a given post

    Args:
        original_post: The original post/tweet text to repost
        author: Author of the original post
        context: Additional context about the post or why it's trending (optional)
        num_options: Number of comment variations to generate (default: 5)
        max_length: Maximum character length for comments (default: 180)

    Returns:
        Dictionary with generated comments, scores, and recommendations
    """

    print(f"✍️ Generating {num_options} repost comments...")

    # Build system prompt
    system_prompt = """You are a repost comment generator for Twitter/X. Your job is to create engaging, authentic comments that add value to the original post.

AUDIENCE: AI/ML developers, indie hackers, founders, tech community
TONE: Conversational, witty-but-respectful, builder-friendly
STYLE: Authentic, adds perspective or insight

REPOST STRATEGIES (use diverse mix):
1. EXPERIENCE - Share personal/team experience related to the post
2. QUESTION - Ask thoughtful questions to spark discussion
3. ANALYSIS - Add technical insight or deeper analysis
4. CONTEXT - Provide broader context or connect to trends
5. REACTION - Express genuine reaction with added value
6. CONNECT - Link to related concepts or parallel insights

RULES:
- Each comment MUST be ≤{max_length} characters
- Add meaningful value - never just "This!" or "Great post!"
- Be specific and concrete, not generic
- Stay respectful - no mockery or misrepresentation
- Use natural language, avoid corporate speak
- Include specific details when sharing experience
- Emoji usage: 0-1 max, only if natural

OUTPUT FORMAT:
Generate {num_options} diverse comment options in JSON format:
{{
  "comments": [
    {{
      "comment": "Your comment text here",
      "strategy": "experience|question|analysis|context|reaction|connect",
      "reasoning": "Why this comment works and adds value",
      "character_count": 142,
      "specificity_score": 0.85,
      "engagement_score": 0.90,
      "authenticity_score": 0.88
    }}
  ]
}}

IMPORTANT:
- Use different strategies across the {num_options} options
- Be specific and concrete (mention tools, metrics, timeframes when relevant)
- Make comments that could stand alone even without seeing the original
- Focus on adding NEW information or perspective
"""

    # Build user prompt
    user_prompt = f"""Original Post by {author}:
"{original_post}"
"""

    if context:
        user_prompt += f"\nContext: {context}\n"

    user_prompt += f"""
Generate {num_options} diverse, engaging repost comments. Each must:
- Add unique value and perspective
- Be ≤{max_length} characters
- Use different strategies
- Be specific and authentic

Return ONLY valid JSON with the specified format."""

    try:
        # Call Gemini to generate comments
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        full_prompt = f"{system_prompt.format(max_length=max_length, num_options=num_options)}\n\n{user_prompt}"

        response = model.generate_content(full_prompt)
        response_text = response.text

        # Parse JSON from response
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "{" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_str = response_text[json_start:json_end]
        else:
            raise ValueError("No JSON found in response")

        result = json.loads(json_str)
        comments = result.get("comments", [])

        if not comments:
            raise ValueError("No comments generated")

        # Calculate overall scores and rank
        for comment in comments:
            specificity = comment.get("specificity_score", 0.8)
            engagement = comment.get("engagement_score", 0.8)
            authenticity = comment.get("authenticity_score", 0.8)

            # Overall = weighted average
            overall = (specificity * 0.30 + engagement * 0.40 + authenticity * 0.30)
            comment["overall_score"] = round(overall, 2)

        # Sort by overall score
        comments.sort(key=lambda x: x.get("overall_score", 0), reverse=True)

        # Select top recommendation
        top_comment = comments[0]

        output = {
            "status": "success",
            "original_post": {
                "text": original_post,
                "author": author,
                "context": context
            },
            "generated_comments": comments,
            "recommended": {
                "comment": top_comment["comment"],
                "strategy": top_comment["strategy"],
                "overall_score": top_comment["overall_score"],
                "character_count": top_comment["character_count"],
                "reasoning": top_comment["reasoning"]
            },
            "total_generated": len(comments)
        }

        print(f"✅ Generated {len(comments)} comments successfully")
        print(f"🏆 Top comment (score: {top_comment['overall_score']:.2f}):")
        print(f"   {top_comment['comment'][:80]}...")

        return output

    except Exception as e:
        print(f"❌ Error generating comments: {e}")
        import traceback
        traceback.print_exc()

        return {
            "status": "error",
            "error": str(e),
            "original_post": {
                "text": original_post,
                "author": author
            }
        }


def generate_single_comment(
    original_post: str,
    author: str = "@unknown",
    strategy: str = "auto",
    context: Optional[str] = None,
    max_length: int = 180
) -> str:
    """
    Generate a single repost comment with specified strategy

    Args:
        original_post: The original post text
        author: Post author
        strategy: Specific strategy to use (auto, experience, question, analysis, context, reaction, connect)
        context: Additional context (optional)
        max_length: Max character length

    Returns:
        The generated comment text
    """

    result = generate_repost_comments(
        original_post=original_post,
        author=author,
        context=context,
        num_options=3 if strategy == "auto" else 1,
        max_length=max_length
    )

    if result["status"] == "success":
        if strategy == "auto":
            return result["recommended"]["comment"]
        else:
            # Find comment with matching strategy
            for comment in result["generated_comments"]:
                if comment["strategy"] == strategy:
                    return comment["comment"]
            return result["recommended"]["comment"]
    else:
        return f"Error: {result.get('error', 'Unknown')}"


def print_comment_options(result: Dict[str, Any]) -> None:
    """Pretty print comment options"""
    if result["status"] != "success":
        print(f"❌ Error: {result.get('error', 'Unknown')}")
        return

    print("\n" + "="*70)
    print("📝 REPOST COMMENT OPTIONS")
    print("="*70)

    print(f"\nOriginal Post by {result['original_post']['author']}:")
    print(f"  \"{result['original_post']['text']}\"")

    if result['original_post'].get('context'):
        print(f"\nContext: {result['original_post']['context']}")

    print(f"\n🎯 RECOMMENDED (Score: {result['recommended']['overall_score']:.2f})")
    print(f"Strategy: {result['recommended']['strategy']}")
    print(f"Comment: {result['recommended']['comment']}")
    print(f"Length: {result['recommended']['character_count']}/280 chars")
    print(f"Why: {result['recommended']['reasoning']}")

    print(f"\n📋 ALL OPTIONS ({result['total_generated']} generated):\n")

    for i, comment in enumerate(result['generated_comments'], 1):
        print(f"{i}. [{comment['strategy'].upper()}] (Score: {comment['overall_score']:.2f})")
        print(f"   {comment['comment']}")
        print(f"   Length: {comment['character_count']} chars")
        print(f"   Why: {comment['reasoning']}")
        print()


def main():
    """Example usage"""
    print("\n" + "🚀" * 35)
    print("REPOST COMMENT GENERATOR")
    print("🚀" * 35)

    # Example 1: Generate comments for a trending post
    print("\n" + "="*70)
    print("EXAMPLE 1: AI/ML Technical Post")
    print("="*70)

    result1 = generate_repost_comments(
        original_post="Just shipped multi-agent systems in production. The debugging complexity is real but the velocity gains are insane. Going from 2 weeks to 2 days for new features.",
        author="@BuilderAI",
        context="Trending in AI/ML community, high engagement",
        num_options=5,
        max_length=180
    )

    print_comment_options(result1)

    # Example 2: Opinion piece
    print("\n" + "="*70)
    print("EXAMPLE 2: Opinion/Hot Take")
    print("="*70)

    result2 = generate_repost_comments(
        original_post="Unpopular opinion: Most teams don't need multi-agent systems. You're adding complexity before proving the single-agent case works. Start simple, scale when you have proof.",
        author="@CTOInsights",
        context="Controversial take, getting lots of discussion",
        num_options=5,
        max_length=180
    )

    print_comment_options(result2)

    # Example 3: Quick single comment generation
    print("\n" + "="*70)
    print("EXAMPLE 3: Quick Single Comment (Auto Strategy)")
    print("="*70)

    post = "The hardest part of AI agent development isn't the LLM - it's the orchestration layer, error handling, and non-deterministic debugging. Infrastructure is 80% of the work."

    comment = generate_single_comment(
        original_post=post,
        author="@DevOps",
        strategy="auto"
    )

    print(f"\nOriginal: {post[:80]}...")
    print(f"\nGenerated Comment:")
    print(f"  {comment}")

    print("\n" + "="*70)
    print("✅ EXAMPLES COMPLETED")
    print("="*70)
    print("\n💡 Usage Tips:")
    print("  1. Copy the 'Recommended' comment and manually repost")
    print("  2. Or choose from 'All Options' based on your preference")
    print("  3. All comments are ≤180 chars and add unique value")
    print("  4. Tracked in Weave for observability")
    print("\n📋 To use in your workflow:")
    print("  result = generate_repost_comments(original_post='...', author='@user')")
    print("  comment = result['recommended']['comment']")
    print("  # Then manually repost with this comment")


if __name__ == "__main__":
    main()
