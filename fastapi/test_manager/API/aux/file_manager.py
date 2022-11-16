# @Author: Daniel Gomes
# @Date:   2022-11-12 09:12:49
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-11-16 17:15:41
import schemas.timestamp as TimestampSchemas
import aux.constants as Constants
import json
from datetime import datetime
import pytz


class FileManager:
    def __init__(self) -> None:
        pass

    # when peers send a TS of their instantiation steps
    # data is indexed by domain, however the first step(by netor itself)
    # domains will not be considered to index data

    def is_initial_step(self, action: str):
        return action != Constants.VSI_REQUEST_TS

    def parse_file_content(self, vsi_id):
        file_name = f'./results_vsi_{vsi_id}.json'
        try:
            f = open(file_name, 'r+')
            file_data = f.read()
            data = json.loads(file_data)
            print(type(file_data))
            data = TimestampSchemas.FileData(**data)
        except FileNotFoundError:
            f = open(file_name, 'w+')
            data = TimestampSchemas.FileData()
        return f, data

    def parse_timestamp_to_utc(self, timestamp):
        format = "%Y-%m-%d %H:%M:%S.%f"
        local_dt = datetime.strptime(str(timestamp), format)
        dt_utc = local_dt.astimezone(pytz.UTC)
        dt_utc_str = dt_utc.strftime(format)
        return dt_utc_str

    def write_to_file(self, f, data):
        data = data.dict()
        print(f"to write {data}")
        f.seek(0)
        json.dump(data, f)
        f.truncate()
        f.close()

    def store_vsi_timestamp(self,
                            vsi_id,
                            data: TimestampSchemas.TimestampData):
        _file, file_data = self.parse_file_content(vsi_id)
        ts = self.parse_timestamp_to_utc(data.timestamp)
        step = TimestampSchemas.Steps(action=data.action, timestamp=ts)
        if not self.is_initial_step(data.action):
            file_data.netor_initial_step = step
        else:
            if not data.domain:
                return
            if data.domain not in file_data.remaining_steps:
                file_data.remaining_steps[data.domain] = [step]
            else:
                file_data.remaining_steps[data.domain].append(step)
        print(file_data.dict())
        self.write_to_file(_file, file_data)
