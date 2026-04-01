from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ErrorType(str, Enum):
    VALUE = "value_error"
    TYPE = "type_error"
    RUNTIME = "runtime_error"
    IMPORT = "import_error"
    ATTRIBUTE = "attribute_error"
    KEY = "key_error"
    INDEX = "index_error"


class ErrorCategory(str, Enum):
    RUNTIME = "runtime"
    LOGICAL = "logical"
    SYNTAX = "syntax"


class DocSource(str, Enum):
    NEXTJS = "nextjs"
    STACKOVERFLOW = "stackoverflow"
    GFG = "geeksforgeeks"


class CodeInput(BaseModel):
    code: str
    error: str
    behaviour: Optional[str] = None


class Context(BaseModel):
    language: str = Field(..., min_length=1)
    error_type: ErrorType


class BugAnalysis(BaseModel):
    root_cause: str                        
    error_category: ErrorCategory          
    responsible_lines: Optional[str] = None 
    summary: Optional[str] = None


class WebSearch(BaseModel):
    source: DocSource
    patterns: list[str] = []
    fixes: list[str] = []


class FixGenerator(BaseModel):
    correct_code: str
    explanation: str
    improvement_suggestions: Optional[str] = None


class Evaluation(BaseModel):
    validity: float = Field(..., ge=0.0, le=1.0)
    code_fix: float = Field(..., ge=0.0, le=1.0)
    regression_risk: float = Field(..., ge=0.0, le=1.0)
    score: float = Field(..., ge=0.0, le=1.0)
    feedback: str


class StrictBaseModel(BaseModel):
    class Config:
        extra = "forbid"