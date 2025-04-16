from flask import Flask, render_template, request, jsonify,send_from_directory
from flask import flash, redirect, url_for
from flask import session

import papermill as pm
import logging
import sys
import os
import pandas as pd
from flask_socketio import SocketIO, emit
import yaml

print("Python executable:", sys.executable)
print("Python path:", sys.path)

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
app.secret_key = 'your_secret_key'  # 用于闪存消息

# 上传文件的保存路径
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 模型的路径
MODEL_FOLDER = 'models'
app.config['MODEL_FOLDER'] = MODEL_FOLDER
# 确保模型目录存在
os.makedirs(MODEL_FOLDER, exist_ok=True)


# 首页路由
@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    print(files)
    file_options = [{'value': file, 'label': file} for file in files]

    models = os.listdir(app.config['MODEL_FOLDER'])
    print(models)
    model_options = [{'value': model, 'label': model} for model in models]

    return render_template('index.html',
                           files=files,
                           file_options=file_options,
                           model_options=model_options,
                           )
#获取参数路由
@app.route('/get_model_params/<model_name>')
def get_model_params(model_name):
    """根据模型名称返回对应的参数"""
    if model_name == "askl_ocv.ipynb":
        params = [
            {"name": "Project Theme", "params_name": "proj_theme","default": "OCV"},
            {"name": "Don't Use Columns", "params_name": "drop_col_list", "default": "cif_idx,name"},
            {"name": "Low accuracy column name", "params_name": "low_accuracy_column_name", "default": "original_md_ocv"},
            {"name": "High accuracy column name", "params_name": "high_accuracy_column_name", "default": "expt_ocv"},
            {"name": "random seed", "params_name": "random_seed", "default": "461"}
            ]
    else:
        params = [
            {"name": "Project Theme", "params_name": "proj_theme", "default": "HOF"},
            {"name": "SMILES column name", "params_name": "smi_column_name", "default": "smiles"},
            {"name": "Low accuracy column name", "params_name": "low_accuracy_column_name",  "default": "acc_low"},
            {"name": "High accuracy column name", "params_name": "high_accuracy_column_name", "default": "acc_high"}
            ]  # 其他情况默认参数

    return jsonify(params)

@app.route('/process', methods=['POST'])
def process():
    """ 处理动态表单数据 """
    data = request.get_json()  # **确保 Flask 解析 JSON**

    if not data:
        return jsonify({"status": "error", "message": "未收到数据"}), 400  # 处理异常情况

    model_name = data.get("model_options", "未选择模型")  # 获取模型名
    dynamic_params = {key: value for key, value in data.items() if key != "model_options"}  # 获取其他参数

    print("用户选择的模型:", model_name)
    print("动态参数:", dynamic_params)

    proj_theme = dynamic_params.get('proj_theme', 'error')

    try:
        os.chdir('/home/chongzhi/research/delta_learning/ADC_platform/models')  # 切换到模型目录
        logging.debug("开始运行 Notebook")
        pm.execute_notebook(
            'askl_ocv.ipynb',  # 原始Notebook路径
            'pm_result.ipynb',            # 输出Notebook路径

            parameters=dynamic_params,  # 参数传递给Notebook
            kernel_name='python3'
        )
        logging.debug("Notebook 运行完成")


        session['dynamic_params'] = dynamic_params
        session['model_name'] = model_name
        session['proj_theme'] = proj_theme


    except Exception as e:
        logging.error(f"运行 Notebook 时出错: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    

    return jsonify({
        "status": "success",
        "model_name": model_name,
        "parameters": dynamic_params,
        "redirect_url": "/result"  # **告诉前端跳转的目标页面**
    })

@app.route('/result')
def result():

    proj_theme = session['proj_theme']
    # 读取对应 YAML 文件
    result_path = os.path.join(app.static_folder, 'data', proj_theme, "config.yaml")
    print(result_path)
    print("当前工作目录:", os.getcwd())
    print("配置路径:", result_path)

    display_config = {}

    if os.path.exists(result_path):
        with open(result_path, "r", encoding="utf-8") as f:
            display_config = yaml.safe_load(f)
    else:
        display_config = {
            "description": "默认模型展示内容。",
            "images": [],
            "notes": []
        }

    return render_template(
        "result.html",
        proj_theme=proj_theme,
        model_name=session['model_name'],
        parameters=session['dynamic_params'],
        display_config=display_config
    )

# 处理用户输入的路由
@app.route('/process2', methods=['POST'])
def process2():
    file_option = request.form.get('file_options')  # 获取用户输入
    file_path = 'uploads/' + file_option

    model_option = request.form.get('model_options')  # 获取用户输入
    model_path = 'models/' + model_option

    form_data = request.form.to_dict()  # 获取整个表单，转换为字典
    #{'file_options': 'ocv_features_normalized_241003.csv', 'model_options': 'askl_ocv.ipynb', 'Project Theme': 'OCV', 'drop_col_list': 'cif_idx,name', 'Low accuracy column name': 'original_md_ocv', 'High accuracy column name': 'expt_ocv', 'random seed': '461'}
    
    proj_theme = form_data['Project Theme']

    # 简单逻辑处理
    #result = f"proj_theme: {proj_theme.upper()}"

    dynamic_params = {key: value for key, value in form_data.items()}

    print(dynamic_params)

    try:
        logging.debug("开始运行 Notebook")
        pm.execute_notebook(
            'models/askl_ocv.ipynb',  # 原始Notebook路径
            'pm_result.ipynb',            # 输出Notebook路径

            parameters={'proj_theme': proj_theme,
                        'file_path': file_path,
                        'smi_column_name': smi_column_name,
                        'low_accuracy_column_name': low_accuracy_column_name,
                        'high_accuracy_column_name': high_accuracy_column_name,
                        },  # 参数传递给Notebook
            kernel_name='python3'
        )
        logging.debug("Notebook 运行完成")

        image_paths = {
        'image_url1': 'static/data/'+proj_theme+'/0_before_delta.jpg',
        'image_url2': 'static/data/'+proj_theme+'/1_compare.jpg',
        'image_url3': 'static/data/'+proj_theme+'/2_adc.png'
        }

    
    except Exception as e:
        logging.error(f"运行 Notebook 时出错: {e}")
        return jsonify({'status': 'error', 'message': str(e)})


    return render_template('result.html', **image_paths)
    # **表示拆开imagepath中的变量分别传入。

@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查请求中是否有文件
    if 'file' not in request.files:
        flash('没有文件被上传！')
        return redirect(request.url)

    file = request.files['file']

    # 检查文件名是否为空
    if file.filename == '':
        flash('没有选择文件！')
        return redirect(request.url)

    # 保存文件
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        flash(f'文件 {file.filename} 上传成功！')
        return redirect(url_for('index'))
    
@app.route('/preview_csv', methods=['GET'])
def preview_csv():
    file_option = request.args.get('file')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_option)

    try:
        df = pd.read_csv(file_path)
        preview = df.head().to_html(index=False, classes='table table-bordered')
        row_count, col_count = df.shape
        preview_info = f"<p>行数: {row_count}, 列数: {col_count}</p>{preview}"
        return jsonify({'status': 'success', 'preview': preview_info})
    except Exception as e:
        logging.error(f"预览 CSV 文件时出错: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # 监听所有 IP，方便通过远程访问
    app.run(host='0.0.0.0', port=14050, debug=True)