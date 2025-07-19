from openai import OpenAI
import re
import json
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("OPEN_AI_API")
print(token)

client = OpenAI(
api_key= token
)

def parseResume(text):
  completion = client.chat.completions.create(
    model="gpt-4o-mini",
    store=True,
    messages=[
      {"role": "developer", "content": "parse the resume and provide JSON output that contains name ,email ,summary ,skills ,experince and projects and give this output in the content part of your output"},
      {"role" : "user" , "content": text}
    ],
  )

  # Extract the content
  assistant_content = completion.choices[0].message.content

  # Clean up the JSON block
  cleaned_json_str = re.sub(r"^```json|```$", "", assistant_content.strip(), flags=re.MULTILINE).strip()

  # Parse and pretty print
  resume_data = json.loads(cleaned_json_str)
  result = json.dumps(resume_data, indent=2)
  print(result)
  return(result)


def generateDescription(text):
  completion = client.chat.completions.create(
    model="gpt-4o-mini",
    store=True,
    messages=[
      {"role": "developer", "content": ''' You are an expert HR assistant helping employers write professional, detailed, and compelling job descriptions.
Generate a complete job description for the following role using the information provided to you. The description should include:
1. Job Title
2. Company Overview (optional if not provided)
3. Job Summary (2-4 sentences)
4. Key Responsibilities (bullet points, 5–10 max)
5. Required Qualifications (education, experience, certifications)
6. Preferred Qualifications (optional)
7. Skills (technical and soft)
8. Work Environment & Schedule (e.g., remote, hybrid, in-office, shift)
9. Compensation & Benefits (optional if not provided)
10. Equal Opportunity Statement (optional)
 '''} ,
      {"role" : "user" , "content": text} 
    ],
  )

  # Extract the content
  assistant_content = completion.choices[0].message.content
  print(assistant_content)
  return assistant_content