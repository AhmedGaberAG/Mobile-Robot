import os
from os import pathsep
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    RegisterEventHandler,
)
from launch.event_handlers import OnProcessExit
from launch.substitutions import (
    Command,
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():

    # Package paths
    ddr_description = get_package_share_directory("ddr_description")

    rviz_path = os.path.join(get_package_share_directory("ddr_description"),
                          "rviz",
                          "ddr_description.rviz"
                        )

    gz_sim = os.path.join(get_package_share_directory("ros_gz_sim"),
                          "launch",
                          "gz_sim.launch.py"
                        )

    # Launch arguments
    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(
            ddr_description,
            "urdf",
            "ddr_description.urdf.xacro",
        ),
        description="Absolute path to robot Xacro file",
    )
    world_name_arg = DeclareLaunchArgument(
        name="world_name",
        default_value="empty",
        description="Gazebo world name",
    )

    # Gazebo world
    world_path = PathJoinSubstitution([
        ddr_description,
        "worlds",
        PythonExpression([
            "'",
            LaunchConfiguration("world_name"),
            "' + '.world'",
        ]),
    ])

    # Gazebo resource path
    model_path = str(Path(ddr_description).parent.resolve())
    model_path += pathsep + os.path.join(ddr_description, "models",)
    gazebo_resource_path = SetEnvironmentVariable(name="GZ_SIM_RESOURCE_PATH",
                                                  value=model_path,)
    # Gazebo bridge parameter
    bridge_config = os.path.join(
        ddr_description,
        "config",
        "gz_bridge.yaml",
    )

    # Robot description
    robot_description = ParameterValue(Command(["xacro ", LaunchConfiguration("model"),]), value_type=str)

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
                "robot_description": robot_description,
                "use_sim_time": True,
            }],
    )

    # Gazebo Sim
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_sim),
        launch_arguments={"gz_args": PythonExpression([
                          "'", world_path, " -v 4 -r'", ])}.items()
    )

    # Spawn robot into Gazebo
    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-topic", "robot_description",
            "-name", "ddr_robot",
        ]
    )

    # Gazebo <-> ROS 2 bridge
    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        output="screen",
        parameters=[{"config_file": bridge_config}]
    )

    # Controller spawners
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        output="screen",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager"
        ]
    )
    # simple_velocity_controller_spawner = Node( 
    #     package="controller_manager", 
    #     executable="spawner", 
    #     output="screen", 
    #     arguments=[ 
    #         "simple_velocity_controller", 
    #         "--controller-manager", 
    #         "/controller_manager" 
    #         ]
    #     )
    # ddr controller spawner
    ddr_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        output="screen",
        arguments=[
            "ddr_controller",
            "--controller-manager",
            "/controller_manager"
        ]
    )
    # Start controllers after robot is spawned
    load_joint_state_broadcaster = RegisterEventHandler(
        OnProcessExit(
            target_action=gz_spawn_entity,
            on_exit=[joint_state_broadcaster_spawner]
        )
    )
    load_ddr_controller = RegisterEventHandler(
        OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[ddr_controller_spawner]
        )
    )

    rviz2_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=['-d' , rviz_path],
        output="screen"
    )
    # Launch description
    return LaunchDescription([
        # Arguments
        model_arg,
        world_name_arg,
        # Environment
        gazebo_resource_path,
        # Robot
        robot_state_publisher_node,
        # Simulation
        gazebo,
        gz_spawn_entity,
        # ROS 2 interfaces
        gz_ros2_bridge,
        # Controllers
        load_joint_state_broadcaster,
        load_ddr_controller,
        #rviz2
        rviz2_node
    ])