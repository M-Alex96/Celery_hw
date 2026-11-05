from flask import Flask, send_file, request, jsonify
import uuid
import os
from tasks import upscale_task

app = Flask("app")

UPLOAD_DIR = "upload_pics"
PROCESSED_DIR = "processed_pics"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

@app.route("/upscale", methods=["POST"])
def upscale_route():
    if "image" not in request.files:
        return jsonify({"error": "Поле 'image' обязательно"}), 400
    image = request.files["image"]
    if not image or image.filename == "":
        return jsonify({"error": "Файл не передан"}), 400
    extension = image.filename.rsplit(".", 1)[-1].lower() if "." in image.filename else "png"
    image_id = uuid.uuid4().hex
    input_path = os.path.join(UPLOAD_DIR, f"{image_id}.{extension}")
    output_path = os.path.join(PROCESSED_DIR, f"{image_id}.{extension}")
    image.save(input_path)
    task = upscale_task.delay(input_path, output_path)
    return jsonify({"task_id": task.id})

@app.route("/tasks/<task_id>", methods =["GET"])
def get_task_status(task_id: str):
    task = upscale_task.AsyncResult(task_id)
    response = {"task_id": task_id, "status": task.status}
    if task.status == "SUCCESS":
        response["file"] = f"/processed/{os.path.basename(task.result)}"
    elif task.status == "FAILURE":
        response["error"] = str(task.info)
    return jsonify(response)

@app.route("/processed/<filename>", methods=["GET"])
def get_processed_file(filename: str):
    path = os.path.abspath(os.path.join(PROCESSED_DIR, filename))
    if not path.startswith(os.path.abspath(PROCESSED_DIR) + os.sep):
        return jsonify({"error": "Недопустимое имя файла"}), 400
    if not os.path.isfile(path):
        return jsonify({"error": "Файл не найден"}), 404
    return send_file(path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)