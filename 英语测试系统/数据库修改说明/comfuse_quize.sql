/*
Navicat MySQL Data Transfer

Source Server         : 的
Source Server Version : 50711
Source Host           : localhost:3306
Source Database       : python

Target Server Type    : MYSQL
Target Server Version : 50711
File Encoding         : 65001

Date: 2016-05-24 12:51:56
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for confuse_quize
-- ----------------------------
DROP TABLE IF EXISTS `confuse_quize`;
CREATE TABLE `confuse_quize` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `answer` varchar(255) DEFAULT NULL,
  `level` int(255) DEFAULT NULL,
  `question` varchar(255) DEFAULT NULL,
  `option` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of grade
-- ----------------------------
INSERT INTO `confuse_quize` VALUES ('1', '1', '1', 'quite', 'A.相当,B.安静,C.不会,D.no');
INSERT INTO `confuse_quize` VALUES ('2', '2', '1', 'quiet', 'A.相当,B.安静,C.不会,D.no');

