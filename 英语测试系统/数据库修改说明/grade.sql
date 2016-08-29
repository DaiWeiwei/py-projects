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
-- Table structure for grade
-- ----------------------------
DROP TABLE IF EXISTS `grade`;
CREATE TABLE `grade` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `score` int(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `quize_id` varchar(20) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  `wrong_answer` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of grade
-- ----------------------------
INSERT INTO `grade` VALUES ('22', '3', 'word_quize', '4,3,2', 'chenjing', '2016-05-23 15:20:32', '1,1,1');
INSERT INTO `grade` VALUES ('23', '3', 'word_quize', '4,3,2', 'chenjing', '2016-05-23 15:27:28', '1,1,1');
INSERT INTO `grade` VALUES ('24', '3', 'word_quize', '2,4,3', 'chenjing', '2016-05-23 15:28:24', '1,1,1');
INSERT INTO `grade` VALUES ('25', '1', 'phrase_quize', '2', 'chenjing', '2016-05-23 15:51:52', '1');
