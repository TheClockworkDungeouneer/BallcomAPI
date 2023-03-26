from fastapi.templating import Jinja2Templates
import os
import jinja2


script_dir = os.path.realpath("Templates/")   ##os.path.dirname(__file__)
directory = script_dir     #os.path.join(script_dir, "Templates/")

print(directory)

templates = Jinja2Templates(directory=directory)
