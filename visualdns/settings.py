import os

settings = {
    'debug' : True,
    'static_path' : os.path.join(os.path.dirname(__file__) , "static") ,
    'template_path' : os.path.join(os.path.dirname(__file__) , "template") ,
}