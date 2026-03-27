import boto3
import json
import os
import logging

# Force non-interactive AWS behavior
os.environ['AWS_PAGER'] = ''
os.environ['AWS_DEFAULT_OUTPUT'] = 'json'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_claude():
    model_ids_to_try = [
        "us.anthropic.claude-sonnet-4-6",      # Recommended for us-east-1
        "global.anthropic.claude-sonnet-4-6"
    ]

    prompt = "Hello Claude! Confirm you are working by responding with this exact JSON: {\"status\": \"working\", \"model\": \"Claude Sonnet 4.6\", \"message\": \"Hello from Termux on Android in Missouri! The pipeline is alive.\"}"

    for model_id in model_ids_to_try:
        print(f"\n🔄 Trying model ID: {model_id}")
        try:
            bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

            response = bedrock.converse(
                modelId=model_id,
                messages=[{
                    "role": "user",
                    "content": [{"text": prompt}]
                }],
                inferenceConfig={
                    "maxTokens": 300,
                    "temperature": 0.1          # Only temperature (no topP)
                }
            )

            output_text = response['output']['message']['content'][0]['text']
            print("\n✅ SUCCESS! Claude responded:")
            print("=" * 70)
            print(output_text)
            print("=" * 70)

            try:
                data = json.loads(output_text)
                print("\n✅ Parsed JSON:", json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print("\n(Note: Response was not pure JSON)")

            print(f"\n✅ Claude is working with model: {model_id}")
            return  # Success → stop

        except Exception as e:
            print(f"❌ Failed with {model_id}: {type(e).__name__} - {e}")

    print("\n❌ All attempts failed.")

if __name__ == "__main__":
    test_claude()
