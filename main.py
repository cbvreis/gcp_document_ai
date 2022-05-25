from google.cloud import documentai as documentai
import gcsfs
import json
from google.oauth2 import service_account
import re


def get_document_orc(project_id: str, location: str, processor: str, blob, credentials) -> str:
    '''
    Get the text from a document
    :param project_id:
    :param file_path:
    :param location:
    :param processor:
    :param blob
    :return:
    '''

    documentai_client = documentai.DocumentProcessorServiceClient(credentials=credentials)
    mime_type = 'application/pdf'
    resource_name = documentai_client.processor_path(
        project_id, location, processor
    )

    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(
        content=blob.download_as_bytes(), mime_type=mime_type)
    print('-----SUCCESS RawDocument -------')

    # Configure the process request
    request = documentai.ProcessRequest(
        name=resource_name, raw_document=raw_document)
    print('-----SUCCESS REQUEST -------')
    # Use the Document AI client to process the sample form

    result = documentai_client.process_document(request=request)
    print('-----SUCCESS PROCESS -------')

    return result.document.text


def get_file(stage: str, file_path: str):
    '''
    Get file from storage
    :param stage
    :param file_path
    :return blob
    '''

    from google.cloud import storage
    client = storage.Client()
    # https://console.cloud.google.com/storage/browser/[bucket-id]/
    bucket = client.get_bucket(stage)
    # Then do other things...
    blob = bucket.get_blob(file_path)
    return blob

def get_credentials()->service_account.Credentials:
    '''
    Get credentials from json file
    :return:
    '''
    gcs_file_system = gcsfs.GCSFileSystem(project='<!----SAUDE ID PROJECT---->')
    gcs_json_path = '<!----FILE CREDENTIALS--->'

    with gcs_file_system.open(gcs_json_path) as f:
        json_dict = json.load(f)

    credentials = service_account.Credentials.from_service_account_info(json_dict)
    return credentials


def get_result_exam(template:str,exam:str,unit:str)->str:
    '''
    Get the result of the exam
    :param template:
    :param exam:
    :param unit:
    :return:
    '''
    try:
        m = re.search(fr'{exam}(.*?) {unit}',template.replace('\n',' '))
        return m.group(0)
    except:
        return None
    return m.group(0)


if 'main' == __name__:
    templates = ['a+', 'fleury']
    arr_result = {}
    for template in templates:
        file = get_file('<!----BUCKET NAME ----->', '<-----FILE PATH----->')
        credentials = get_credentials()
        arr_result[template] = get_document_orc('<!----SAUDE ID PROJECT---->', 'us', '<!----PROCESSOR ID ------>', file,
                                                credentials)

    for template in templates:
        print(f'Template {template}->ORC: {get_result_exam(arr_result[template], "UREIA", "mg/dL")}')
        print(f'Template {template}->ORC: {get_result_exam(arr_result[template], "CREATININA", "mg/dL")}')
        print(f'Template {template}->ORC: {get_result_exam(arr_result[template], "POTASSIO", "mEq/L")}')
        # Exam not found
        print(f'Template {template}->ORC: {get_result_exam(arr_result[template], "EXAM1", "mEq/L")}')
