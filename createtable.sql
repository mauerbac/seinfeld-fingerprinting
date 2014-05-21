CREATE TABLE `episodes` (
  `episode_id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `episode_name` varchar(250) NOT NULL,
  `fingerprinted` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`episode_id`),
  UNIQUE KEY `episode_id` (`episode_id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;


CREATE TABLE `fingerprints` (
  `hash` binary(10) NOT NULL,
  `episode_id` mediumint(8) unsigned NOT NULL,
  `offset` int(10) unsigned NOT NULL,
  UNIQUE KEY `unique_constraint` (`episode_id`,`offset`,`hash`),
  KEY `hash` (`hash`),
  CONSTRAINT `fingerprints_ibfk_1` FOREIGN KEY (`episode_id`) REFERENCES `episodes` (`episode_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;