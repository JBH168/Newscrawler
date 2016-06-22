-- Re-initalize DB-schema for the ccolon web-crawler
-- Updated: 11.06.2016 16:11

--
-- Table structure for table `ArchiveVersion`
--

DROP TABLE IF EXISTS `ArchiveVersion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ArchiveVersion` (
  `id` int(10) unsigned NOT NULL,
  `localPath` varchar(255) NOT NULL,
  `modifiedDate` datetime NOT NULL,
  `downloadDate` datetime NOT NULL,
  `sourceDomain` varchar(255) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `title` varchar(255) NOT NULL,
  `ancestor` int(10) unsigned DEFAULT NULL,
  `descendant` int(10) unsigned DEFAULT NULL,
  `version` int(10) unsigned NOT NULL,
  `rssTitle` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ArchiveVersion`
--

LOCK TABLES `ArchiveVersion` WRITE;
/*!40000 ALTER TABLE `ArchiveVersion` DISABLE KEYS */;
/*!40000 ALTER TABLE `ArchiveVersion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `CurrentVersion`
--

DROP TABLE IF EXISTS `CurrentVersion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `CurrentVersion` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `localPath` varchar(255) NOT NULL,
  `modifiedDate` datetime NOT NULL,
  `downloadDate` datetime NOT NULL,
  `sourceDomain` varchar(255) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `title` varchar(255) NOT NULL,
  `ancestor` int(10) unsigned DEFAULT NULL,
  `descendant` int(10) unsigned DEFAULT NULL,
  `version` int(10) unsigned NOT NULL,
  `rssTitle` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `CurrentVersion`
--

LOCK TABLES `CurrentVersion` WRITE;
/*!40000 ALTER TABLE `CurrentVersion` DISABLE KEYS */;
/*!40000 ALTER TABLE `CurrentVersion` ENABLE KEYS */;
UNLOCK TABLES;