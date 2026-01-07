def sql_for_insert_job() -> str:
    return """
    INSERT INTO jobs (
        id,
        creation_time,
        execution_second,
        n_qubits,
        depth,
        gate_type,
        bn,
        t,
        cost,
        parameter,
        iteration,
        cost_history,
        parameter_history,
        iteration_history,
        actual_labels,
        estimated_labels,
        estimated_labels_history,
        encode_type,
        config
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
