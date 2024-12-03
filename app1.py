import boto3
import botocore.config
import json
from datetime import datetime

#function to generate a blog topic accepts a string and returns a string
def blog_generate_using_bedrock(blogtopic:str)-> str:
    
    #writing the prompt msg
    prompt=f"""Human: Write a 200 words blog on the topic {blogtopic}
    Assistant:"""

    #we nedd to mention the body
    body={
        "prompt":prompt,
        "temperature":0.5,
        "top_p":0.9,
        "max_tokens_to_sample": 200,
        "stop_sequences": ["\n\nHuman:"]

    }
    #writing a try except block with basic config to call the foundational model
    try:
        
        bedrock=boto3.client("bedrock-runtime",region_name="us-east-1",
                             config=botocore.config.Config(read_timeout=300,
                                                           retries={'max_attempts':3}))
        #calling the specific model
        response=bedrock.invoke_model(body=json.dumps(body),modelId="anthropic.claude-v2")

        #reading the body content
        response_content=response.get('body').read()
        response_data=json.loads(response_content)
        print(response_data)
        #getting the details w.r.t blog from response_data
        blog_details = response_data['completion']
        return blog_details
        
    except Exception as e:
        print(f"Error generating the blog:{e}")
        return " "

#Fucntion to save blog into s3 bucket   
def save_blog_details_s3(s3_key,s3_bucket,generate_blog):
    s3 = boto3.client('s3')

    try:
        s3.put_object(Bucket=s3_bucket,Key=s3_key,Body=generate_blog)
        print("Code saved to s3")
    
    except Exception as e:
        print("Error when saving the code to s3")


#next we'll have to define the lambda handler as we write the code in lamda
#the belopw function wil be hit first

#this will hit via the aws api gateway where event will have the blog body
def lambda_handler(event, context):
    event = json.loads(event['body'])
    blogtopic=event['blog_topic']

    generate_blog=blog_generate_using_bedrock(blogtopic=blogtopic)

    #setting the time and storing s3 bucket
    if generate_blog:
        current_time = datetime.now().strftime('%H%M%S')
        s3_key = f"blog-output/{current_time}.txt"
        s3_bucket ='aws-bedrockblog'
        save_blog_details_s3(s3_key,s3_bucket,generate_blog)

    else:
        print("No blog was generated")

    return{
        'statusCode':200,
        'body':json.dumps('blog generation is complete')   
    }