import requests
from parser.file_reader import read_file


API_TOKEN = "your API token here"
API_URL = "https://api-inference.huggingface.co/models/microsoft/phi-2"
resume_text = read_file("../uploads/Puneet_CV.pdf")

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

prompt = f"""Extract the following information from the resume below in json format:
- Full Name
- Email
- Phone
- Experience
- Projects
- Education
- Skills
- Social Links

Resume:
{resume_text}

Extracted: """

payload = {
    "inputs": prompt,
    "parameters": {
        "max_new_tokens": 500,
        "temperature": 0.3,
        "do_sample": False
    }
}

response = requests.post(API_URL, headers=headers, json=payload)
if response.status_code == 200:
    try:
        output = response.json()
        print("\nGenerated Output:\n")
        print(output[0]["generated_text"])
    except Exception as e:
        print("⚠️ Failed to parse JSON response:")
        print(response.text)
else:
    print(f"❌ Request failed with status code {response.status_code}")
    print("Response content:", response.text)
