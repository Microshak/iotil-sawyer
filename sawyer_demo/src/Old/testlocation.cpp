

#include <moveit/move_group_interface/move_group.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>

#include <moveit_msgs/DisplayRobotState.h>
#include <moveit_msgs/DisplayTrajectory.h>

#include <moveit_msgs/AttachedCollisionObject.h>
#include <moveit_msgs/CollisionObject.h>
#include <string>
#include <sstream>

int main(int argc, char **argv)
{
  ros::init(argc, argv, "move_group_interface_tutorial");
  ros::NodeHandle node_handle;  
  ros::AsyncSpinner spinner(1);
  spinner.start();

  bool verbos =false;

  /* This sleep is ONLY to allow Rviz to come up */
 // 
  
  moveit::planning_interface::MoveGroup group("right_arm");

  moveit::planning_interface::PlanningSceneInterface planning_scene_interface;  

  
  // (Optional) Create a publisher for visualizing plans in Rviz.
  ros::Publisher display_publisher = node_handle.advertise<moveit_msgs::DisplayTrajectory>("/move_group/display_planned_path", 1, true);
  moveit_msgs::DisplayTrajectory display_trajectory;

int x = 0;
while(x++<10)
{



 geometry_msgs::PoseStamped hi = group.getCurrentPose("right_gripper");

ROS_INFO("%.2f%% ",hi.pose.position.x);
ROS_INFO("%.2f%% ",hi.pose.position.y);
ROS_INFO("%.2f%% ",hi.pose.position.z);

ROS_INFO("%.2f%% ",hi.pose.orientation.x);
ROS_INFO("%.2f%% ",hi.pose.orientation.y);
ROS_INFO("%.2f%% ",hi.pose.orientation.z);
sleep(1.0);
}
  



  ros::shutdown();  
  return 0;
}

template <typename T>
  std::string NumberToString ( T Number )
  {
     std::ostringstream ss;
     ss << Number;
     return ss.str();
  }