from flask import Flask, request, jsonify
import boto3
import json
import os

app = Flask(__name__)

@app.route('/status', methods=['GET'])
def status_endpoint():
    return jsonify({'status': 'Server is live'})

@app.route('/prompt', methods=['POST'])
def prompt_endpoint():
    # Get the prompt from the request data
    data = request.get_json()
    prompt = data.get('prompt')

    # Your existing function
    AWS_ACCESS_KEY_ID = 'AKIA2UC3FQM4PHSGWLMX'
    AWS_SECRET_ACCESS_KEY = 'r65soHz4zLPgVTsQyVtfTLpr92Di10YxEEPpmmV0'
    REGION_NAME = 'us-west-2'
    if not prompt.startswith("Human:"):
        prompt = "Human: " + prompt
    if not prompt.endswith("Assistant:"):
        prompt += "\nAssistant:"
    boto3.setup_default_session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                region_name=REGION_NAME)

    bedrock = boto3.client(service_name='bedrock-runtime')
    body = json.dumps({
        "prompt": f"\n\n{prompt}\n\nAssistant:",
        "max_tokens_to_sample": 2000,
        "temperature": 0.1,
        "top_p": 0.9,
    })
    modelId = 'anthropic.claude-instant-v1'
    accept = 'application/json'
    contentType = 'application/json'

    response = bedrock.invoke_model_with_response_stream(body=body, modelId=modelId, accept=accept, contentType=contentType)

    event_stream = response['body']
    combined_string = ''

    for event in event_stream:
        data = event['chunk']
        json_string = data['bytes'].decode('utf-8')
        json_data = json.loads(json_string)
        value = json_data['completion']
        combined_string += value

    # Return the combined string as a JSON response
    return jsonify({'response': combined_string})

if __name__ == '__main__':
    app.run(debug=True)
