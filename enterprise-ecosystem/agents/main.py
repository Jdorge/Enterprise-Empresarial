import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import structlog
from dotenv import load_dotenv
import openai
import anthropic

load_dotenv()

logger = structlog.get_logger()

app = FastAPI(title="MCP Orchestrator Service", version="1.0.0")


class InvokeRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to send to the AI provider")
    provider: str = Field(..., description="Provider name: 'openai' or 'anthropic'")
    model: Optional[str] = Field(None, description="Model name (optional, uses default if not provided)")


class InvokeResponse(BaseModel):
    provider: str
    model: str
    response: str


class HealthResponse(BaseModel):
    status: str
    service: str
    providers: dict


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    anthropic_configured = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    return {
        "status": "healthy",
        "service": "mcp-orchestrator",
        "providers": {
            "openai": "configured" if openai_configured else "not configured",
            "anthropic": "configured" if anthropic_configured else "not configured"
        }
    }


@app.post("/invoke", response_model=InvokeResponse)
async def invoke(request: InvokeRequest):
    """
    Invoke an AI provider with a prompt.
    
    Supports:
    - openai: Uses OpenAI API
    - anthropic: Uses Anthropic API
    """
    provider = request.provider.lower()
    
    try:
        if provider == "openai":
            return await invoke_openai(request)
        elif provider == "anthropic":
            return await invoke_anthropic(request)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown provider: {provider}. Supported providers: 'openai', 'anthropic'"
            )
    except Exception as e:
        logger.error("invoke_failed", provider=provider, error=str(e))
        raise HTTPException(status_code=500, detail=f"Provider invocation failed: {str(e)}")


async def invoke_openai(request: InvokeRequest) -> InvokeResponse:
    """Invoke OpenAI API"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    model = request.model or "gpt-4"
    client = openai.OpenAI(api_key=api_key)
    
    logger.info("invoking_openai", model=model)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": request.prompt}
        ]
    )
    
    content = response.choices[0].message.content
    
    logger.info("openai_success", model=model)
    
    return InvokeResponse(
        provider="openai",
        model=model,
        response=content
    )


async def invoke_anthropic(request: InvokeRequest) -> InvokeResponse:
    """Invoke Anthropic API"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
    
    model = request.model or "claude-3-5-sonnet-20241022"
    client = anthropic.Anthropic(api_key=api_key)
    
    logger.info("invoking_anthropic", model=model)
    
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": request.prompt}
        ]
    )
    
    content = response.content[0].text
    
    logger.info("anthropic_success", model=model)
    
    return InvokeResponse(
        provider="anthropic",
        model=model,
        response=content
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
