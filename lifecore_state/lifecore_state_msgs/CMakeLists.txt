cmake_minimum_required(VERSION 3.8)
project(lifecore_state_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(unique_identifier_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  msg/StateDescriptor.msg
  msg/StateDescription.msg
  msg/StateSample.msg
  msg/StateUpdate.msg
  DEPENDENCIES std_msgs unique_identifier_msgs
)

ament_package()
