#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/point_types.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/filters/passthrough.h>

using PointT = pcl::PointXYZ;
using Cloud = pcl::PointCloud<PointT>;

class LidarProc : public rclcpp::Node {
public:
  LidarProc() : Node("lidar_proc") {
    // Settings you can change without recompiling
    auto in_topic  = declare_parameter<std::string>("input_topic", "/scan/points");
    auto out_topic = declare_parameter<std::string>("output_topic", "/scan/points_filtered");
    leaf_  = declare_parameter<double>("voxel_leaf", 0.05);
    min_z_ = declare_parameter<double>("min_z", -0.55);  // just above the floor
    max_z_ = declare_parameter<double>("max_z", 0.9);    // about 1.5 m above the floor

    sub_ = create_subscription<sensor_msgs::msg::PointCloud2>(
        in_topic, rclcpp::SensorDataQoS(),
        std::bind(&LidarProc::cb, this, std::placeholders::_1));
    pub_ = create_publisher<sensor_msgs::msg::PointCloud2>(out_topic, 10);
  }

private:
  void cb(const sensor_msgs::msg::PointCloud2::SharedPtr msg) {
    // 1. ROS message -> PCL cloud
    Cloud::Ptr cloud(new Cloud);
    pcl::fromROSMsg(*msg, *cloud);

    // 2. Keep only points between min_z and max_z (this also drops inf/NaN points)
    Cloud::Ptr band(new Cloud);
    pcl::PassThrough<PointT> pass;
    pass.setInputCloud(cloud);
    pass.setFilterFieldName("z");
    pass.setFilterLimits(min_z_, max_z_);
    pass.filter(*band);

    // 3. Shrink: one point per small cube
    Cloud::Ptr down(new Cloud);
    if (!band->empty()) {
      pcl::VoxelGrid<PointT> vg;
      vg.setInputCloud(band);
      vg.setLeafSize(leaf_, leaf_, leaf_);
      vg.filter(*down);
    }

    // 4. PCL cloud -> ROS message, keep the same frame and time
    sensor_msgs::msg::PointCloud2 out;
    pcl::toROSMsg(*down, out);
    out.header = msg->header;
    pub_->publish(out);
  }

  float leaf_;
  double min_z_, max_z_;
  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr sub_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr pub_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<LidarProc>());
  rclcpp::shutdown();
}