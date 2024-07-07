from openai import AzureOpenAI
import os

client = AzureOpenAI(
    api_key=os.environ['AZURE_OPENAI_API_KEY'],
    api_version=os.environ['AZURE_OPENAI_API_VERSION'],
    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT']
)


def generate_response(question: str) -> str:
    response = client.chat.completions.create(
        model="acd-openai-gpt35-aihub-dev",  # model = "deployment_name".
        messages=[
            {"role": "system",
             "content": "You are an AI expert and you work in the retail industry."
                        "You have 5 years of experience."
                        "You are now in an interview and answering questions."
                        "Never give more than 3 examples"
                        "If you do give examples, link them to your own projects."
                        "Don't give any examples if the question is general."
                        "Try to come up with relevant projects to your job or industry. "
                        "Always answer in first person and focus on what you did."},
            {"role": "user", "content": question},
        ]
    )

    return response.choices[0].message.content