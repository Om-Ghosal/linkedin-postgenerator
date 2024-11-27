from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import time
import dotenv
import os
from selenium.webdriver.edge.options import Options
import shutil

from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
import uvicorn
from fastapi.responses import JSONResponse
from typing import List


from llm import llm_generete,post_maker_llm

dotenv.load_dotenv()


options = Options()
options.add_argument("--headless")  # Run Edge in headless mode
options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration

options.add_argument("--disable-extensions")  # Disable extensions
options.add_argument("--disable-software-rasterizer")  # Disable software rasterizer

service = Service(executable_path="msedgedriver.exe")
driver = webdriver.ChromiumEdge(service=service, options=options)
url = "https://www.linkedin.com/article/new/"
def postImages():
    upload_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Upload from computer"]')
    print(upload_button)
    upload_button.click()
    time.sleep(2)

    # using selenium
    file_input = driver.find_element(By.ID, "media-editor-file-selector__file-input")
    cwd = os.getcwd().replace('\\','/')
    file_path = f'''{cwd}/temp1/{os.listdir("temp1")[0]}'''
    file_input.send_keys(file_path)

    print("File uploaded successfully.")

    
    
def get_btn(driver,pattern):
    buttons = driver.find_elements(By.XPATH, pattern)
    return buttons[0].get_attribute('id')

def linkedinbot(title, content,images_upload = None):
    try:
        driver.get(url)

        # login

        email = os.getenv("LINKEDIN_USERNAME")
        pswd = os.getenv("LINKEDIN_PSWD")

        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys(email)
        time.sleep(1)

        pswd_field = driver.find_element(By.ID, "password")
        pswd_field.send_keys(pswd+Keys.ENTER)


        #  automated post
        if images_upload:
            postImages()
        # title
        title_textarea = driver.find_element(By.ID, "article-editor-headline__textarea")
        title_textarea.send_keys(title+Keys.ENTER)

        time.sleep(1)

        driver.switch_to.active_element.send_keys(content)

        time.sleep(1)
        # get the next btn
        submit_btn_id = get_btn(driver, "//button[starts-with(@id, 'ember') and .//span[text()='Next']]")

        time.sleep(3)
        send_btn = driver.find_element(By.ID , submit_btn_id)
        send_btn.click()

        time.sleep(3)

        post_dict = post_maker_llm(title,content).replace('{','').replace('}',''.replace('\n','').replace('\t','').replace("'",'').replace('"','').replace('title','').replace('body',''))
        print(post_dict)
        driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Text editor for creating content"]').send_keys(post_dict+Keys.ENTER)
        


        # get the publish btn
        time.sleep(5)
        publish_btn_id = get_btn(driver, "//button[starts-with(@id, 'ember') and .//span[text()='Publish']]")
        
        

        publish_btn = driver.find_element(By.ID , publish_btn_id)
        publish_btn.click()

        time.sleep(5)
        driver.quit()

        shutil.rmtree("temp1/image.png")

        return  {"success":200,"message":"Post created successfully"}

    except Exception as e:

        
        # shutil.rmtree("temp1")
        return {"success":0, "error":str(e)}

    
    

class LlmData(BaseModel):
    app_name: str
    app_context: str
    tech_stack: str
class InputData(BaseModel):
    title: str
    content: str

app = FastAPI()

@app.post("/api")
async def create_item(
    title: str = Form(...), 
    content: str = Form(...), 
    images: List[UploadFile] = File(...)
):
    input_data = InputData(title=title, content=content)
    
    images_flag = False
    if images is not None:
        if not os.path.exists("temp1"):
            os.mkdir("temp1")
            
        for image in images:
            img = await image.read()
            print(f"Received image: {image.filename}, size: {len(img)} bytes")
            img_location = f"temp1/{image.filename}"

            with open(img_location, "wb") as img_file:
                img_file.write(img)
            images_flag = True
    
    return linkedinbot(input_data.title, input_data.content,images_flag)
        

@app.post("/llm")
async def create_llm(llm_data: LlmData):
    
    return llm_generete(llm_data.app_name,llm_data.app_context,llm_data.tech_stack)

if '__main__' == __name__:
    uvicorn.run(app, host="127.0.0.1", port=8000 )