{
    "dag":{
        "schedule_interval": "@once",
        "py_file": "gs://${ddos_bucket}/eval_dag_pipeline_util.py"
    },
    "beam_options": {
        "op_kwargs": {
            "BQ_PROJECT": "${project_id}",
            "INFERENCE_TARGET_DATASET": "inferenced_${random_suffix}",
            "GCS_TEMP_LOCATION": "gs://${ddos_bucket}/temp/bq",
            "REGION": "${region}",
            "MODEL_ENDPOINT_NAME": "${endpoint_name}",
            "INFERENCE_TARGET_TABLE": "ddos_automl_online_predictions_s06",
            "INFERENCE_TARGET_TABLE_SCHEMA": "timestamp:STRING,entity_type_flows:STRING,c0:INTEGER,flow_id:STRING,src_ip:STRING,src_port:INTEGER,dst_ip:STRING,dst_port:INTEGER,protocol:INTEGER,flow_duration:INTEGER,tot_fwd_pkts:INTEGER,tot_bwd_pkts:INTEGER,totlen_fwd_pkts:FLOAT,totlen_bwd_pkts:FLOAT,fwd_pkt_len_max:FLOAT,fwd_pkt_len_min:FLOAT,fwd_pkt_len_mean:FLOAT,fwd_pkt_len_std:FLOAT,bwd_pkt_len_max:FLOAT,bwd_pkt_len_min:FLOAT,bwd_pkt_len_mean:FLOAT,bwd_pkt_len_std:FLOAT,flow_byts_s:FLOAT,flow_pkts_s:FLOAT,flow_iat_mean:FLOAT,flow_iat_std:FLOAT,flow_iat_max:FLOAT,flow_iat_min:FLOAT,fwd_iat_tot:FLOAT,fwd_iat_mean:FLOAT,fwd_iat_std:FLOAT,fwd_iat_max:FLOAT,fwd_iat_min:FLOAT,bwd_iat_tot:FLOAT,bwd_iat_mean:FLOAT,bwd_iat_std:FLOAT,bwd_iat_max:FLOAT,bwd_iat_min:FLOAT,fwd_psh_flags:INTEGER,bwd_psh_flags:INTEGER,fwd_urg_flags:INTEGER,bwd_urg_flags:INTEGER,fwd_header_len:INTEGER,bwd_header_len:INTEGER,fwd_pkts_s:FLOAT,bwd_pkts_s:FLOAT,pkt_len_min:FLOAT,pkt_len_max:FLOAT,pkt_len_mean:FLOAT,pkt_len_std:FLOAT,pkt_len_var:FLOAT,fin_flag_cnt:INTEGER,syn_flag_cnt:INTEGER,rst_flag_cnt:INTEGER,psh_flag_cnt:INTEGER,ack_flag_cnt:INTEGER,urg_flag_cnt:INTEGER,cwe_flag_cnt:INTEGER,ece_flag_cnt:INTEGER,down_up_ratio:FLOAT,pkt_size_avg:FLOAT,fwd_seg_size_avg:FLOAT,bwd_seg_size_avg:FLOAT,fwd_byts_b_avg:INTEGER,fwd_pkts_b_avg:INTEGER,fwd_blk_rate_avg:INTEGER,bwd_byts_b_avg:INTEGER,bwd_pkts_b_avg:INTEGER,bwd_blk_rate_avg:INTEGER,subflow_fwd_pkts:INTEGER,subflow_fwd_byts:INTEGER,subflow_bwd_pkts:INTEGER,subflow_bwd_byts:INTEGER,init_fwd_win_byts:INTEGER,init_bwd_win_byts:INTEGER,fwd_act_data_pkts:INTEGER,fwd_seg_size_min:INTEGER,active_mean:FLOAT,active_std:FLOAT,active_max:FLOAT,active_min:FLOAT,idle_mean:FLOAT,idle_std:FLOAT,idle_max:FLOAT,idle_min:FLOAT,label:STRING,predict:STRING,json:STRING",
            "INCIDENT_TOPIC_ID": "${ddos_incidents_topic_id}",
            "SOURCE_TOPIC_ID": "${ddos_topic_id}"
        },
        "runner": "DataflowRunner",
        "project": "${project_id}",
        "job_name": "ddos-predict-stream-${random_suffix}",
        "streaming": null,
        "no_use_public_ips": true,
        "network": "${network_self_link}", 
        "subnetwork": "${subnet_self_link}",
        "service_account_email": "${service_account_email}",
        "temp_location": "gs://${ddos_bucket}/temp/py_temp",
        "worker_machine_type": "e2-standard-4",
        "staging_location": "gs://${ddos_bucket}/temp/py_stage",
        "region": "${region}",
        "noauth_local_webserver": null,
        "setup_file": "setup.py"
    }
}
