"""
Pydantic models for BizGenie AI
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class BusinessIdeaRequest(BaseModel):
    idea: str = Field(..., min_length=10, max_length=2000, description="Business idea description")
    plan_id: Optional[int] = None


class AgentStep(BaseModel):
    step_name: str
    status: str  # pending, running, completed, failed
    result: Optional[str] = None


class ExecutiveSummary(BaseModel):
    company_name: str
    tagline: str
    description: str
    market_size: str
    revenue_projection: str
    users_projection: str
    funding_required: str
    year: str = "2028"


class CompetitorItem(BaseModel):
    name: str
    strengths: str
    weaknesses: str


class FinancialRow(BaseModel):
    year: str
    revenue: str
    expenses: str
    profit: str


class MilestoneItem(BaseModel):
    quarter: str
    milestone: str


class BusinessPlanOutput(BaseModel):
    executive_summary: Optional[Dict[str, Any]] = None
    problem_statement: Optional[str] = None
    solution: Optional[str] = None
    market_opportunity: Optional[List[str]] = None
    target_audience: Optional[List[str]] = None
    business_model: Optional[List[str]] = None
    competitor_analysis: Optional[List[Dict[str, str]]] = None
    marketing_strategy: Optional[List[str]] = None
    swot_analysis: Optional[Dict[str, List[str]]] = None
    financial_projections: Optional[List[Dict[str, str]]] = None
    funding_requirements: Optional[Dict[str, Any]] = None
    milestone_roadmap: Optional[List[Dict[str, str]]] = None
    conclusion: Optional[str] = None


class PlanResponse(BaseModel):
    id: int
    title: str
    idea: str
    plan_data: Optional[Dict[str, Any]]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GeneratePlanResponse(BaseModel):
    plan_id: int
    message: str
    status: str
