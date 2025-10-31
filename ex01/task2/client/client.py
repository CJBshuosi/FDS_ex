import sys
import grpc
import dservice_pb2
import dservice_pb2_grpc
import hservice_pb2
import hservice_pb2_grpc

data_ip = 'localhost'
data_port = 50051
data_channel = grpc.insecure_channel(f'{data_ip}:{data_port}')
d_stub = dservice_pb2_grpc.DBStub(data_channel)


hash_ip = 'localhost' 
hash_port = 50052
hash_channel = grpc.insecure_channel(f'{hash_ip}:{hash_port}')
h_stub = hservice_pb2_grpc.HSStub(hash_channel)

if __name__ == '__main__':
    username = 'marco.dreher'
    password = 'password'

    """
    Workflow:
    1. Register user on data server
    2. Store data on data server
    3. Generate one-time passcode from data server
    4. Request hash computation from hash server using passcode
    """

    # Step 1: Register the user on data server
    user_pass = dservice_pb2.UserPass(username=username, password=password)  # Create UserPass message
    res = d_stub.RegisterUser(user_pass)  # Call RegisterUser RPC on data server
    if not res.success:
        print('Failure when registering user')
    else: 
        print('User registered successfully')

    # Step 2: Store data on data server
    data = "Hello, World!"  # Data to store
    data_msg = dservice_pb2.StoreReq(username=username, password=password, msg=data)
    res = d_stub.StoreData(data_msg)
    if not res.success:
        print('Failure when storing data')
    else:
        print(f'Data: {data} stored successfully')

    # Step 3: Generate one-time passcode from data server
    user_pass = dservice_pb2.UserPass(username=username, password=password)
    passcode = d_stub.GenPasscode(user_pass)
    print(f'Generated passcode: {passcode.code}')

    # Step 4: Request hash computation from hash server
    hash_request = hservice_pb2.Request(passcode=passcode.code, ip=data_ip, port=data_port)
    hash_response = h_stub.GetHash(hash_request)
    print(f'Received hash: {hash_response.hash}')
