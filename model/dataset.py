import kagglehub

# Download latest version
path = kagglehub.dataset_download("kailaspsudheer/sarscope-unveiling-the-maritime-landscape")

print("Path to dataset files:", path)