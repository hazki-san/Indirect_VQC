import json
import os
import sys
import time
import uuid
from ast import Dict
from datetime import datetime
from typing import List, Union

import yaml

from src.vqc import IndirectVQC

symbol_count = 10

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

    start_time = time.time()

    print("=" * symbol_count + "Config" + "=" * symbol_count)
    print(config)
    print("=" * symbol_count + "VQC running" + "=" * symbol_count)
   
    for i in range(vqc_iteration):

        each_start_time = time.time()
        vqc_instance = IndirectVQC(
            nqubit = nqubit,
            ansatz = ansatz,
            init_param = initialparam,
            optimization = optimization,
            dataset = dataset,
        )
        if runmode == "vqc":
            vqc_output = vqc_instance.run_vqc()
        elif runmode == "debug":
            vqc_output = vqc_instance.debug()
        each_end_time = time.time()

        each_run_time = each_end_time - each_start_time
    
        print(f"VQC #{i+1} done with time taken: {each_run_time} sec.")

        initial_cost = vqc_output["initial_cost"]
        min_cost = vqc_output["min_cost"]
        optimized_param = vqc_output["optimized_param"]

        initial_cost_history.append(initial_cost)
        min_cost_history.append(min_cost)
        all_optimized_param.append(optimized_param)

        #time_evolution_hamiltonian_string.append(str(vqe_instance.get_ugate_hamiltonain()))

    end_time = time.time()
    total_run_time = end_time - start_time

    print("=" * symbol_count + "Output" + "=" * symbol_count)

    print(f"Initial costs: {initial_cost_history}")
    print(f"Optimized minimum costs: {min_cost_history}")
    print(f"Optimized parameters: {all_optimized_param}")
    print(f"Run time: {total_run_time} sec")

    


if __name__ == "__main__":
    #configファイル指定してあるか確認
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <config_file>")
        sys.exit(1)

    #configファイル読み込み
    config_file = sys.argv[1]
    config = load_config(config_file)

    #is_valid_config: bool = validate_yml_config(config) #このモジュール作ってないのであとで追加
    is_valid_config: bool = True

    if config and is_valid_config:
        nqubit: int = config["nqubit"]
        vqc_iteration: int = config["vqc"]["iteration"]
        optimization: Dict = config["vqc"]["optimization"]
        ansatz: Dict = config["vqc"]["ansatz"]
        dataset: Dict = config["vqc"]["Dataset"]
        initialparam: Union[str, List[float]] = ansatz["init_param"]
        runmode :str = config["mode"]

    initialize_vqc()

    #DBに色々する処理を追加する　阿南さんの参照

        