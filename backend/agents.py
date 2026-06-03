"""
Agent Pipeline for BizGenie AI
7-step agentic workflow using Grok API with intelligent fallback
"""
import json
import re
import time
from typing import Dict, Any, Callable, Optional
from grok_client import call_grok


AGENT_STEPS = [
    "Analyzing Idea",
    "Market Research",
    "Competitor Analysis",
    "Business Model",
    "Financial Projections",
    "Marketing Strategy",
    "Finalizing Business Plan",
]

SYSTEM_BASE = """You are BizGenie AI, an expert business analyst and startup advisor.
You generate structured, data-driven, professional business plans.
Always respond with valid JSON only — no markdown fences, no explanation outside JSON.
Be specific with numbers, percentages, and real market data estimates."""


def extract_json(text: str) -> Dict[str, Any]:
    """Safely extract JSON from Grok response."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return {}


def _try_grok(system_prompt: str, user_prompt: str, temperature: float = 0.65):
    """Attempt Grok call; return (result_text, error_str)."""
    try:
        result = call_grok(system_prompt, user_prompt, temperature=temperature)
        return result, None
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────
# INTELLIGENT FALLBACK GENERATOR
# ─────────────────────────────────────────────
def _smart_plan(idea: str) -> Dict[str, Any]:
    """
    Generate a complete, keyword-aware business plan when the Grok API
    is unavailable (e.g. no credits). Parses the idea text for domain
    clues and injects them throughout the plan.
    """
    idea_lower = idea.lower()

    # ── Detect domain keywords ──
    domains = {
        "fitness": ["fitness", "workout", "gym", "health", "exercise", "nutrition", "wellness"],
        "edtech":  ["education", "learning", "course", "tutor", "school", "teach", "e-learning"],
        "fintech": ["finance", "payment", "bank", "invest", "crypto", "wallet", "money", "loan"],
        "ecommerce": ["shop", "store", "ecommerce", "marketplace", "retail", "product", "sell"],
        "saas":    ["saas", "software", "platform", "tool", "dashboard", "automation", "workflow"],
        "food":    ["food", "restaurant", "delivery", "recipe", "meal", "chef", "catering"],
        "travel":  ["travel", "hotel", "booking", "trip", "tourism", "flight", "vacation"],
        "healthcare": ["health", "medical", "doctor", "patient", "clinic", "therapy", "mental"],
        "ai":      ["ai", "machine learning", "ml", "nlp", "deep learning", "chatbot", "gpt"],
        "realestate": ["real estate", "property", "rent", "housing", "apartment", "mortgage"],
    }

    detected = "tech"
    for domain, kws in domains.items():
        if any(k in idea_lower for k in kws):
            detected = domain
            break

    # ── Domain-specific data ──
    domain_data = {
        "fitness": {
            "company": "FitAI Pro", "tagline": "Your AI Personal Trainer, Anytime Anywhere",
            "market_size": "$14.7B", "revenue": "$18.3M", "users": "1.2M+", "funding": "$2.5M",
            "industry": "Health & Fitness Tech", "cagr": "23.4",
            "competitors": ["MyFitnessPal", "Fitbit", "Nike Training Club"],
        },
        "edtech": {
            "company": "LearnSpark AI", "tagline": "Personalized Learning Powered by AI",
            "market_size": "$404B", "revenue": "$22.1M", "users": "2.5M+", "funding": "$3.5M",
            "industry": "EdTech", "cagr": "19.2",
            "competitors": ["Coursera", "Duolingo", "Khan Academy"],
        },
        "fintech": {
            "company": "FinGenius AI", "tagline": "Smart Finance for the Modern World",
            "market_size": "$340B", "revenue": "$31.5M", "users": "800K+", "funding": "$5.0M",
            "industry": "FinTech", "cagr": "26.1",
            "competitors": ["Robinhood", "Revolut", "Plaid"],
        },
        "ecommerce": {
            "company": "ShopSmart AI", "tagline": "AI-Driven Commerce, Reimagined",
            "market_size": "$6.3T", "revenue": "$45.0M", "users": "3.0M+", "funding": "$4.0M",
            "industry": "E-Commerce", "cagr": "14.7",
            "competitors": ["Shopify", "Amazon", "WooCommerce"],
        },
        "saas": {
            "company": "FlowBase AI", "tagline": "Automate Everything, Focus on What Matters",
            "market_size": "$232B", "revenue": "$15.2M", "users": "500K+", "funding": "$3.0M",
            "industry": "SaaS / Productivity", "cagr": "18.3",
            "competitors": ["Notion", "Monday.com", "Zapier"],
        },
        "food": {
            "company": "ChefBot AI", "tagline": "Restaurant-Quality Meals, Delivered by AI",
            "market_size": "$223B", "revenue": "$12.8M", "users": "900K+", "funding": "$2.0M",
            "industry": "Food Tech", "cagr": "12.6",
            "competitors": ["DoorDash", "Uber Eats", "HelloFresh"],
        },
        "travel": {
            "company": "WanderAI", "tagline": "Your Intelligent Travel Companion",
            "market_size": "$1.1T", "revenue": "$28.0M", "users": "1.8M+", "funding": "$4.5M",
            "industry": "Travel Tech", "cagr": "17.4",
            "competitors": ["Booking.com", "Airbnb", "TripAdvisor"],
        },
        "healthcare": {
            "company": "MedMind AI", "tagline": "AI-Powered Healthcare for Everyone",
            "market_size": "$659B", "revenue": "$19.5M", "users": "1.0M+", "funding": "$6.0M",
            "industry": "HealthTech", "cagr": "21.9",
            "competitors": ["Teladoc", "Hims & Hers", "Noom"],
        },
        "ai": {
            "company": "NeuralLaunch", "tagline": "Building the Intelligent Future, Today",
            "market_size": "$407B", "revenue": "$25.0M", "users": "600K+", "funding": "$5.5M",
            "industry": "Artificial Intelligence", "cagr": "36.2",
            "competitors": ["OpenAI", "Anthropic", "Cohere"],
        },
        "realestate": {
            "company": "PropGenius AI", "tagline": "Find Your Perfect Home with AI Precision",
            "market_size": "$3.7T", "revenue": "$16.8M", "users": "750K+", "funding": "$3.2M",
            "industry": "PropTech", "cagr": "15.8",
            "competitors": ["Zillow", "Redfin", "Opendoor"],
        },
        "tech": {
            "company": "TechVision AI", "tagline": "Intelligent Solutions for Tomorrow's Challenges",
            "market_size": "$150B", "revenue": "$15.0M", "users": "800K+", "funding": "$3.0M",
            "industry": "Technology", "cagr": "20.5",
            "competitors": ["Competitor A", "Competitor B", "Competitor C"],
        },
    }

    d = domain_data.get(detected, domain_data["tech"])
    comp = d["competitors"]
    cname = d["company"]

    # Truncate idea for display
    idea_short = idea[:120] + "..." if len(idea) > 120 else idea

    plan = {
        "executive_summary": {
            "company_name": cname,
            "tagline": d["tagline"],
            "description": (
                f"{cname} is an AI-powered solution that {idea_short} "
                f"Our mission is to make {detected} smarter, simpler, and more effective using artificial intelligence."
            ),
            "market_size": d["market_size"],
            "revenue_projection": d["revenue"],
            "users_projection": d["users"],
            "funding_required": d["funding"],
            "year": "2028",
            "industry": d["industry"],
            "stage": "Seed",
        },
        "problem_statement": (
            f"People struggle with fragmented, generic {detected} solutions that don't adapt to their "
            f"individual needs. Current tools lack personalization, real-time insights, and intelligent "
            f"automation — leaving users frustrated and underserved."
        ),
        "solution": (
            f"{cname} uses cutting-edge AI and machine learning to deliver a fully personalized "
            f"{detected} experience. Our platform adapts in real-time, providing actionable insights, "
            f"intelligent recommendations, and seamless automation to maximize user outcomes."
        ),
        "market_opportunity": [
            f"Global {d['industry']} market growing at {d['cagr']}% CAGR",
            f"Market size expected to reach {d['market_size']} by 2028",
            "Rising demand for AI-powered personalization",
            "Mobile-first users driving digital adoption",
            "Underserved SMB and consumer segments",
        ],
        "target_audience": [
            "Age Group: 18–45 years",
            f"{d['industry']} enthusiasts and professionals",
            "Tech-savvy early adopters",
            "Location: Global",
            "Income Group: $30K – $150K",
        ],
        "business_model": {
            "revenue_streams": [
                "Freemium Model",
                "Free Plan: Basic features",
                "Premium Plan: $9.99/month",
                "Enterprise Plan: $49/month per seat",
                "In-app purchases & API partnerships",
            ],
            "premium_percentage": 70,
            "free_percentage": 30,
            "key_activities": ["Product R&D", "User Acquisition", "Partnership Development"],
            "key_resources": ["AI Models", "Engineering Team", "Brand & Community"],
            "cost_structure": ["Cloud Infrastructure", "Engineering Salaries", "Marketing & Sales"],
        },
        "competitor_analysis": [
            {"name": comp[0], "strengths": "Large user base, brand recognition", "weaknesses": "Generic features, no AI personalization"},
            {"name": comp[1], "strengths": "Strong hardware integration", "weaknesses": "Limited software flexibility"},
            {"name": comp[2] if len(comp) > 2 else "Others", "strengths": "Brand trust", "weaknesses": "No real-time adaptation"},
            {"name": f"{cname} (Our Advantage)", "strengths": "AI personalization, all-in-one platform, real-time insights", "weaknesses": "New entrant, building brand trust"},
        ],
        "competitive_advantage": (
            f"{cname} uniquely combines deep AI personalization with a seamless UX, "
            f"offering features no competitor currently provides — all in one platform."
        ),
        "marketing_strategy": [
            "Influencer partnerships & micro-influencer campaigns",
            "Social media content marketing (Instagram, TikTok, YouTube)",
            "Content marketing: Blog, podcast, and YouTube SEO",
            "Referral & loyalty reward programs",
            "App Store Optimization (ASO) & Google UAC",
        ],
        "channels": ["Instagram", "YouTube", "Twitter/X", "TikTok", "LinkedIn"],
        "swot": {
            "strengths": ["AI personalization", "All-in-one solution", "User-friendly UX", "Real-time insights"],
            "weaknesses": ["New brand", "High CAC initially", "Limited initial feature set"],
            "opportunities": [f"Growing {detected} market", "Wearable & API integrations", "Enterprise expansion", "Global markets"],
            "threats": ["Established competitors", "Data privacy regulations", "Market saturation", "Economic downturn"],
        },
        "financials": {
            "projections": [
                {"year": "2024", "revenue": "$0.3M", "expenses": "$0.8M", "profit": "-$0.5M"},
                {"year": "2025", "revenue": "$3.6M", "expenses": "$2.1M", "profit": "$1.5M"},
                {"year": "2026", "revenue": "$7.8M", "expenses": "$3.5M", "profit": "$4.3M"},
                {"year": "2027", "revenue": "$13.2M", "expenses": "$4.8M", "profit": "$8.4M"},
                {"year": "2028", "revenue": d["revenue"], "expenses": "$5.5M", "profit": "$12.8M"},
            ],
            "funding_details": {
                "amount": d["funding"],
                "type": "Seed Funding",
                "allocation": {
                    "Product Development": 45,
                    "Marketing": 30,
                    "Team Hiring": 20,
                    "Operations": 10,
                },
            },
            "break_even": "Q3 2025",
            "runway_months": 18,
        },
        "milestones": [
            {"quarter": "Q1 2024", "milestone": "MVP Development & Internal Testing"},
            {"quarter": "Q2 2024", "milestone": "Beta Launch – 1,000 Early Users"},
            {"quarter": "Q3 2024", "milestone": "Official Public Launch"},
            {"quarter": "Q4 2024", "milestone": "10K Active Users"},
            {"quarter": "Q2 2025", "milestone": "100K+ Active Users"},
            {"quarter": "Q4 2025", "milestone": "Break-even Achieved"},
            {"quarter": "Q2 2026", "milestone": "Series A – $10M Raise"},
            {"quarter": "Q4 2027", "milestone": "Global Expansion & Enterprise Tier"},
        ],
        "conclusion": (
            f"{cname} is positioned to revolutionize the {d['industry']} industry by combining "
            f"cutting-edge AI with an intuitive, all-in-one platform. With a strong market opportunity, "
            f"proven business model, and a passionate team, we are poised for exponential growth and "
            f"long-term global impact."
        ),
    }
    return plan


# ─────────────────────────────────────────────
# STEP FUNCTIONS (Grok with smart fallback)
# ─────────────────────────────────────────────
def step_analyze_idea(idea: str, fallback_plan: Dict) -> Dict[str, Any]:
    prompt = f"""Analyze this business idea and return a JSON executive summary:

Business Idea: {idea}

Return ONLY this JSON structure:
{{
  "company_name": "Creative startup name",
  "tagline": "Short compelling tagline",
  "description": "2-3 sentence company description",
  "market_size": "$XX.XB",
  "revenue_projection": "$XX.XM",
  "users_projection": "X.XM+",
  "funding_required": "$X.XM",
  "year": "2028",
  "industry": "Industry name",
  "stage": "Seed/Series A/etc"
}}"""
    text, err = _try_grok(SYSTEM_BASE, prompt, temperature=0.6)
    if text:
        result = extract_json(text)
        if result:
            return result
    return fallback_plan["executive_summary"]


def step_market_research(idea: str, context: Dict, fallback_plan: Dict) -> Dict[str, Any]:
    prompt = f"""Based on this business idea, provide market research:

Business Idea: {idea}
Company: {context.get('company_name', 'the startup')}
Industry: {context.get('industry', 'tech')}

Return ONLY this JSON:
{{
  "problem_statement": "Clear 2-3 sentence problem description",
  "solution": "Clear 2-3 sentence solution description",
  "market_opportunity": [
    "Market is growing at XX% CAGR",
    "Market size expected to reach $XB by 20XX",
    "Key driver 1",
    "Key driver 2",
    "Key driver 3"
  ],
  "target_audience": [
    "Age Group: XX-XX years",
    "Demographic 1",
    "Demographic 2",
    "Location: Global/Regional",
    "Income Group: $XX - $XXK"
  ]
}}"""
    text, err = _try_grok(SYSTEM_BASE, prompt, temperature=0.65)
    if text:
        result = extract_json(text)
        if result:
            return result
    return {
        "problem_statement": fallback_plan["problem_statement"],
        "solution": fallback_plan["solution"],
        "market_opportunity": fallback_plan["market_opportunity"],
        "target_audience": fallback_plan["target_audience"],
    }


def step_competitor_analysis(idea: str, context: Dict, fallback_plan: Dict) -> Dict[str, Any]:
    prompt = f"""Perform competitor analysis for:

Business Idea: {idea}
Company: {context.get('company_name', 'Our Company')}

Return ONLY this JSON:
{{
  "competitors": [
    {{"name": "Competitor1", "strengths": "Key strength", "weaknesses": "Key weakness"}},
    {{"name": "Competitor2", "strengths": "Key strength", "weaknesses": "Key weakness"}},
    {{"name": "Competitor3", "strengths": "Key strength", "weaknesses": "Key weakness"}},
    {{"name": "{context.get('company_name', 'Us')} (Our Advantage)", "strengths": "AI personalization, real-time adaptation, all-in-one", "weaknesses": "New entrant, building brand"}}
  ],
  "competitive_advantage": "Our unique value proposition in 1-2 sentences"
}}"""
    text, err = _try_grok(SYSTEM_BASE, prompt, temperature=0.65)
    if text:
        result = extract_json(text)
        if result:
            return result
    return {
        "competitors": fallback_plan["competitor_analysis"],
        "competitive_advantage": fallback_plan["competitive_advantage"],
    }


def step_business_model(idea: str, context: Dict, fallback_plan: Dict) -> Dict[str, Any]:
    prompt = f"""Design the business model for:

Business Idea: {idea}
Company: {context.get('company_name', 'the startup')}

Return ONLY this JSON:
{{
  "revenue_streams": [
    "Freemium Model",
    "Free Plan: Basic features",
    "Premium Plan: $X.XX/month",
    "Enterprise Plan: $XX/month",
    "Additional stream"
  ],
  "premium_percentage": 70,
  "free_percentage": 30,
  "key_activities": ["Activity 1", "Activity 2", "Activity 3"],
  "key_resources": ["Resource 1", "Resource 2", "Resource 3"],
  "cost_structure": ["Cost 1", "Cost 2", "Cost 3"]
}}"""
    text, err = _try_grok(SYSTEM_BASE, prompt, temperature=0.6)
    if text:
        result = extract_json(text)
        if result:
            return result
    return fallback_plan["business_model"]


def step_financial_projections(idea: str, context: Dict, fallback_plan: Dict) -> Dict[str, Any]:
    prompt = f"""Create 5-year financial projections for:

Business Idea: {idea}
Company: {context.get('company_name', 'the startup')}
Funding: {context.get('funding_required', '$2.5M')}

Return ONLY this JSON:
{{
  "projections": [
    {{"year": "2024", "revenue": "$0.3M", "expenses": "$0.4M", "profit": "-$0.1M"}},
    {{"year": "2025", "revenue": "$2.1M", "expenses": "$1.6M", "profit": "$0.5M"}},
    {{"year": "2026", "revenue": "$6.8M", "expenses": "$3.2M", "profit": "$3.6M"}},
    {{"year": "2027", "revenue": "$12.5M", "expenses": "$4.0M", "profit": "$8.5M"}},
    {{"year": "2028", "revenue": "$18.3M", "expenses": "$5.5M", "profit": "$12.8M"}}
  ],
  "funding_details": {{
    "amount": "$2.5M",
    "type": "Seed Funding",
    "allocation": {{
      "Product Development": 45,
      "Marketing": 30,
      "Team Hiring": 20,
      "Operations": 10
    }}
  }},
  "break_even": "Q4 2025",
  "runway_months": 18
}}"""
    text, err = _try_grok(SYSTEM_BASE, prompt, temperature=0.55)
    if text:
        result = extract_json(text)
        if result:
            return result
    return fallback_plan["financials"]


def step_marketing_strategy(idea: str, context: Dict, fallback_plan: Dict) -> Dict[str, Any]:
    prompt = f"""Create marketing strategy for:

Business Idea: {idea}
Company: {context.get('company_name', 'the startup')}
Target Audience: {context.get('target_audience', [])}

Return ONLY this JSON:
{{
  "strategies": [
    "Influencer partnerships",
    "Social media campaigns",
    "Content marketing (Blog, YouTube)",
    "Referral & reward programs",
    "App store optimization (ASO)"
  ],
  "channels": ["Instagram", "YouTube", "Twitter/X", "TikTok", "LinkedIn"],
  "swot": {{
    "strengths": ["Strength 1", "Strength 2", "Strength 3", "Strength 4"],
    "weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],
    "opportunities": ["Opportunity 1", "Opportunity 2", "Opportunity 3", "Opportunity 4"],
    "threats": ["Threat 1", "Threat 2", "Threat 3", "Threat 4"]
  }}
}}"""
    text, err = _try_grok(SYSTEM_BASE, prompt, temperature=0.65)
    if text:
        result = extract_json(text)
        if result:
            return result
    return {
        "strategies": fallback_plan["marketing_strategy"],
        "channels": fallback_plan["channels"],
        "swot": fallback_plan["swot"],
    }


def step_finalize_plan(idea: str, context: Dict, fallback_plan: Dict) -> Dict[str, Any]:
    prompt = f"""Create the final milestone roadmap and conclusion for:

Business Idea: {idea}
Company: {context.get('company_name', 'the startup')}

Return ONLY this JSON:
{{
  "milestones": [
    {{"quarter": "Q1 2024", "milestone": "MVP Development"}},
    {{"quarter": "Q2 2024", "milestone": "Beta Launch"}},
    {{"quarter": "Q3 2024", "milestone": "Official Launch"}},
    {{"quarter": "Q4 2025", "milestone": "100K+ Active Users"}},
    {{"quarter": "Q2 2026", "milestone": "Break-even"}},
    {{"quarter": "Q1 2027", "milestone": "Series A Funding"}},
    {{"quarter": "Q4 2027", "milestone": "Global Expansion"}}
  ],
  "conclusion": "2-3 sentence powerful conclusion about the company's vision and potential"
}}"""
    text, err = _try_grok(SYSTEM_BASE, prompt, temperature=0.7)
    if text:
        result = extract_json(text)
        if result:
            return result
    return {
        "milestones": fallback_plan["milestones"],
        "conclusion": fallback_plan["conclusion"],
    }


# ─────────────────────────────────────────────
# MASTER PIPELINE
# ─────────────────────────────────────────────
def run_agent_pipeline(
    idea: str,
    progress_callback: Optional[Callable[[str, str, Any], None]] = None
) -> Dict[str, Any]:
    """
    Run all 7 agent steps sequentially.
    Falls back to intelligent keyword-based generation if Grok API is unavailable.
    """
    # Pre-build fallback plan from keyword analysis
    fallback = _smart_plan(idea)

    plan = {}
    context = {}

    def notify(step: str, status: str, data: Any = None):
        if progress_callback:
            progress_callback(step, status, data)

    # Step 1
    notify("Analyzing Idea", "running")
    exec_summary = step_analyze_idea(idea, fallback)
    context.update(exec_summary)
    plan["executive_summary"] = exec_summary
    notify("Analyzing Idea", "completed", exec_summary)

    # Step 2
    notify("Market Research", "running")
    market = step_market_research(idea, context, fallback)
    plan.update(market)
    notify("Market Research", "completed", market)

    # Step 3
    notify("Competitor Analysis", "running")
    competitors = step_competitor_analysis(idea, context, fallback)
    plan["competitor_analysis"] = competitors.get("competitors", [])
    plan["competitive_advantage"] = competitors.get("competitive_advantage", "")
    notify("Competitor Analysis", "completed", competitors)

    # Step 4
    notify("Business Model", "running")
    biz_model = step_business_model(idea, context, fallback)
    plan["business_model"] = biz_model
    notify("Business Model", "completed", biz_model)

    # Step 5
    notify("Financial Projections", "running")
    financials = step_financial_projections(idea, context, fallback)
    plan["financials"] = financials
    notify("Financial Projections", "completed", financials)

    # Step 6
    notify("Marketing Strategy", "running")
    marketing = step_marketing_strategy(idea, context, fallback)
    plan["marketing_strategy"] = marketing.get("strategies", [])
    plan["channels"] = marketing.get("channels", [])
    plan["swot"] = marketing.get("swot", {})
    notify("Marketing Strategy", "completed", marketing)

    # Step 7
    notify("Finalizing Business Plan", "running")
    final = step_finalize_plan(idea, context, fallback)
    plan["milestones"] = final.get("milestones", [])
    plan["conclusion"] = final.get("conclusion", "")
    notify("Finalizing Business Plan", "completed", final)

    return plan
