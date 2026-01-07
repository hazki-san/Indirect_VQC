import subprocess
import yaml
import shutil

# Pythonファイルを実行して結果を取得
def run_python_script():
    try:
        result = subprocess.run(
            ['python', 'main.py', 'config.yml', 'run'], 
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        return None
    except Exception as e:
        print(f"Error running script: {e}")
        return None

# ymlファイルの更新
def update_yml_file(yml_file_path, result_value):
    with open(yml_file_path, 'r') as file:
        data = yaml.safe_load(file)
    
    # "gate" -> "time" -> "value" がNoneや空リストの場合にリストに初期化
    if data['gate']['time']['value'] is None or not isinstance(data['gate']['time']['value'], list):
        data['gate']['time']['value'] = []
    
    # 実行結果をリストとして追加
    result_list = [float(x) for x in result_value.strip('[]').split()]  # 文字列をfloatリストに変換
    data['gate']['time']['value'] = result_list

    # "gate" -> "time" -> "type" を "absolute" に変更
    data['gate']['time']['type'] = "absolute"
    
    # YAMLファイルを更新
    with open(yml_file_path, 'w') as file:
        yaml.dump(data, file)
"""
今回やりたいこと
    depthを8~20の間で、encode_typeを0->1->2->0...の順に実行する
"""

# 元のYAMLファイルをバックアップ
def backup_yml_file(original_file_path, backup_file_path):
    shutil.copyfile(original_file_path, backup_file_path)
    print(f"Backup created at {backup_file_path}")

# YAMLファイルを元に戻す
def restore_yml_file(backup_file_path, original_file_path):
    shutil.copyfile(backup_file_path, original_file_path)
    print(f"YML file restored to its original state from {backup_file_path}")

# 自動化処理
def automate_process(yml_file_path, backup_file_path):
   
    for i in range (4): #depth 8 12 16 20
        with open(yml_file_path, 'r') as file:
            data = yaml.safe_load(file)
        data["vqc"]["ansatz"]["depth"] = 8 + 4*i
        with open(yml_file_path, 'w') as file:
            yaml.dump(data, file)
 
        for j in range (3): #encode type 0 1 2
            backup_yml_file(yml_file_path, backup_file_path)
            with open(yml_file_path, 'r') as file:
                data = yaml.safe_load(file)
            data["Dataset"]["encode_type"] = j
            with open(yml_file_path, 'w') as file:
                yaml.dump(data, file)         
            run_python_script()
            print(f"depth {4*i+8} encode_type {j}  done.")


yml_file_path = 'config/test.yml'  # YAMLファイルのパス
backup_file_path = 'config/configfile_backup.yml'  # バックアップファイルのパス

#automate_process(yml_file_path, backup_file_path)
repeat_automate_process(yml_file_path, backup_file_path, 10)