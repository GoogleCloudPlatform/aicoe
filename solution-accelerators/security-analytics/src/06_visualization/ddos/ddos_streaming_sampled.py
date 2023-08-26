#!/usr/bin/env python

"""
 Copyright 2023 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 """

import datetime
import json
import logging
import numpy as np
import os
import pandas as pd
import sys

current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_path, "..", "..", "utils"))

from gcp_utils import publish_pubsub_messages

logger = logging.getLogger(__name__)


def process_data(row):
    """Takes a row as input and returns a JSON equivalent

    Args:
        row (_type_): _description_

    Returns:
        _type_: Returns the data dictionary as a JSON string.
    """
    row = json.loads(row)
    data = {key: str(value) for key, value in row.items()}

    return json.dumps(data)


def get_samples_from_dataset(dataset_file_csv: str):
    df = pd.read_csv(dataset_file_csv)
    df["entity_type_flows"] = df["Flow_ID"]
    print(datetime.datetime.now().isoformat())
    df["Timestamp"] = df.apply(lambda x: datetime.datetime.now().isoformat(), axis=1)
    df["json"] = df.apply(lambda x: x.to_json(), axis=1)

    df_benign = df[df['Label'] == 'Benign'].sample(1)
    df_ddos = df[df['Label'] == 'ddos'].sample(1)
    return (df_benign, df_ddos)

def generate_prediction_request(row):
    try:
        renamed_dict = dict()
        renamed_dict['timestamp'] = row['Timestamp']
        renamed_dict['entity_type_flows'] = row['entity_type_flows']
        renamed_dict['c0'] = row['field0']
        renamed_dict['flow_id'] = row['Flow_ID']
        renamed_dict['src_ip'] = row['Src_IP']
        renamed_dict['src_port'] = row['Src_Port']
        renamed_dict['dst_ip'] = row['Dst_IP']
        renamed_dict['dst_port'] = row['Dst_Port']
        renamed_dict['protocol'] = row['Protocol']
        renamed_dict['flow_duration'] = row['Flow_Duration']
        renamed_dict['tot_fwd_pkts'] = row['Tot_Fwd_Pkts']
        renamed_dict['tot_bwd_pkts'] = row['Tot_Bwd_Pkts']
        renamed_dict['totlen_fwd_pkts'] = row['TotLen_Fwd_Pkts']
        renamed_dict['totlen_bwd_pkts'] = row['TotLen_Bwd_Pkts']
        renamed_dict['fwd_pkt_len_max'] = row['Fwd_Pkt_Len_Max']
        renamed_dict['fwd_pkt_len_min'] = row['Fwd_Pkt_Len_Min']
        renamed_dict['fwd_pkt_len_mean'] = row['Fwd_Pkt_Len_Mean']
        renamed_dict['fwd_pkt_len_std'] = row['Fwd_Pkt_Len_Std']
        renamed_dict['bwd_pkt_len_max'] = row['Bwd_Pkt_Len_Max']
        renamed_dict['bwd_pkt_len_min'] = row['Bwd_Pkt_Len_Min']
        renamed_dict['bwd_pkt_len_mean'] = row['Bwd_Pkt_Len_Mean']
        renamed_dict['bwd_pkt_len_std'] = row['Bwd_Pkt_Len_Std']
        renamed_dict['flow_byts_s'] = row['Flow_Byts_s']
        renamed_dict['flow_pkts_s'] = row['Flow_Pkts_s']
        renamed_dict['flow_iat_mean'] = row['Flow_IAT_Mean']
        renamed_dict['flow_iat_std'] = row['Flow_IAT_Std']
        renamed_dict['flow_iat_max'] = row['Flow_IAT_Max']
        renamed_dict['flow_iat_min'] = row['Flow_IAT_Min']
        renamed_dict['fwd_iat_tot'] = row['Fwd_IAT_Tot']
        renamed_dict['fwd_iat_mean'] = row['Fwd_IAT_Mean']
        renamed_dict['fwd_iat_std'] = row['Fwd_IAT_Std']
        renamed_dict['fwd_iat_max'] = row['Fwd_IAT_Max']
        renamed_dict['fwd_iat_min'] = row['Fwd_IAT_Min']
        renamed_dict['bwd_iat_tot'] = row['Bwd_IAT_Tot']
        renamed_dict['bwd_iat_mean'] = row['Bwd_IAT_Mean']
        renamed_dict['bwd_iat_std'] = row['Bwd_IAT_Std']
        renamed_dict['bwd_iat_max'] = row['Bwd_IAT_Max']
        renamed_dict['bwd_iat_min'] = row['Bwd_IAT_Min']
        renamed_dict['fwd_psh_flags'] = row['Fwd_PSH_Flags']
        renamed_dict['bwd_psh_flags'] = row['Bwd_PSH_Flags']
        renamed_dict['fwd_urg_flags'] = row['Fwd_URG_Flags']
        renamed_dict['bwd_urg_flags'] = row['Bwd_URG_Flags']
        renamed_dict['fwd_header_len'] = row['Fwd_Header_Len']
        renamed_dict['bwd_header_len'] = row['Bwd_Header_Len']
        renamed_dict['fwd_pkts_s'] = row['Fwd_Pkts_s']
        renamed_dict['bwd_pkts_s'] = row['Bwd_Pkts_s']
        renamed_dict['pkt_len_min'] = row['Pkt_Len_Min']
        renamed_dict['pkt_len_max'] = row['Pkt_Len_Max']
        renamed_dict['pkt_len_mean'] = row['Pkt_Len_Mean']
        renamed_dict['pkt_len_std'] = row['Pkt_Len_Std']
        renamed_dict['pkt_len_var'] = row['Pkt_Len_Var']
        renamed_dict['fin_flag_cnt'] = row['FIN_Flag_Cnt']
        renamed_dict['syn_flag_cnt'] = row['SYN_Flag_Cnt']
        renamed_dict['rst_flag_cnt'] = row['RST_Flag_Cnt']
        renamed_dict['psh_flag_cnt'] = row['PSH_Flag_Cnt']
        renamed_dict['ack_flag_cnt'] = row['ACK_Flag_Cnt']
        renamed_dict['urg_flag_cnt'] = row['URG_Flag_Cnt']
        renamed_dict['cwe_flag_cnt'] = row['CWE_Flag_Count']
        renamed_dict['ece_flag_cnt'] = row['ECE_Flag_Cnt']
        renamed_dict['down_up_ratio'] = row['Down_Up_Ratio']
        renamed_dict['pkt_size_avg'] = row['Pkt_Size_Avg']
        renamed_dict['fwd_seg_size_avg'] = row['Fwd_Seg_Size_Avg']
        renamed_dict['bwd_seg_size_avg'] = row['Bwd_Seg_Size_Avg']
        renamed_dict['fwd_byts_b_avg'] = row['Fwd_Byts_b_Avg']
        renamed_dict['fwd_pkts_b_avg'] = row['Fwd_Pkts_b_Avg']
        renamed_dict['fwd_blk_rate_avg'] = row['Fwd_Blk_Rate_Avg']
        renamed_dict['bwd_byts_b_avg'] = row['Bwd_Byts_b_Avg']
        renamed_dict['bwd_pkts_b_avg'] = row['Bwd_Pkts_b_Avg']
        renamed_dict['bwd_blk_rate_avg'] = row['Bwd_Blk_Rate_Avg']
        renamed_dict['subflow_fwd_pkts'] = row['Subflow_Fwd_Pkts']
        renamed_dict['subflow_fwd_byts'] = row['Subflow_Fwd_Byts']
        renamed_dict['subflow_bwd_pkts'] = row['Subflow_Bwd_Pkts']
        renamed_dict['subflow_bwd_byts'] = row['Subflow_Bwd_Byts']
        renamed_dict['init_fwd_win_byts'] = row['Init_Fwd_Win_Byts']
        renamed_dict['init_bwd_win_byts'] = row['Init_Bwd_Win_Byts']
        renamed_dict['fwd_act_data_pkts'] = row['Fwd_Act_Data_Pkts']
        renamed_dict['fwd_seg_size_min'] = row['Fwd_Seg_Size_Min']
        renamed_dict['active_mean'] = row['Active_Mean']
        renamed_dict['active_std'] = row['Active_Std']
        renamed_dict['active_max'] = row['Active_Max']
        renamed_dict['active_min'] = row['Active_Min']
        renamed_dict['idle_mean'] = row['Idle_Mean']
        renamed_dict['idle_std'] = row['Idle_Std']
        renamed_dict['idle_max'] = row['Idle_Max']
        renamed_dict['idle_min'] = row['Idle_Min']
        renamed_dict['label'] = row['Label']
    except KeyError as ex:
        print(f"KeyError: {str(ex)}")
        return dict()

    req_pre = '{ "instances": [ {'
    req_suf = ' }  ] } '
    df = pd.DataFrame([renamed_dict])
    X_test = df.drop(['label'], axis=1)
    Y_test = df['label']
    temp = ''

    for c in X_test.columns:
        try:
            if c in ['active_mean', 'active_std', 'active_max', 'active_min', 'bwd_iat_mean', 'bwd_iat_std', 
                    'bwd_iat_tot', 'bwd_iat_max', 'bwd_iat_min', 'bwd_pkt_len_mean', 
                    'bwd_pkt_len_std', 'bwd_pkt_len_max', 'bwd_pkt_len_min', 'bwd_pkts_s', 
                    'bwd_seg_size_avg', 'down_up_ratio', 'flow_byts_s', 'flow_iat_mean', 'flow_iat_std', 
                    'flow_iat_max', 
                    'flow_pkts_s', 'fwd_iat_mean', 'fwd_iat_max', 'flow_iat_min', 'fwd_iat_std', 
                    'fwd_iat_tot', 'fwd_iat_min', 'fwd_pkt_len_mean', 'fwd_pkt_len_std', 
                    'fwd_pkt_len_max', 'fwd_pkt_len_min', 'fwd_pkts_s', 'fwd_seg_size_avg', 'idle_mean', 
                    'idle_std', 'idle_max', 'idle_min',
                    'pkt_len_mean', 'pkt_len_std', 'pkt_len_var', 'pkt_size_avg', 'pkt_len_min',
                    'pkt_len_max', 'totlen_fwd_pkts', 'totlen_bwd_pkts']:
                if (isinstance(X_test.iloc[0][c], str) == False and np.isnan(X_test.iloc[0][c])) or (isinstance(X_test.iloc[0][c], str) == True and (X_test.iloc[0][c] == 'nan' or X_test.iloc[0][c] == '')):
                    temp = temp + '"{}": {}, '.format(c, 0)
                elif (isinstance(X_test.iloc[0][c], str) == False and np.isinf(X_test.iloc[0][c])) or (isinstance(X_test.iloc[0][c], str) == True and X_test.iloc[0][c] == 'inf'):
                    temp = temp + '"{}": {}, '.format(c, 9223372036854775807)
                else:
                    temp = temp + '"{}": {}, '.format(c, X_test.iloc[0][c])
            else:
                temp = temp + '"{}": "{}", '.format(c, X_test.iloc[0][c])
        except Exception as e:
            print(str(e))

    temp = req_pre + temp[:-2] + req_suf
    return temp

def load_arguments_from_env():
    env_undef = []
    for env in ["PROJECT_ID", "DDOS_TOPIC_NAME"]:
        if env not in os.environ:
            env_undef.append(env)

    if len(env_undef) > 0:
        logger.error(
            f"The following environment variables are required and not defined: {env_undef}"
        )
        return (None, None)
    else:
        return (os.environ.get("PROJECT_ID"), os.environ.get("DDOS_TOPIC_NAME"))

def main():
    """Publish to PubSub"""

    (project, pubsub_topic) = load_arguments_from_env()

    if project != None and pubsub_topic != None:
        file_loc = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "ddos_sample.csv")
        )

        (df_benign, df_ddos) = get_samples_from_dataset(file_loc)

        print(f"Benign Pub/Sub JSON:\n{str(df_benign['json'].values)}")
        print(f"\n\nDDoS Pub/Sub JSON:\n{str(df_ddos['json'].values)}")
        
        for index, row in df_benign.iterrows():
            print("\n\nBenign Prediction JSON:")
            print(generate_prediction_request(row))
        for index, row in df_ddos.iterrows():
            print("\n\nDDoS Prediction JSON:")
            print(generate_prediction_request(row))
        print("Publishing Benign sample\n")
        publish_pubsub_messages(
            project, pubsub_topic, df_benign["json"], process_data, use_pandas=True
        )
        print("Publishing DDoS sample\n")
        publish_pubsub_messages(
            project, pubsub_topic, df_ddos["json"], process_data, use_pandas=True
        )

main()
