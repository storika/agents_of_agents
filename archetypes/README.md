# Agent Archetypes

Pre-defined agent role templates for the HR Director to build consistent, well-defined teams.

## Purpose

**Problem**: Creating agents from scratch leads to inconsistent prompts, tool assignments, and behaviors.

**Solution**: Pre-defined archetypes provide consistent templates. HR Director picks archetypes instead of inventing new agents.

## Structure

```
archetypes/
├── index.json                 # Registry + common team patterns
├── orchestrators.json         # Team lead archetypes (3 types)
├── content_creation.json      # Content specialist archetypes (4 types)
├── intelligence.json          # Analysis specialist archetypes (3 types)
├── quality_safety.json        # Validation specialist archetypes (3 types)
└── engagement.json            # Community specialist archetypes (2 types)
```

**Total**: 15 archetype definitions across 5 categories

## Archetype Format

Each archetype follows this simplified schema:

```json
{
  "name": "TrendResearcher",
  "version": "1.0.0",
  "role": "content.researcher",
  "objective": "One-line purpose statement",
  "system_prompt": "Concise prompt with {template_variables}. Rules: (1) Rule 1. (2) Rule 2.",
  "io": {
    "inputs": ["input1", "input2"],
    "outputs": ["output1", "output2"]
  },
  "tool_bindings": ["tool_1", "tool_2", "weave_log"]
}
```

## Archetypes by Category

### Orchestrators (Team Leads)
**1 required per team** - Coordinates sub-agents, makes final decisions

- **ContentTeamLead**: Fast content creation workflow (3 rounds, 15min)
- **CampaignManager**: Multi-day campaigns with narrative coherence
- **CommunityTeamLead**: Engagement and relationship-building coordination

### Content Creation
**1-3 per team** - Researches, creates, and optimizes content

- **TrendResearcher**: Identifies viral trends and timing opportunities
- **ViralCopywriter**: Creates 2-3 high-engagement copy variations
- **ThreadWriter**: Structures long-form educational threads (7-12 tweets)
- **MemeCreator**: Adapts trending meme formats to brand context

### Intelligence
**0-2 per team** - Provides data-driven insights

- **PerformanceAnalyst**: Monitors metrics and optimization insights
- **AudienceResearcher**: Analyzes follower data for content alignment
- **CompetitorAnalyst**: Tracks competitor strategies and gaps

### Quality & Safety
**1-2 per team** - Validates brand safety and quality

- **BrandSafetyValidator**: Pre-publish risk assessment (approve/revise/reject)
- **FactChecker**: Verifies claims and statistics (<3min)
- **CrisisManager**: Monitors sentiment and coordinates crisis response

### Engagement
**0-2 per team** - Handles community interactions

- **CommunityManager**: Reply management and authentic relationship building
- **InfluencerOutreach**: Identifies and coordinates influencer partnerships
```

## Common Team Patterns

Pre-configured team templates in `index.json` > `commonTeamPatterns`:

1. **trend_focused_team**: TrendResearcher + ViralCopywriter + BrandSafetyValidator
2. **meme_focused_team**: MemeCreator + ViralCopywriter + BrandSafetyValidator
3. **thread_focused_team**: ThreadWriter + FactChecker + BrandSafetyValidator
4. **data_driven_team**: PerformanceAnalyst + ViralCopywriter + BrandSafetyValidator
5. **community_building_team**: CommunityManager + AudienceResearcher + BrandSafetyValidator
6. **influencer_partnership_team**: InfluencerOutreach + AudienceResearcher + BrandSafetyValidator
7. **campaign_launch_team**: TrendResearcher + ViralCopywriter + PerformanceAnalyst + BrandSafetyValidator

## HR Director Usage

### 1. Load Archetypes
```python
import json

# Load all archetype definitions
orchestrators = json.load(open("archetypes/orchestrators.json"))
content_creators = json.load(open("archetypes/content_creation.json"))
intelligence = json.load(open("archetypes/intelligence.json"))
quality_safety = json.load(open("archetypes/quality_safety.json"))
engagement = json.load(open("archetypes/engagement.json"))

all_archetypes = {
    archetype["name"]: archetype
    for category in [orchestrators, content_creators, intelligence, quality_safety, engagement]
    for archetype in category
}
```

### 2. Select Team Pattern
```python
# Load common patterns
patterns = json.load(open("archetypes/index.json"))["commonTeamPatterns"]

# Choose based on owner profile
if owner_profile["goals"]["primary"] == "virality":
    team_template = patterns["trend_focused_team"]
elif owner_profile["brandVoice"]["tone"] == "humorous":
    team_template = patterns["meme_focused_team"]
```

### 3. Customize with Owner Context
```python
def fill_archetype_variables(archetype, owner_profile):
    prompt = archetype["system_prompt"]

    # Fill template variables
    variables = {
        "handle": owner_profile.get("xHandle", "@YourHandle"),
        "brand_tone": owner_profile.get("brandVoice", {}).get("tone", "professional"),
        "risk_tolerance": owner_profile.get("brandVoice", {}).get("riskTolerance", "moderate"),
        "topics_to_avoid": ", ".join(owner_profile.get("constraints", {}).get("topicsToAvoid", [])),
        "target_audience": owner_profile.get("targetAudience", {}).get("description", "general"),
        "brand_focus": owner_profile.get("accountFocus", "general topics")
    }

    for var, value in variables.items():
        prompt = prompt.replace(f"{{{var}}}", str(value))

    return {
        **archetype,
        "system_prompt": prompt,
        "customizations": variables
    }
```

### 4. Output for Agent Builder
```json
{
  "teamId": "team_a",
  "strategy": "trend_focused",
  "slotAssignments": [
    {
      "slotId": "team_a_slot_1",
      "archetypeName": "ContentTeamLead",
      "systemPrompt": "You are ContentTeamLead for @YourHandle...",
      "toolBindings": ["x_api_post", "x_api_reply", "weave_log"]
    },
    {
      "slotId": "team_a_slot_2",
      "archetypeName": "TrendResearcher",
      "systemPrompt": "You are TrendResearcher for @YourHandle...",
      "toolBindings": ["x_api_search", "trend_analyzer", "x_api_post", "x_api_reply", "weave_log"]
    }
  ]
}

## Agent Builder Usage

Agent Builder reads archetype files and:
1. Loads `systemPromptTemplate`
2. Replaces `{template_variables}` with customizations
3. Assigns `requiredTools` to the agent
4. Configures agent with personality and communication style

Example:
```python
# Agent Builder
def configure_agent_from_archetype(archetype_id, customizations, slot_config):
    # Load archetype
    archetype = load_archetype(archetype_id)

    # Fill template variables
    system_prompt = archetype["systemPromptTemplate"]
    for var, value in customizations.items():
        system_prompt = system_prompt.replace(f"{{{var}}}", value)

    # Create agent config
    return Agent(
        model="gemini-2.0-flash-exp",
        name=f"{slot_config['slotId']}_{archetype_id}",
        instructions=system_prompt,
        tools=[tool_registry[tool] for tool in archetype["requiredTools"]]
    )
```

## Benefits

1. **Consistency**: Same archetype = same behavior across teams
2. **Predictability**: Agent Builder knows exactly what to configure
3. **Testability**: Test archetypes independently
4. **Reusability**: HR Director can reuse proven patterns
5. **Maintainability**: Update archetype once, affects all instances
6. **Documentation**: Clear descriptions of each role

## Adding New Archetypes

To add a new archetype:
1. Create JSON file in appropriate category folder
2. Follow the schema structure
3. Add entry to `index.json` > `archetypeFiles`
4. (Optional) Create common team pattern using the archetype
5. Update this README if needed

## Template Variables

Common template variables across archetypes:
- `{brand_tone}`: casual, professional, edgy, humorous
- `{brand_style}`: conversational, authoritative, playful
- `{risk_tolerance}`: conservative, moderate, bold
- `{topics_to_avoid}`: List of sensitive topics
- `{brand_guidelines}`: Brand safety requirements
- `{target_audience}`: Audience description
- `{brand_focus}`: Primary brand focus area

## Integration Points

### HR Director → Archetypes
- Reads `index.json` for available archetypes
- Uses `commonTeamPatterns` as templates
- Selects archetype IDs based on owner profile
- Fills in template variables from owner data

### Agent Builder → Archetypes
- Receives archetype IDs from HR Director
- Loads archetype JSON files
- Instantiates agent configs with filled templates
- Assigns tools from archetype definitions

### Performance Tracking → HR Director → Archetypes
- HR Director tracks which archetypes/patterns perform best
- Can switch archetypes on same slot when strategy changes
- Example: `trend_researcher` → `meme_creator` on same slot
