import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import tensorflow as tf
from classify_image import run_inference_on_image, NodeLookup
from PIL import Image

UPLOAD_FOLDER = '/var/www/tf/static'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

app = Flask(__name__)
app.secret_key = 'some_secret90210'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(full_path, out_path=None, max_w=800, max_h=600):
    try:
        with Image.open(full_path) as im:
            siz = im.size
            if siz[0] > max_w or siz[1] > max_h:
                rato = min(max_w/siz[0], max_h/siz[1])
                newsize = [int(x * rato) for x in siz]
                resized = im.resize(newsize)
                split_img = full_path.split(".")
                if not out_path:
                    new_path = "".join(split_img[:1]) + "_resized" + "." + split_img[-1]
                else:
                    new_path = os.sep.join([out_path, split_img[0].split(os.path.sep)[-1] + "_resized" + "." + split_img[-1]])
                print("Saving {} as {}".format(full_path, new_path))
                resized.save(new_path)
                return new_path
            else:
                return full_path
    except Exception as e:
        print("EXCEPTION: " + str(e))
        raise


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            flash("OK so far...")
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file', filename=filename))
            return redirect(url_for('do_classify_image', filename=filename))
    return '''
    <!doctype html>
    <head>
    <link rel="stylesheet" type="text/css" href="{}" />
    <title>ImageNet - Home</title>
    </head>
    <h1>Upload new File</h1>
    <form method="post" enctype="multipart/form-data">
      <p><input type="file" name="file">
         <input type="submit" value="Upload">
    </form>
    '''.format(url_for("static", filename="styles.css"))


def main(img_file):
    try:
        full_path = os.sep.join([UPLOAD_FOLDER, img_file[1]])
        output = run_inference_on_image(full_path)
        return output
    except Exception as e:
        print("EXCEPTION: " + str(e))
        raise


@app.route('/classify/', methods=['GET'])
def do_classify_image():
    # check for URL param of "filename"

    img_file = request.args.get("filename")

    full_path = os.sep.join([UPLOAD_FOLDER, img_file])

    # All the TensorFlow stuff happens in the next function
    predictions_out = run_inference_on_image(full_path)

    # Creates node ID --> English string lookup.
    node_lookup = NodeLookup()

    # top_k = predictions.argsort()[-FLAGS.num_top_predictions:][::-1]
    top_k = predictions_out.argsort()[-5:][::-1]
    
    output = []

    for node_id in top_k:
      human_string = node_lookup.id_to_string(node_id)
      score = predictions_out[node_id]
      print('%s (score = %.5f)' % (human_string, score))
      output.append((human_string, score))
    # outz = tf.app.run(main=main, argv=[None, img_file]) 
   
    if len(output) > 0:
        alt_text = "Most likely " + str(output[0][0])
    else:
        alt_text = "Unable to categorize this image"
 
    print_out = []
    for x in output:
        print_out.append("<tr><td>" + str(x[0]) + "</td><td>" +  "{:3.1f}".format(x[1] * 100) + " percent </td></tr>")
 
    out_file_full_path = resize_image(full_path)
    out_filename = out_file_full_path.split(os.sep)[-1] 

    return '''
    <!doctype html>
    <head>
    <link rel="stylesheet" type="text/css" href="{}" />

    <title>Image Classification</title>
    </head>
    <body>
    <p>Image classified as:</p>
    <table><tr><th>Prediction</th><th>Confidence</th></tr>{}</table>
    <br />
    <br />
    <a href="/">Click here to upload another image</a>
    <br />
    <br />
    <img src="{}" alt="{}" />
    </body>
    </html>'''.format(url_for("static", filename="styles.css")," ".join(print_out), url_for("static", filename=out_filename), alt_text)

if __name__ == "__main__":
    app.run(debug=True)
