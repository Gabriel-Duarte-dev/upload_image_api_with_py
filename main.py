import zipfile
import uuid
import os
from typing import Union
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from os import listdir
from os.path import isfile, join
from urllib.parse import quote
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

IMAGEDIR = "images/"

app = FastAPI()
env = os.environ

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/upload/")
async def uploadImages(files: list[UploadFile]):
    if not files:
        return {"message": "No upload file sent"}
    
    unsupported_types = 0
    for file in files:
        file_type = file.content_type.split('/')

        if file_type[0] == "image":
            file.filename = f"{uuid.uuid4()}.{file_type[1]}"
            contents = await file.read()

            with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
                f.write(contents)
        else:
            unsupported_types += 1

    return {
        "success": f"{len(files) - unsupported_types} uploads successfull",
        "error": f"{unsupported_types} unsupported types"
    }

@app.get("/get-images/")
async def get_images():
    image_files = [f for f in listdir(IMAGEDIR) if isfile(join(IMAGEDIR, f))]
    image_list = []

    for filename in image_files:
        image_list.append({"filename": filename, "url": f"{env.get('SERVER_URL')}/images/{quote(filename)}"})
    return image_list

@app.get("/images/")
async def get_images():
    image_files = [f for f in listdir(IMAGEDIR) if isfile(join(IMAGEDIR, f))]
    image_list = []

    for file in image_files:
        image_list.append(FileResponse(file))
    return image_list

@app.get("/download-images/")
async def download_images():
    image_files = [f for f in os.listdir(IMAGEDIR) if os.path.isfile(os.path.join(IMAGEDIR, f))]
    zip_path = "images.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for image_file in image_files:
            zipf.write(os.path.join(IMAGEDIR, image_file), image_file)
    return StreamingResponse(open(zip_path, "rb"), media_type="application/zip", headers={"Content-Disposition": "attachment; filename=images.zip"})
