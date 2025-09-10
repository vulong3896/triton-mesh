import numpy as np
import tritonclient.grpc as grpcclient

try:
    # Create a gRPC client instance
    client = grpcclient.InferenceServerClient(url="localhost:8011") # Default gRPC port

    # Check server readiness
    if not client.is_server_ready():
        print("Triton server is not ready.")
    else:
        print("Triton server is ready.")

    # Prepare input data (example for a model expecting a single input named 'input_tensor')
    input_data = np.random.rand(1, 3, 224, 224).astype(np.float32) # Example shape and datatype

    # Create InferInput objects
    infer_input = grpcclient.InferInput("input_tensor", input_data.shape, "FP32")
    infer_input.set_data_from_numpy(input_data)

    # Create InferRequestedOutput objects for desired outputs (example for 'output_tensor')
    infer_output = grpcclient.InferRequestedOutput("output_tensor")

    # Send inference request
    results = client.infer(
        model_name="ie_vbhc", # Replace with your model's name
        inputs=[infer_input],
        outputs=[infer_output]
    )

    # Get output data
    output_data = results.as_numpy("output_tensor")
    print("Inference successful. Output shape:", output_data.shape)

except Exception as e:
    print(f"An error occurred: {e}")