from flask import Flask, render_template, request
import numpy as np
import pandas as pd

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('myImage.html')



def adding(n1, n2):
    df = pd.DataFrame({"Name": ['sajeel'],
                     
                   "Address": ['abc'],
                   })
    return df.to_html(classes='table tablt-stripped')
    
   

if __name__ == '__main__':
   app.run()
