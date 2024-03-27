from openai import OpenAI
import credentials.credentials


def resume_chatgpt_query(resume_info, job_info):
    client = OpenAI(
        api_key=credentials.credentials.api_key_chatgpt,
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Create a tailored resume that contains the following properties using the RESUME and the JOB DESCRIPTION provided below:"
                           f"\n- Keep it under 600 words"
                           f"\n- It must include three sections named exactly: Education, Work Experiences, Skills"
                           f"\n- Include the three previous sections even if it is not relevant or modified"
                           f"\n- Ensure that each section ends with ':'"
                           f"\n- Extract the keywords from the JOB DESCRIPTION and include them in the tailored resume"
                           f"\n- Adapt the resume so it uses the keywords based on the requirements of the job"
                           f"\n- Modify the Skills section as needed to add all the relevant and matching keywords found in the Job Description and Resume"
                           f"\n- Stop generating content after being done with the Skills section, this is being used to create a document"
                           f"\n- For each of the work experiences, divide the description of the job role in maximum four bullet points"
                           f"\n- For each of the bullet points in each experience, show details about the highlights and words to quantify the success including keywords from the job description"
                           f"\n- If necessary, create new bullet points to add relevant key experience in the resume to stand out"
                           f"\n- The design of the bullet points should be black dots that show up in a word document format"
                           f"\n- Ensure that each bullet point contains 40 words at least"
                           f"\n- Do not include any non-relevant work experience to the job description"
                           f"\n- Do not include any empty spaces or lines"
                           f"\n- Finish the prompt with the 'END' keyword"
                           f"\n- Focus on the technical keywords from the job description to modify the resume:"
                           f"\nResume:{resume_info}\nJob Description:{job_info}",
            }
        ],
        model="gpt-3.5-turbo",
    )
    content = chat_completion.choices[0].message.content
    print(content)
    return content


def cover_letter_chatgpt_query(resume_info, job_info, tone):
    client = OpenAI(
        api_key=credentials.credentials.api_key_chatgpt,
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Create a cover letter that contains the following properties using the RESUME and the JOB DESCRIPTION provided below:"
                           f"\n- Keep it under 300 words"
                           f"\n- Always start exactly with 'Dear Hiring Manager,' even if the tone is more or less formal"
                           f"\n- Use a {tone} tone for the cover letter"
                           f"\n- It must include only three paragraphs"
                           f"\n- Extract the keywords from the JOB DESCRIPTION and include them in the cover letter"
                           f"\n- Adapt the cover letter so it uses the keywords based on the requirements of the job"
                           f"\n- Do not include any non-relevant work experience to the job description"
                           f"\n- Do not include any empty spaces or lines"
                           f"\n- Finish the prompt with the 'END' keyword"
                           f"\n- Focus on the technical keywords from the job description to modify the resume:"
                           f"\nResume:{resume_info}\nJob Description:{job_info}",
            }
        ],
        model="gpt-3.5-turbo",
    )
    content = chat_completion.choices[0].message.content
    print(content)
    return content
