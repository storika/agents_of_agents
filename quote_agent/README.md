# Repost Agent

A specialized AI agent for creating engaging quote tweets (reposts with comments) on Twitter/X.

## Overview

The Repost Agent helps you amplify great content on Twitter/X by creating thoughtful, engaging quote tweets that add value to the original tweet. It analyzes tweets, determines the best engagement strategy, and generates comments that spark conversation while maintaining your brand voice.

## Features

- **Smart Tweet Discovery**: Find trending tweets on any topic
- **Multiple Strategies**: 6 different repost strategies (experience, question, analysis, context, reaction, connect)
- **Intelligent Analysis**: Automatic strategy recommendation based on tweet content
- **Safety First**: Built-in safety checks and brand alignment
- **Weave Integration**: Full observability and tracking with Weave
- **Dry Run Mode**: Test before posting to production

## Installation

The Repost Agent is part of the agents_of_agents project. Make sure you have all dependencies installed:

```bash
# Install dependencies
pip install -r requirements.txt

# Or with uv
uv pip install -r requirements.txt
```

## Usage

### Quick Start

```python
from repost_agent.agent import create_quote_tweet

# Create a quote tweet for a specific tweet
result = create_quote_tweet(
    tweet_text="Just shipped multi-agent systems in production!",
    strategy="experience"
)

print(result['selected_comment']['comment'])
```

### Finding Trending Tweets

```python
from repost_agent.tools import find_trending_tweets_tool
import json

# Find trending tweets on a topic
result = find_trending_tweets_tool(topic="AI agents", max_results=5)
tweets = json.loads(result)

for tweet in tweets['tweets']:
    print(f"{tweet['author']}: {tweet['text']}")
```

### Generating Comments with Different Strategies

```python
from repost_agent.tools import generate_repost_comment_tool
import json

tweet_text = "Debugging AI agents at 2am is a special kind of pain"

# Generate comment with specific strategy
result = generate_repost_comment_tool(
    tweet_text=tweet_text,
    author="@Developer",
    strategy="experience"  # or "question", "analysis", "context", "reaction", "connect"
)

data = json.loads(result)
print(f"Best comment: {data['top_comment']['comment']}")
```

### Analyzing Tweets for Best Strategy

```python
from repost_agent.tools import analyze_tweet_for_repost
import json

result = analyze_tweet_for_repost(
    tweet_text="Unpopular opinion: most teams don't need multi-agent systems",
    author="@CTO"
)

analysis = json.loads(result)
print(f"Recommended strategy: {analysis['recommended_strategy']}")
print(f"Reasoning: {analysis['reasoning']}")
```

### Posting Quote Tweets

```python
from repost_agent.tools import post_quote_tweet_tool
import json

# Dry run (safe, won't actually post)
result = post_quote_tweet_tool(
    original_tweet_url="https://twitter.com/example/status/1234567890",
    comment="This is exactly what we're seeing in production. The coordination layer is critical.",
    dry_run=True
)

# Actual posting (requires Twitter API credentials)
result = post_quote_tweet_tool(
    original_tweet_url="https://twitter.com/example/status/1234567890",
    comment="This is exactly what we're seeing in production.",
    dry_run=False  # Set to False for actual posting
)
```

## Repost Strategies

The agent supports 6 different strategies for creating engaging comments:

### 1. Experience
Share your personal experience related to the original tweet.

**Example:**
> Original: "Just shipped a new AI feature in 2 hours using Claude"
>
> Comment: "This is exactly why we integrated Claude into our workflow. What used to take days now takes hours. The productivity gains are real. 🚀"

### 2. Question
Ask thoughtful questions to spark discussion.

**Example:**
> Original: "Multi-agent systems are the future of AI applications"
>
> Comment: "We're seeing this firsthand. The real challenge isn't building agents - it's making them work together reliably. Thoughts on coordination patterns?"

### 3. Analysis
Add technical insight or deeper analysis.

**Example:**
> Original: "AI agent debugging is complex"
>
> Comment: "The key insight: debugging complexity scales non-linearly. We started logging everything with observability tools - game changer for production AI."

### 4. Context
Provide broader context or background.

**Example:**
> Original: "Agent orchestration is getting popular"
>
> Comment: "Context: This is part of a broader trend. The shift from single-model to multi-agent architectures is accelerating faster than expected."

### 5. Reaction
Express genuine reaction with added value.

**Example:**
> Original: "Debugging production AI agents at 2am is painful"
>
> Comment: "This! The hardest part? Non-deterministic failures. We built an entire monitoring stack just to catch edge cases. Worth every hour."

### 6. Connect
Link to related concepts or trends.

**Example:**
> Original: "AI development velocity is increasing"
>
> Comment: "This connects to what we're seeing with agentic workflows. The composition of specialized agents is unlocking new capabilities we couldn't build before."

## Testing

Run the test suite to verify everything works:

```bash
python test_repost_agent.py
```

The test suite includes:
- Finding trending tweets
- Generating comments with different strategies
- Tweet analysis
- Full quote tweet creation workflow
- Direct agent calls
- URL parsing

## Architecture

```
repost_agent/
├── agent.py          # Main agent with LLM coordination
├── tools.py          # Tool functions (search, generate, post)
├── __init__.py       # Package exports
└── README.md         # This file

test_repost_agent.py  # Test suite
```

### Tools

1. **find_trending_tweets_tool**: Search for tweets on a topic
2. **generate_repost_comment_tool**: Generate engaging comments
3. **post_quote_tweet_tool**: Post the quote tweet
4. **analyze_tweet_for_repost**: Analyze and recommend strategy
5. **extract_tweet_id**: Parse tweet URLs

## Configuration

### Environment Variables

Required in your `.env` file:

```bash
# Weave (for observability)
WANDB_API_KEY=your_wandb_api_key

# Google AI (for LLM)
GOOGLE_AI_STUDIO_API_KEY=your_google_api_key

# Twitter API (for production posting) - Optional
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
```

## Best Practices

1. **Always Add Value**: Never just say "This!" or "Great post!" - add meaningful perspective
2. **Respect Original Authors**: No misrepresentation or mockery
3. **Test First**: Use dry_run=True before posting to production
4. **Choose Right Strategy**: Use analyze_tweet_for_repost for recommendations
5. **Stay on Brand**: Maintain consistent voice (builder-friendly, witty-but-respectful)
6. **Be Authentic**: Share genuine insights and experiences
7. **Engage After Posting**: Reply to comments on your quote tweets

## Safety & Compliance

The agent includes built-in safety features:

- ✅ No politics, harassment, or personal attacks
- ✅ No misrepresentation of original tweets
- ✅ Character limit validation (≤280 chars)
- ✅ URL validation
- ✅ Dry run mode by default
- ✅ Safety scoring for all generated comments

## Production Deployment

### Twitter API Integration

To enable actual posting to Twitter, you need to:

1. Apply for Twitter API access at [developer.twitter.com](https://developer.twitter.com)
2. Create a project and app
3. Get your API keys and tokens
4. Add them to your `.env` file
5. Update `post_quote_tweet_tool` in [tools.py](tools.py:171-236) with actual Twitter API calls using `tweepy` or similar library

Example integration:

```python
import tweepy

def post_quote_tweet_tool(original_tweet_url, comment, dry_run=False):
    if dry_run:
        # Return simulation
        pass

    # Production posting
    client = tweepy.Client(
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
    )

    tweet_id = extract_tweet_id(original_tweet_url)
    response = client.create_tweet(
        text=comment,
        quote_tweet_id=tweet_id
    )

    return response
```

## Observability

All agent actions are tracked with Weave:

- Tweet searches
- Comment generation
- Strategy selection
- Posting attempts
- Agent calls

View your runs at: [https://wandb.ai/mason-choi-storika/WeaveHacks2](https://wandb.ai/mason-choi-storika/WeaveHacks2)

## Examples

See [test_repost_agent.py](../test_repost_agent.py) for complete usage examples.

## Contributing

When extending the Repost Agent:

1. Add new strategies in `generate_repost_comment_tool`
2. Add new tools as needed
3. Update tests in `test_repost_agent.py`
4. Publish prompts to Weave for observability
5. Follow existing code patterns

## Troubleshooting

**Issue**: Agent returns raw response instead of JSON

**Solution**: The agent may need refinement. Check the response format and update parsing logic.

---

**Issue**: Twitter API errors

**Solution**: Verify your API credentials and ensure you have the right access levels.

---

**Issue**: Comments too long (>280 chars)

**Solution**: The agent should auto-truncate, but you can also specify max length in the strategy.

## License

Part of the agents_of_agents project.

## Support

For issues or questions, check the main project [README.md](../README.md) or create an issue in the repository.
