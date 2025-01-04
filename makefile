# Compiler
CXX = c++

# Automatically detect macOS version
MACOS_VERSION := $(shell sw_vers -productVersion | cut -d. -f1-2)

# Compiler flags
CXXFLAGS = -std=c++14 -O3 -Wall -Wextra -mmacosx-version-min=$(MACOS_VERSION)

# Include directories
INCLUDES = -I./llama/include

# Library directories
LIBDIRS = -L./llama/lib

# Libraries to link
LIBS = -lllama -lggml -lggml-base -lggml-cpu -lggml-blas -lggml-metal

# macOS specific flags and frameworks
LDFLAGS = -mmacosx-version-min=$(MACOS_VERSION) \
          -framework Foundation \
          -framework Metal \
          -framework MetalKit \
          -framework Accelerate

# Source and output directories
SRCDIR = src
BUILDDIR = build

# Target executable name
TARGET = $(BUILDDIR)/main.exe

# Source files
SOURCES = $(SRCDIR)/main.cpp

# Object files
OBJECTS = $(SOURCES:$(SRCDIR)/%.cpp=$(BUILDDIR)/%.o)

# Make sure the build directory exists
$(shell mkdir -p $(BUILDDIR))

# Main target
all: $(TARGET)

# Linking
$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $(TARGET) $(LIBDIRS) $(LIBS) $(LDFLAGS)

# Compilation
$(BUILDDIR)/%.o: $(SRCDIR)/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# Clean
clean:
	rm -rf $(BUILDDIR)

.PHONY: all clean
