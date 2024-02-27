from openai import OpenAI
import credentials.credentials


def query_chat_gpt(resume_info, job_info):
    client = OpenAI(
        # This is the default and can be omitted
        api_key=credentials.credentials.api_key_chatgpt,
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Create a resume that contains the following properties using the resume and the job "
                           f"description provided below:\n- Keep it under 500 words\n- Include only three sections named exactly: "
                           f"EDUCATION, WORK EXPERIENCES, and SKILLS\n- Adapt the resume so it uses the keywords "
                           f"based on the requirements of the job\n- Stop generating content after being done "
                           f"with the Skills section, this is being used to create a document\n - For each of the work experiences, divide the description of the job role in maximum three bullet points"
                           f":\nResume:{resume_info}\nJob Description:{job_info}",
            }
        ],
        model="gpt-3.5-turbo",
    )
    content = chat_completion.choices[0].message.content
    print(content)
    return content

