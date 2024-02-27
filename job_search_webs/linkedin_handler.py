import credentials.credentials
from linkedin_api import Linkedin
from urllib.parse import urlparse, parse_qs

api = Linkedin(credentials.credentials.user, credentials.credentials.pw)


def get_job_description(job_link):
    job_id = get_job_id(job_link)
    job_description = get_job_from_id(job_id)
    return job_description


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


def get_job_from_id(job_id):
    print(f"Job ID: {job_id}")
    job_details = api.get_job(job_id)
    job_requirements = job_details.get('description', 'Job requirements not found.')
    return job_requirements['text']

# job_id = get_job_id('https://www.linkedin.com/jobs/view/3840618716/?trackingId=IQqWHCOqLLzNCRp3nZyf3A%3D%3D&refId'
#                     '=ByteString%28length%3D16%2Cbytes%3D2e4819cf...ddaa6b80%29&midToken=AQEtfYe9xmJzAA&midSig=16'
#                     '-JMaTyd0DH81&trk=eml-email_job_alert_digest_01-job_card-0-jobcard_body&trkEmail=eml'
#                     '-email_job_alert_digest_01-job_card-0-jobcard_body-null-d7u52m~lt3jgglv~7p-null-null&eid=d7u52m'
#                     '-lt3jgglv-7p&otpToken'
#                     '=MTUwYzE3ZTIxMDJkYzFjMWIwMjQwNGVkNDYxNmVlYmM4N2NjZDE0NjlkYTk4YzYxNzdjNDAzNjc0YzVlNWVmNmYyZGZkNWI5MWFkMmJlZjA1MWI4OTMxODM0MGI5MjQxYzFhM2I1YTg5NzNkZTUwNjZlZWEsMSwx')
# job_description = get_job_from_id(job_id)
# print(job_description)
