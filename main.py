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
def initialize_vqc() -> None:

    initial_cost_history = []
    min_cost_history = []
    all_optimized_param = []
    time_evolution_hamiltonian_strings = []

    #必要に応じて開始のステータスメッセージを表示

    start_time = time.time()
    vqc_instance = IndirectVQC


if __name__ == "__main__":
    #configファイル指定してあるか確認
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <config_file>")
        sys.exit(1)

    #configファイル読み込み
    config_file = sys.argv[1]
    config = load_config(config_file)

    if config:
        #operation: str = config["run"]      #VQCしかしないので要らないかも
        nqubits: int = config["nqubits"]
        state: str = config["state"]

        #observable: Dict = config["observable"] #いらないと思う 多分ここはVQEのObservable
        #arijitさんのところのObservable項は飛ばす

        