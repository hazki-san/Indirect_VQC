import json
import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Job:
    id: str
    creation_time: datetime
    execution_second: int
    n_qubits: int
    depth: int
    gate_type: str
    bn: str
    t: str
    cost: str
    parameter: str
    iteration: str
    cost_history: str
    parameter_history: str
    iteration_history: str
    actual_labels: str
    estimated_labels: str
    estimated_labels_history: str
    encode_type: int
    config: str


class JobFactory:
    def __init__(self, config):
        self.config = config
        pass

    def _to_string(self, two_dim_array):
        s = ""
        for i in range(len(two_dim_array)):
            s += ",".join([str(j) for j in two_dim_array[i]])
            if i == len(two_dim_array):
                break

            s += "\n"

        return s

    def create(
        self,
        current_time: datetime,
        start_time: float,
        end_time: float,
        cost_history: list[float],
        param_history: list[float],
        iter_history: list[int],
        actual_labels: list[float],
        estimated_labels_history: list[float],
        fixed_random_params: list[float],
    ) -> Job:
        if self.config["vqc"]["ansatz"]["type"] == "direct":
            job = self._create_job_for_direct(
                current_time,
                start_time,
                end_time,
                cost_history,
                param_history,
                iter_history,
                actual_labels,
                estimated_labels_history,
            )
        else:
            job = self._create_job_for_indirect(
                current_time,
                start_time,
                end_time,
                cost_history,
                param_history,
                iter_history,
                actual_labels,
                estimated_labels_history,
                fixed_random_params,
            )
        return job

    def _create_job_for_direct(
        self,
        current_time: datetime,
        start_time: float,
        end_time: float,
        cost_history: list[float],
        param_history: list[float],
        iter_history: list[int],
        actual_labels: list[float],
        estimated_labels_history: list[float],
    ) -> Job:
        return Job(
            str(uuid.uuid4()),
            current_time,
            int(end_time - start_time),
            self.config["nqubit"],
            self.config["vqc"]["ansatz"]["depth"],
            self.config["vqc"]["ansatz"]["type"],
            "",
            "",
            str(cost_history[-1]),
            str(param_history[-1]),
            str(iter_history[-1]),
            str(cost_history),
            self._to_string(param_history),
            str(iter_history),
            str(actual_labels),
            str(estimated_labels_history[-1]),
            str(estimated_labels_history),
            "",
            "",
            json.dumps(self.config),
        )

    def _create_job_for_indirect(
        self,
        current_time: datetime,
        start_time: float,
        end_time: float,
        cost_history: list[float],
        param_history: list[float],
        iter_history: list[int],
        actual_labels: list[float],
        estimated_labels_history: list[float],
        fixed_random_params: list[float]
    ) -> Job:
        return Job(
            str(uuid.uuid4()),
            current_time,
            int(end_time - start_time),
            self.config["nqubit"],
            self.config["vqc"]["ansatz"]["depth"],
            self.config["vqc"]["ansatz"]["type"],
            str(self.config["vqc"]["ansatz"]["ugate"]["coefficient"]),
            str(self.config["vqc"]["ansatz"]["ugate"]["time"]["value"])
            if "value" in self.config["vqc"]["ansatz"]["ugate"]["time"]["value"]
            else "",
            str(cost_history[-1]),
            str(param_history[-1]),
            str(iter_history[-1]),
            str(cost_history),
            self._to_string(param_history),
            str(iter_history),
            str(actual_labels),
            str(estimated_labels_history[-1]),
            str(estimated_labels_history),
            self.config["vqc"]["Dataset"]["encode_type"],
            str(fixed_random_params),
            json.dumps(self.config),
        )
