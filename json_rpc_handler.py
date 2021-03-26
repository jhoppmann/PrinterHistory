import json


class JsonRpcHandler:
    registered_classes = {}

    @staticmethod
    def wrap_into_json_rpc(value: str, call_id: str) -> str:
        jsonrpc_dict = {'jsonrpc': '2.0', 'id': call_id, 'result': value}
        return json.dumps(jsonrpc_dict)

    def register(self, clazz: str, methods: dict) -> None:
        self.registered_classes[clazz] = methods
        pass

    def process(self, payload) -> str:
        data = payload
        call_id = str(data['id'])
        clazz = data['method'].split('.')[0]
        method = data['method'].split('.')[1]
        func = self.registered_classes[clazz][method]
        ret_val = func()
        return self.wrap_into_json_rpc(value=ret_val, call_id=call_id)
