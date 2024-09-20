cmake_minimum_required(VERSION 3.10)
project(dbow VERSION 1.0)

# Specify the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Add the external library
add_subdirectory(lib/fbow)

# Add your source files
file(GLOB_RECURSE SOURCES "src/*.cpp")

# Create the executable
add_executable(${PROJECT_NAME} ${SOURCES})

# Include directories
target_include_directories(${PROJECT_NAME} PRIVATE include)
target_include_directories(${PROJECT_NAME} PRIVATE lib/fbow/include)

# Link the external library
target_link_libraries(${PROJECT_NAME} PRIVATE fbow)