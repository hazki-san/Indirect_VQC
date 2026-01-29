import subprocess
import yaml
import shutil

# Pythonファイルを実行して結果を取得
def run_python_script():
    try:
        result = subprocess.run(
            ['python', 'main.py', 'config2.yml', 'run'], 
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        return None
    except Exception as e:
        print(f"Error running script: {e}")
        return None

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
    #一応バックアップ ほぼ要らないかも
    backup_yml_file(yml_file_path, backup_file_path)

    for i in range (2): #depth 12 16
        #書き換え
        with open(yml_file_path, 'r') as file:
            data = yaml.safe_load(file)

        data["vqc"]["ansatz"]["depth"] = 12 + 4*i

        with open(yml_file_path, 'w') as file:
            yaml.dump(data, file) 
        #書き換え終了

        #run       
        print(f"depth {4*i+16} encode_type {j}  start.")
        run_python_script()
        print(f"depth {4*i+16} encode_type {j}  done.")


yml_file_path = 'config2.yml'  # YAMLファイルのパス
backup_file_path = 'config2_backup.yml'  # バックアップファイルのパス

automate_process(yml_file_path, backup_file_path)
#repeat_automate_process(yml_file_path, backup_file_path, 10)