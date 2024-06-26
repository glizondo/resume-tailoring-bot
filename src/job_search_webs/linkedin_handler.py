from linkedin_api import Linkedin
from urllib.parse import urlparse, parse_qs

from src.credentials import credentials

api = Linkedin(credentials.user, credentials.pw)

# Given a link provided pulls the job id
def get_job_description(job_link):
    job_id = get_job_id(job_link)
    job_description = get_job_requirements(job_id)
    return job_description


# Filters the link to pull the id depending on the type of link
def get_job_id(job_link):
    parsed_url = urlparse(job_link)
    query_params = parse_qs(parsed_url.query)
    job_id_current_id = query_params.get("currentJobId", [None])[0]
    if job_id_current_id:
        return job_id_current_id
    else:
        path_segments = parsed_url.path.split('/')
        if 'view' in path_segments:
            job_id_index = path_segments.index('view') + 1
            job_id_view_link = path_segments[job_id_index] if job_id_index < len(path_segments) else None
            return job_id_view_link

# Uses linkedin api to get details about job given a job id
def get_job_requirements(job_id):
    print(f"Job ID: {job_id}")
    job_details = api.get_job(job_id)
    job_requirements = job_details.get('description', 'Job requirements not found.')
    return job_requirements['text']
