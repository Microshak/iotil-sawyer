

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
 // sleep(20.0);
  
  moveit::planning_interface::MoveGroup group("right_arm");

  moveit::planning_interface::PlanningSceneInterface planning_scene_interface;  

  
  // (Optional) Create a publisher for visualizing plans in Rviz.
  ros::Publisher display_publisher = node_handle.advertise<moveit_msgs::DisplayTrajectory>("/move_group/display_planned_path", 1, true);
  moveit_msgs::DisplayTrajectory display_trajectory;
 if(verbos)
  { 
  ROS_INFO("Reference frame: %s", group.getPlanningFrame().c_str());
  
  ROS_INFO("Reference frame: %s", group.getEndEffectorLink().c_str());
}

  geometry_msgs::Pose target_pose1;
  target_pose1.orientation.w = 0.5;
  target_pose1.position.x = 0.5;
  target_pose1.position.y = 0.5;
  target_pose1.position.z = 0.5;
  target_pose1.orientation.x = 0.5;
  target_pose1.orientation.z = 0.5;
  
ROS_INFO("%.2f%% ",target_pose1.orientation.x);

 geometry_msgs::PoseStamped hi = group.getCurrentPose("right_gripper");
 robot_state::RobotState ahhh(*group.getCurrentState());
 

//group.setPoseTarget(target_pose1);
 // group.move() ;

  group.setJointValueTarget(target_pose1);



  // Now, we call the planner to compute the plan
  // and visualize it.
  // Note that we are just planning, not asking move_group 
  // to actually move the robot.
  moveit::planning_interface::MoveGroup::Plan my_plan;
  bool success = group.plan(my_plan);

  ROS_INFO("Visualizing plan 1 (pose goal) %s",success?"":"FAILED");    
  /* Sleep to give Rviz time to visualize the plan. */
  sleep(5.0);

  // Visualizing plans
  // ^^^^^^^^^^^^^^^^^
  // Now that we have a plan we can visualize it in Rviz.  This is not
  // necessary because the group.plan() call we made above did this
  // automatically.  But explicitly publishing plans is useful in cases that we
  // want to visualize a previously created plan.
  if (verbos)
  {
    ROS_INFO("Visualizing plan 1 (again)");    
    display_trajectory.trajectory_start = my_plan.start_state_;
    display_trajectory.trajectory.push_back(my_plan.trajectory_);
    display_publisher.publish(display_trajectory);
    /* Sleep to give Rviz time to visualize the plan. */
    sleep(5.0);
  }
  
   group.move() ;

// geometry_msgs::PoseStamped hi = group.getCurrentPose("right_gripper");
 //ROS_INFO("This is my X %s",.toString());
//std::string s = std::to_string(hi.pose.position.x);
//hi.pose.orientation.z;
ROS_INFO("%.2f%% ",hi.pose.position.z);

ROS_INFO("%.2f%% ",hi.pose.orientation.x);
ROS_INFO("%.2f%% ",hi.pose.orientation.y);
ROS_INFO("%.2f%% ",hi.pose.orientation.z);
   
  // Planning to a joint-space goal 
  // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  //
  // Let's set a joint space goal and move towards it.  This will replace the
  // pose target we set above.
  //
  // First get the current set of joint values for the group.
  std::vector<double> group_variable_values;
  group.getCurrentState()->copyJointGroupPositions(group.getCurrentState()->getRobotModel()->getJointModelGroup(group.getName()), group_variable_values);
  
hi = group.getCurrentPose();

ROS_INFO("%.2f%% ",hi.pose.position.z);

ROS_INFO("%.2f%% ",hi.pose.orientation.x);
ROS_INFO("%.2f%% ",hi.pose.orientation.y);
ROS_INFO("%.2f%% ",hi.pose.orientation.z);
  ros::shutdown();  
  return 0;


  // Now, let's modify one of the joints, plan to the new joint
  // space goal and visualize the plan.
  group_variable_values[0] = -0.5;  
  group.setJointValueTarget(group_variable_values);
  success = group.plan(my_plan);

  ROS_INFO("Visualizing plan 2 (joint space goal) %s",success?"":"FAILED");
  /* Sleep to give Rviz time to visualize the plan. */
  sleep(5.0);

  // Planning with Path Constraints
  // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  //
  // Path constraints can easily be specified for a link on the robot.
  // Let's specify a path constraint and a pose goal for our group.
  // First define the path constraint.
  moveit_msgs::OrientationConstraint ocm;  
  ocm.link_name = "r_wrist_roll_link";  
  ocm.header.frame_id = "base_link";
  ocm.orientation.w = 0.5;
  ocm.absolute_x_axis_tolerance = 0.1;
  ocm.absolute_y_axis_tolerance = 0.1;
  ocm.absolute_z_axis_tolerance = 0.1;
  ocm.weight = 0.5;
  
  // Now, set it as the path constraint for the group.
  moveit_msgs::Constraints test_constraints;
  test_constraints.orientation_constraints.push_back(ocm);  
  group.setPathConstraints(test_constraints);
  group.move();
  // We will reuse the old goal that we had and plan to it.
  // Note that this will only work if the current state already 
  // satisfies the path constraints. So, we need to set the start
  // state to a new pose. 
  robot_state::RobotState start_state(*group.getCurrentState());
  geometry_msgs::Pose start_pose2;
  start_pose2.orientation.w = 0.5;
  start_pose2.position.x = 0.55;
  start_pose2.position.y = -0.05;
  start_pose2.position.z = 0.8;
  const robot_state::JointModelGroup *joint_model_group =
                  start_state.getJointModelGroup(group.getName());
  start_state.setFromIK(joint_model_group, start_pose2);
  group.setStartState(start_state);
  
  // Now we will plan to the earlier pose target from the new 
  // start state that we have just created.
  group.setPoseTarget(target_pose1);
  success = group.plan(my_plan);

  ROS_INFO("Visualizing plan 3 (constraints) %s",success?"":"FAILED");
  /* Sleep to give Rviz time to visualize the plan. */
  sleep(10.0);

  // When done with the path constraint be sure to clear it.
  group.clearPathConstraints();

  // Cartesian Paths
  // ^^^^^^^^^^^^^^^
  // You can plan a cartesian path directly by specifying a list of waypoints 
  // for the end-effector to go through. Note that we are starting 
  // from the new start state above.  The initial pose (start state) does not
  // need to be added to the waypoint list.
  std::vector<geometry_msgs::Pose> waypoints;

  geometry_msgs::Pose target_pose3 = start_pose2;
  target_pose3.position.x += 0.2;
  target_pose3.position.z += 0.2;
  waypoints.push_back(target_pose3);  // up and out

  target_pose3.position.y -= 0.2;
  waypoints.push_back(target_pose3);  // left

  target_pose3.position.z -= 0.2;
  target_pose3.position.y += 0.2;
  target_pose3.position.x -= 0.2;
  waypoints.push_back(target_pose3);  // down and right (back to start)

  // We want the cartesian path to be interpolated at a resolution of 1 cm
  // which is why we will specify 0.01 as the max step in cartesian
  // translation.  We will specify the jump threshold as 0.0, effectively
  // disabling it.
  moveit_msgs::RobotTrajectory trajectory;
  double fraction = group.computeCartesianPath(waypoints,
                                               0.01,  // eef_step
                                               0.0,   // jump_threshold
                                               trajectory);

  ROS_INFO("Visualizing plan 4 (cartesian path) (%.2f%% acheived)",
        fraction * 100.0);    
  /* Sleep to give Rviz time to visualize the plan. */
  sleep(15.0);


  // Adding/Removing Objects and Attaching/Detaching Objects
  // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  // First, we will define the collision object message.
  moveit_msgs::CollisionObject collision_object;
  collision_object.header.frame_id = group.getPlanningFrame();

  /* The id of the object is used to identify it. */
  collision_object.id = "box1";

  /* Define a box to add to the world. */
  shape_msgs::SolidPrimitive primitive;
  primitive.type = primitive.BOX;
  primitive.dimensions.resize(3);
  primitive.dimensions[0] = 0.4;
  primitive.dimensions[1] = 0.1;
  primitive.dimensions[2] = 0.4;

  /* A pose for the box (specified relative to frame_id) */
  geometry_msgs::Pose box_pose;
  box_pose.orientation.w = 0.5;
  box_pose.position.x =  0.6;
  box_pose.position.y = -0.4;
  box_pose.position.z =  1.2;

  collision_object.primitives.push_back(primitive);
  collision_object.primitive_poses.push_back(box_pose);
  collision_object.operation = collision_object.ADD;

  std::vector<moveit_msgs::CollisionObject> collision_objects;  
  collision_objects.push_back(collision_object);  

  // Now, let's add the collision object into the world
  ROS_INFO("Add an object into the world");  
  planning_scene_interface.addCollisionObjects(collision_objects);
  
  /* Sleep so we have time to see the object in RViz */
  sleep(2.0);

  // Planning with collision detection can be slow.  Lets set the planning time
  // to be sure the planner has enough time to plan around the box.  10 seconds
  // should be plenty.
  group.setPlanningTime(10.0);


  // Now when we plan a trajectory it will avoid the obstacle
  group.setStartState(*group.getCurrentState());
  group.setPoseTarget(target_pose1);
  success = group.plan(my_plan);

  ROS_INFO("Visualizing plan 5 (pose goal move around box) %s",
    success?"":"FAILED");
  /* Sleep to give Rviz time to visualize the plan. */
  sleep(10.0);
  

  // Now, let's attach the collision object to the robot.
  ROS_INFO("Attach the object to the robot");  
  group.attachObject(collision_object.id);  
  /* Sleep to give Rviz time to show the object attached (different color). */
  sleep(4.0);


  // Now, let's detach the collision object from the robot.
  ROS_INFO("Detach the object from the robot");  
  group.detachObject(collision_object.id);  
  /* Sleep to give Rviz time to show the object detached. */
  sleep(4.0);


  // Now, let's remove the collision object from the world.
  ROS_INFO("Remove the object from the world");  
  std::vector<std::string> object_ids;
  object_ids.push_back(collision_object.id);  
  planning_scene_interface.removeCollisionObjects(object_ids);
  /* Sleep to give Rviz time to show the object is no longer there. */
  sleep(4.0);


  // Dual-arm pose goals
  // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  // First define a new group for addressing the two arms. Then define 
  // two separate pose goals, one for each end-effector. Note that 
  // we are reusing the goal for the right arm above
  moveit::planning_interface::MoveGroup two_arms_group("arms");

  two_arms_group.setPoseTarget(target_pose1, "r_wrist_roll_link");

  geometry_msgs::Pose target_pose2;
  target_pose2.orientation.w = 0.5;
  target_pose2.position.x = 0.7;
  target_pose2.position.y = 0.15;
  target_pose2.position.z = 0.5;

  two_arms_group.setPoseTarget(target_pose2, "l_wrist_roll_link");

  // Now, we can plan and visualize
  moveit::planning_interface::MoveGroup::Plan two_arms_plan;
  two_arms_group.plan(two_arms_plan);
  sleep(4.0);

// END_TUTORIAL

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