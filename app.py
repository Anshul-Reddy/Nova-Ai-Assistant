from flask import Flask,render_template,request
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os,markdown2

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

grounding_tool = types.Tool(
    google_search = types.GoogleSearch()
)

config = types.GenerateContentConfig(
    tools = [grounding_tool]
)

chat_history=[]

app = Flask(__name__)

def needs_search(user_text):

    search_words=[
        "today",
        "latest",
        "news",
        "weather",
        "current",
        "live",
        "score",
        "price",
        "yesterday",
        "stock",
        "bitcoin",
        "ipl",
        "cricket",
        "football",
        "election",
        "breaking",
        "update"
    ]
    for word in search_words:
        if word in user_text.lower():
            return True
    return False

@app.route("/",methods = ["GET","POST"] )
def home():

    response_text = ""
    if request.method == "POST":

        action = request.form["action"]
        if action == "clear":
            chat_history.clear()
            return render_template("index.html",chat_history=chat_history
                                   )
        user_text = request.form["message"]

        chat_history.append({
            "role":"user",
            "message":user_text
        })
        prompt=""
        for msg in chat_history:
            prompt += f"{msg['role'].capitalize()}: {msg['message']}\n"
        
        try:

            if needs_search(user_text):
                print("Using Google Search.")

                response = client.models.generate_content(
                model = "gemini-3.5-flash",
                contents = prompt,
                config = config
                )
            else:
                print("Using Gemini Only.")

                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents = prompt 
                )

            response_text = response.text
            response_html = markdown2.markdown(response_text)
            
            chat_history.append({
                "role":"gemini",
                "message":response_html
            })

        except Exception as e:
            error = str(e)

            if "429" in error:
                response_text = "⚠️ Google search in temporarily unavailable due to API quota. Please try again later."

            elif "404" in error:
                response_text = "⚠️ The selected AI Model was not found."

            else:
                response_text = "⚠️ Oops! Something went wrong please try again."
            print(error)
            chat_history.append({
                "role":"gemini",
                "message":response_html
            })

    return render_template("index.html",chat_history=chat_history)

if __name__ == "__main__":
    app.run(debug=True)