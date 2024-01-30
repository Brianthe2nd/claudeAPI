from flask import Flask, request, jsonify
import boto3
import json
import os
from dotenv import load_dotenv
from urllib.parse import parse_qs

# Load environment variables from .env file
load_dotenv()

# Now you can access the variables using os.environ
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
region_name = os.environ.get('REGION_NAME')

app = Flask(__name__)

@app.route('/', methods=['GET'])
def status_endpoint():
    return jsonify({'status': 'Server is live'})

@app.route('/prompt', methods=['POST'])
def prompt_endpoint():
    # Get the prompt from the request data
    data = request.get_json()
    print('data')
    print(data)
    description = data.get('Description')
    print('description')
    print(description)
    # Extract and process query parameters from the URL
    query_string = request.url.split('?', 1)[-1]
    query_parameters = parse_qs(query_string)
    if 'prompt' in query_parameters:
        quiz = query_parameters['prompt'][0]
    else:
        quiz = None 
    # both quiz and the description are strings
    print('quiz')
    print(quiz)    
    prompt = quiz + description
    print('prompt')
    print(prompt)
    # Your existing function
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
        "max_tokens_to_sample": 300,
        "temperature": 0.05,
        "top_p": 0.8,
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
