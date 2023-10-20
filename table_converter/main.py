from flask import Flask, render_template, request
import openai
import json

app = Flask(__name__)

# Set your OpenAI API key here
openai.api_key = "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"

# Define a dictionary to map routes to task descriptions
task_descriptions = {
    "/": "You will be provided with table headers and a description of the table to create. Your task is to generate only a JSON table based on the given headers and description. For example, if the headers are 'Name' and 'Age' and the description is 'A table of people's names and ages,' your response should be a JSON table like: [{'Name': 'John', 'Age': 30}, {'Name': 'Alice', 'Age': 25}, ...]."
}

# Define functions for different routes
@app.route("/", methods=["GET", "POST"])
def table():
    task_route = "/"
    return handle_task(task_route)

# Common function to handle tasks
def handle_task(task_route):
    task_description = task_descriptions.get(task_route, "")
    conversation = []  # Initialize an empty list to store the conversation history

    if request.method == "POST":
        message = request.form["message"]

        # Add user's message to the conversation
        conversation.append({"role": "user", "content": f"Person: {message}"})

        header_color = request.form["header_color"]
        row_color = request.form["row_color"]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": task_description},
                *conversation  # Include the entire conversation history
            ],
            max_tokens=300  # Adjust as needed
        )

        # Add AI's reply to the conversation
        reply = response.choices[0].message["content"]

        try:
            # Attempt to parse the JSON response
            json_response = json.loads(reply)

            # Ensure that the JSON response is a list of dictionaries
            if isinstance(json_response, list) and all(isinstance(item, dict) for item in json_response):
                table_html = "<table>"
                if len(json_response) > 0:
                    table_html += "<thead><tr>"
                    for key in json_response[0]:
                        table_html += f"<th style='background-color: {header_color};'>{key}</th>"
                    table_html += "</tr></thead><tbody>"
                    for row in json_response:
                        table_html += f"<tr style='background-color: {row_color};'>"
                        for key, value in row.items():
                            table_html += f"<td>{value}</td>"
                        table_html += "</tr>"
                    table_html += "</tbody></table>"
                else:
                    table_html += "<p>No data available</p>"
            else:
                table_html = "<p>Invalid JSON format</p>"
        except json.JSONDecodeError:
            table_html = "<p>Unable to parse JSON response</p>"

        conversation.append({"role": "assistant", "content": table_html})

        return render_template("index.html", conversation=conversation, task_description=task_description, task_route=task_route)

    return render_template("index.html", conversation=conversation, task_description=task_description, task_route=task_route)

if __name__ == '__main__':
    app.run(debug=True)
