#!/usr/bin/env fish

# Store the initial working directory
set initial_pwd (pwd)

# Clone the repo into /tmp and checkout specific tag
cd /tmp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
git checkout b4409

# Build commands
cmake -S . -B build \
    -DBUILD_SHARED_LIBS=OFF \
    -DGGML_ACCELERATE=ON \
    -DGGML_METAL=ON \
    -DGGML_METAL_EMBED_LIBRARY=ON \
    -DLLAMA_METAL=ON \
    -DLLAMA_METAL_EMBED_LIBRARY=ON \
    -DGGML_BLAS=ON \
    -DGGML_BLAS_VENDOR=Apple

cmake --build build --config Release

# Install to ../llama relative to the original directory
cmake --install build --prefix "$initial_pwd/../llama"

# Return to original directory
cd $initial_pwd
