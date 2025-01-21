from flask import Flask
import numpy as np
import pandas as pd

app = Flask('__main__')

@app.route('/')
def hello():
    #return "<table> <tr><td>", adding(3,4), "</td></tr></table>"
    return adding(3,4)


def adding(n1, n2):
    df = pd.DataFrame({"Name": ['sajeel'],
                     
                   "Address": ['abc'],
                   })
    return df.to_html(classes='table tablt-stripped')
