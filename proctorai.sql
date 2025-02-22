CREATE DATABASE IF NOT EXISTS `proctorai` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `proctorai`;

DROP TABLE IF EXISTS `reportlog`;
CREATE TABLE `reportlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `proctor` varchar(255) NOT NULL,
  `num_students` int NOT NULL,
  `block` varchar(255) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `room` varchar(255) NOT NULL,
  `start` TIME NOT NULL,
  `end` TIME NOT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
