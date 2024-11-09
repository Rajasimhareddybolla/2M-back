import os
import pandas as pd
import time
import google.generativeai as genai


# GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_KEY = "AIzaSyD194W9zkMt0Gbud6IuNloJNyPfRblv9gU"
print("google api key",GEMINI_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)


def upload_to_gemini(path, mime_type=None, metadata=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    try:
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file
    except Exception as e:
        print(f"Failed to upload file: {e}")
        return None
      
  
def wait_for_files_active(files):
  """Waits for the given files to be active.

  Some files uploaded to the Gemini API need to be processed before they can be
  used as prompt inputs. The status can be seen by querying the file's "state"
  field.

  This implementation uses a simple blocking polling loop. Production code
  should probably employ a more sophisticated approach.
  """
  print("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      time.sleep(10)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  print("...all files ready")
  print()
  
def upload_files(path = None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, path)
    path = path if path else 'data'
    files = os.listdir(path)
    files = [os.path.join(path, file) for file in files if file.endswith('.csv')]
    mime_type = "text/csv"
   
    files = [
    upload_to_gemini(file, mime_type=mime_type) for file in files
    ]
    print(files)
    wait_for_files_active(files)
    return files


def get_files (ids):
    return [genai.get_file(id) for id in ids]