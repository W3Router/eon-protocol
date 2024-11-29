
from fastapi.openapi.utils import get_openapi
from eon.api.main import app
import json
from pathlib import Path
import yaml

def generate_openapi_spec():
    """生成OpenAPI规范文档"""
    openapi_schema = get_openapi(
        title="EON Protocol API",
        version="1.0.0",
        description="Privacy-preserving distributed computation protocol",
        routes=app.routes,
    )
    
    # 保存JSON格式
    with open('docs/openapi.json', 'w') as f:
        json.dump(openapi_schema, f, indent=2)
        
    # 保存YAML格式
    with open('docs/openapi.yaml', 'w') as f:
        yaml.dump(openapi_schema, f)

def generate_markdown_docs():
    """生成Markdown文档"""
    openapi_schema = json.loads(Path('docs/openapi.json').read_text())
    
    md_content = [
        "# EON Protocol API Documentation\n",
        "## Overview\n",
        f"{openapi_schema['info']['description']}\n",
        "## Endpoints\n"
    ]
    
    for path, methods in openapi_schema['paths'].items():
        md_content.append(f"### {path}\n")
        for method, details in methods.items():
            md_content.extend([
                f"#### {method.upper()}\n",
                f"{details['description']}\n",
                "**Parameters:**\n"
            ])
            
            if 'parameters' in details:
                for param in details['parameters']:
                    md_content.append(
                        f"- {param['name']} ({param['in']}): {param['description']}\n"
                    )
                    
            md_content.append("**Responses:**\n")
            for status, response in details['responses'].items():
                md_content.append(f"- {status}: {response['description']}\n")
                
    Path('docs/api.md').write_text('\n'.join(md_content))

if __name__ == '__main__':
    generate_openapi_spec()
    generate_markdown_docs()
