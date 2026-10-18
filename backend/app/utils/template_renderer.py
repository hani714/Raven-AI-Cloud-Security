from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from datetime import datetime, timezone
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent

env = Environment(
    loader=FileSystemLoader(BASE_DIR / "email" / "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

def render_template(dto: BaseModel) -> str:
    context = dto.model_dump()
    template_name = context.pop("template_name")
    context["year"] = datetime.now(timezone.utc).year
    
    template = env.get_template(template_name)

    return template.render(**context)