/*
Navicat MySQL Data Transfer

Source Server         : 的
Source Server Version : 50711
Source Host           : localhost:3306
Source Database       : python

Target Server Type    : MYSQL
Target Server Version : 50711
File Encoding         : 65001

Date: 2016-04-23 17:40:47
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for grade
-- ----------------------------
DROP TABLE IF EXISTS `grade`;
CREATE TABLE `grade` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `score` int(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `quize_id` varchar(20) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of grade
-- ----------------------------
INSERT INTO `grade` VALUES ('1', '1', '100', 'word_quize', '1', 'chenjing', '2016-04-06 16:52:21');
INSERT INTO `grade` VALUES ('2', null, '0', 'word_quize', '2', 'chenjing', '2016-04-13 16:52:26');
INSERT INTO `grade` VALUES ('3', null, '1', 'word_quize', '2,3,4', 'chenjing', '2016-04-13 16:52:30');
INSERT INTO `grade` VALUES ('4', null, '1', 'word_quize', '2,3,4', 'chenjing', '2016-04-13 16:52:34');
INSERT INTO `grade` VALUES ('5', null, '3', 'word_quize', '4', 'chenjing', '2016-04-20 16:52:39');
INSERT INTO `grade` VALUES ('6', null, '0', 'word_quize', '1,2,3,4', 'chenjing', '2016-04-13 16:53:41');
INSERT INTO `grade` VALUES ('7', null, '0', 'word_quize', '1,2,3,4', 'chenjing', '2016-04-19 16:53:51');
INSERT INTO `grade` VALUES ('8', null, '3', 'word_quize', '4', 'chenjing', '2016-04-07 16:53:56');
INSERT INTO `grade` VALUES ('9', null, '0', 'phrase_quize', '1', 'chenjing', '2016-04-21 16:54:04');
INSERT INTO `grade` VALUES ('10', null, '1', 'word_quize', '2,3,4', 'chenjing', '2016-04-15 16:54:12');
INSERT INTO `grade` VALUES ('11', null, '0', 'phrase_quize', '1,2', 'chenjing', '2016-04-13 16:54:45');
INSERT INTO `grade` VALUES ('12', null, '1', 'phrase_quize', '2', 'chenjing', '2016-04-06 16:54:53');
INSERT INTO `grade` VALUES ('13', null, '1', 'phrase_quize', '2', 'chenjing', '2016-04-10 16:54:57');
INSERT INTO `grade` VALUES ('14', null, '2', 'phrase_quize', '', 'chenjing', '2016-04-18 15:08:38');
INSERT INTO `grade` VALUES ('15', null, '2', 'phrase_quize', '', 'chenjing', '2016-04-18 15:08:36');
INSERT INTO `grade` VALUES ('16', null, '1', 'word_quize', '2,3,4', 'chenjing', '2016-04-18 17:45:33');

-- ----------------------------
-- Table structure for phrase_quize
-- ----------------------------
DROP TABLE IF EXISTS `phrase_quize`;
CREATE TABLE `phrase_quize` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `answer` varchar(255) DEFAULT NULL,
  `level` int(255) DEFAULT NULL,
  `question` varchar(255) DEFAULT NULL,
  `option` varchar(255) DEFAULT NULL,
  `type` int(11) DEFAULT NULL,
  `kind` varchar(255) DEFAULT NULL,
  `classify` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of phrase_quize
-- ----------------------------
INSERT INTO `phrase_quize` VALUES ('1', '1', '1', 'hello1222', 'A.B,B.hh,C.不会,Dno', '0', 'verb', 'GRE');
INSERT INTO `phrase_quize` VALUES ('2', '2', '1', '2', 'A.B,B.hh,C.不会,Dno', '0', 'obj', 'IESTL');

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `type` tinyint(255) DEFAULT NULL,
  `level` int(255) DEFAULT NULL,
  `teacherId` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES ('1', 'chenjing', 'chenjing', '1', '1', '3');
INSERT INTO `user` VALUES ('2', 'admin', 'admin', '0', null, null);
INSERT INTO `user` VALUES ('3', 'teacher', 'teacher', '2', null, null);
INSERT INTO `user` VALUES ('4', '1', '1', '1', null, null);
INSERT INTO `user` VALUES ('5', 'chenjing', 'chenjing', '0', null, null);

-- ----------------------------
-- Table structure for word_quize
-- ----------------------------
DROP TABLE IF EXISTS `word_quize`;
CREATE TABLE `word_quize` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `answer` varchar(255) DEFAULT NULL,
  `level` int(255) DEFAULT NULL,
  `question` varchar(255) DEFAULT NULL,
  `option` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of word_quize
-- ----------------------------
INSERT INTO `word_quize` VALUES ('1', '1', '1', 'h11ello是什么意思', 'A.B,B.hh,C.不会,Dno');
INSERT INTO `word_quize` VALUES ('2', '2', '1', 'a', 'A.B,B.hh,C.不会,Dno');
INSERT INTO `word_quize` VALUES ('3', '3', '1', 'b', 'A.B,B.hh,C.不会,Dno');
INSERT INTO `word_quize` VALUES ('4', '4', '1', 'hello', 'A.B,B.hh,C.不会,Dno');
INSERT INTO `word_quize` VALUES ('5', '1', '1', '1', 'A.1,B.1,C.1,D.1');
INSERT INTO `word_quize` VALUES ('6', '1', '1', '444', 'A.4,B.4,C.4,D.4');
INSERT INTO `word_quize` VALUES ('7', '3', '3', '1333', 'A.3,B.3,C.3,D.3');
