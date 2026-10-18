from enum import Enum

class AnalysisLevel(str, Enum):
    triage = "triage"
    deep = "deep"
    exploit = "exploit"
