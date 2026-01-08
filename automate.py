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

    for i in range (5): #depth 4 8 12 16 20
        for j in range (2): #encode type 1 2
            #書き換え
            with open(yml_file_path, 'r') as file:
                data = yaml.safe_load(file)

            data["vqc"]["ansatz"]["depth"] = 4 + 4*i
            data["vqc"]["Dataset"]["encode_type"] = j+1

            with open(yml_file_path, 'w') as file:
                yaml.dump(data, file) 
            #書き換え終了

            #run       
            print(f"depth {4*i+4} encode_type {j+1}  start.")
            run_python_script()
            print(f"depth {4*i+4} encode_type {j+1}  done.")


yml_file_path = 'config.yml'  # YAMLファイルのパス
backup_file_path = 'config_backup.yml'  # バックアップファイルのパス

automate_process(yml_file_path, backup_file_path)
#repeat_automate_process(yml_file_path, backup_file_path, 10)