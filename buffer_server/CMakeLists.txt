cmake_minimum_required(VERSION 2.4)
project(buffer_server)
cmake_policy(SET CMP0015 NEW)


set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES main.cpp)

link_directories(../externals/build)

include_directories(../externals/cppcms-1.0.5/)
include_directories(../externals/cppcms-1.0.5/booster)
include_directories(../externals/build)
include_directories(../externals/build/booster)

add_executable(buffer_server ${SOURCE_FILES} include/handler.h src/handler.cpp)
target_link_libraries(${PROJECT_NAME} cppcms)