from concurrent import futures
import grpc
import hservice_pb2
import hservice_pb2_grpc
import dservice_pb2
import dservice_pb2_grpc
import hashlib

data_ip = 'localhost'
data_port = 50051
data_channel = grpc.insecure_channel(f'{data_ip}:{data_port}')
d_stub = dservice_pb2_grpc.DBStub(data_channel)

class HashServicer(hservice_pb2_grpc.HSServicer):
    def GetHash(self, request, context):
        print(f"Received GetHash request with passcode: {request.passcode}, IP: {request.ip}, Port: {request.port}")
        # Retrieve data from data server
        data_request = dservice_pb2.Passcode(code=request.passcode)
        data_response = d_stub.GetAuthData(data_request)
        print(f"Retrieved data: {data_response.msg}")
        # Compute hash 
        hash = hashlib.sha256(data_response.msg.encode()).hexdigest()
        return hservice_pb2.Response(hash=hash)

if __name__ == '__main__':
    # Initialize gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hservice_pb2_grpc.add_HSServicer_to_server(HashServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Hash server started on port 50052")
    server.wait_for_termination()
