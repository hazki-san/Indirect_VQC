import json
import os
import sys
import time
import uuid
from ast import Dict
from datetime import datetime
from typing import List, Union

import yaml

#configファイル読み込む
def load_config(config_file_path):
    if not os.path.exists(config_file_path):
        print(f"Error: Config file '{config_file_path}' not found.")
        return None

    with open(config_file_path, "r") as file:
        config = yaml.safe_load(file)

    return config

#
def initialize_vqc(config) -> None:

    initial_cost_history = []
    min_cost_history = []
    all_optimized_param = []
    time_evolution_hamiltonian_strings = []

    #必要に応じて開始のステータスメッセージを表示

    start_time = time.time()
    vqc_instance = IndirectVQC(

    )
    vqc_output = vqc_instance.run_vqc()
    end_time = time.time()

    run_time = end_time - start_time
    print(f"VQC done with time taken: {run_time} sec.")
    


if __name__ == "__main__":
    #configファイル指定してあるか確認
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <config_file>")
        sys.exit(1)

    #configファイル読み込み
    config_file = sys.argv[1]
    config = load_config(config_file)

    #DBに色々する処理を追加する　阿南さんの参照
    for k in range(config["vqc"]["iteration"]):
        initialize_vqc(config)

        