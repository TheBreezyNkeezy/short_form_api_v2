# Package imports
import os
import openai
import lob_python
from lob_python.exceptions import ApiException
from lob_python.model.postcard_editable import PostcardEditable
from lob_python.model.address_editable import AddressEditable
from lob_python.model.merge_variables import MergeVariables
from lob_python.model.country_extended import CountryExtended
from lob_python.api.postcards_api import PostcardsApi
from dotenv import load_dotenv
from flask import Flask, request, render_template

# Local imports
import scraper

load_dotenv()
configuration = lob_python.Configuration(
    username = os.getenv('LOB_API_KEY')
)

# Inspiration for the template website came from the following sources:
# https://python.plainenglish.io/sentiment-analysis-flask-web-app-using-python-and-nltkintroduction-a45f893fb724
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/test-parse", methods=["POST"])
def test_parse():
    url = request.form["url"]
    dyn = request.form["dyn"]
    return scraper.parse_website(url, dyn)

# import lob_python
# from lob_python.exceptions import ApiException

# from lob_python.model.postcard_editable import PostcardEditable
# from lob_python.model.address_editable import AddressEditable
# from lob_python.model.merge_variables import MergeVariables
# from lob_python.model.country_extended import CountryExtended

# from lob_python.api.postcards_api import PostcardsApi

# configuration = lob_python.Configuration(
#   username = "test_41fef6c0ed6dbae478be0de1247d4ca6fc1"
# )

# postcard_editable = PostcardEditable(
#   description = "First Postcard",
#   front = "<html style='padding: 1in; font-size: 50;'>Front HTML for {{name}}</html>",
#   back = "<html style='padding: 1in; font-size: 20;'>Back HTML for {{name}}</html>",
#   to = AddressEditable(
#     name = "Harry Zhang",
#     address_line1 = "210 King Street",
# address_city = "San Francisco",
# address_state = "CA",
# address_zip = "94107",
#   ),
#   _from = AddressEditable(
#     name = "Leore Avidar",
#     address_line1 = "210 King Street",
#     address_city = "San Francisco",
#     address_state = "CA",
#     address_zip = "94107",
#     address_country = CountryExtended("US")
#   ),
#   merge_variables = MergeVariables(
#     name = "Harry",
#   ),
# )

# with lob_python.ApiClient(configuration) as api_client:
#   api = PostcardsApi(api_client)

# try:
#   created_postcard = api.create(postcard_editable)
#   print(created_postcard)
# except ApiException as e:
#   print(e)

if __name__ == "__main__":
    app.run(debug=True)