"""Structured output schema for the research agent."""
from pydantic import BaseModel, Field


class ResearchResponse(BaseModel):
    topic: str = Field(description="The core topic or query researched.")
    summary: str = Field(
        description="A deep, synthesized summary of the findings (at least 3-4 sentences)."
    )
    key_findings: list[str] = Field(
        default_factory=list,
        description="Bullet-point list of the most important discrete facts or insights.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="URLs, publications, or named sources used during information gathering.",
    )
    tools_used: list[str] = Field(
        default_factory=list,
        description="List of tools that were invoked during the research process.",
    )
    confidence: str = Field(
        default="medium",
        description="Rough confidence level in the findings: 'low', 'medium', or 'high'.",
    )
