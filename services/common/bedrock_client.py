import boto3
import logging
from typing import Type, TypeVar
from pydantic import BaseModel

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=BaseModel)

class BedrockExtractor:
    """
    Multimodal AI Extractor for 2026. 
    Handles documents and images natively via the Bedrock Converse API.
    """
    def __init__(self, region_name: str = "us-east-1", model_id: str = "us.anthropic.claude-sonnet-4-6"):
        self.client = boto3.client('bedrock-runtime', region_name=region_name)
        self.model_id = model_id

    def extract_structured_data(self, file_bytes: bytes, file_name: str, pydantic_model: Type[T]) -> T:
        ext = file_name.split('.')[-1].lower()
        
        # 🛡️ Resilience Patch: Check if PDF is a "fake" (plain text disguised as PDF)
        if ext == "pdf" and not file_bytes.startswith(b"%PDF"):
            logger.warning(f"File {file_name} has .pdf extension but invalid header. Falling back to text.")
            ext = "txt"

        # Supported formats for the Bedrock Document Block
        doc_formats = ["pdf", "csv", "docx", "xls", "xlsx", "html", "txt", "md"]
        # Supported formats for the Bedrock Image Block
        img_formats = {"png": "png", "jpg": "jpeg", "jpeg": "jpeg", "webp": "webp"}

        content_block = []

        # Step 1: Wrap bytes in the correct API block
        if ext in doc_formats:
            content_block.append({
                "document": {
                    "format": ext,
                    "name": "doc_" + file_name.replace(".", "_")[:20],
                    "source": {"bytes": file_bytes}
                }
            })
        elif ext in img_formats:
            content_block.append({
                "image": {
                    "format": img_formats[ext],
                    "source": {"bytes": file_bytes}
                }
            })
        else:
            # Fallback for unknown extensions: try raw text decode
            content_block.append({
                "text": file_bytes.decode('utf-8', errors='ignore')
            })

        # Step 2: Define the strict JSON tool based on your Pydantic model
        schema = pydantic_model.model_json_schema()
        tool_name = f"extract_{pydantic_model.__name__.lower()}"
        
        tool_config = {
            "tools": [{
                "toolSpec": {
                    "name": tool_name,
                    "description": f"Extract data into {pydantic_model.__name__} format.",
                    "inputSchema": {"json": schema}
                }
            }],
            "toolChoice": {"tool": {"name": tool_name}}
        }

        messages = [{
            "role": "user",
            "content": content_block + [{"text": "Extract all relevant fields into structured JSON. If a field like a date or total is missing from the document, set it to null in the JSON. Do not make up data or use placeholders like UNKNOWN."}]
        }]

        # Step 3: Invoke the AI
        try:
            logger.info(f"Invoking {self.model_id} via Inference Profile...")
            response = self.client.converse(
                modelId=self.model_id,
                messages=messages,
                toolConfig=tool_config
            )
            
            # Step 4: Parse the tool result
            for content in response['output']['message']['content']:
                if 'toolUse' in content:
                    return pydantic_model(**content['toolUse']['input'])
            
            raise ValueError("Claude failed to use the extraction tool.")

        except Exception as e:
            logger.error(f"Bedrock API Error: {e}")
            raise
