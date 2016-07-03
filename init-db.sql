-- Re-initalize DB-schema for the ccolon web-crawler
-- Updated: 03.07.2016 14:00

--
-- Table structure for table `ArchiveVersion`
--

DROP TABLE IF EXISTS `ArchiveVersion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ArchiveVersion` (
  `id` int(10) unsigned NOT NULL,
  `local_path` varchar(255) NOT NULL,
  `modified_date` datetime NOT NULL,
  `download_date` datetime NOT NULL,
  `source_domain` varchar(255) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `html_title` varchar(255) NOT NULL,
  `ancestor` int(10) unsigned NOT NULL DEFAULT 0,
  `descendant` int(10) unsigned NOT NULL,
  `version` int(10) unsigned NOT NULL DEFAULT 2,
  `rss_title` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `CurrentVersion`
--

DROP TABLE IF EXISTS `CurrentVersion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `CurrentVersion` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `local_path` varchar(255) NOT NULL,
  `modified_date` datetime NOT NULL,
  `download_date` datetime NOT NULL,
  `source_domain` varchar(255) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `html_title` varchar(255) NOT NULL,
  `ancestor` int(10) unsigned NOT NULL DEFAULT 0,
  `descendant` int(10) unsigned NOT NULL DEFAULT 0,
  `version` int(10) unsigned NOT NULL DEFAULT 1,
  `rss_title` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
