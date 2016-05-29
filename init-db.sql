-- Re-initalize DB-schema for the ccolon web-crawler
-- Updated: 29.05.2016 17:49

--
-- Table structure for table `Heritage`
--

DROP TABLE IF EXISTS `Heritage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Heritage` (
  `id` int(10) unsigned NOT NULL,
  `version` smallint(5) unsigned NOT NULL,
  `ancestor` int(10) unsigned DEFAULT NULL,
  `decendant` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ancestor` (`ancestor`),
  KEY `decendant` (`decendant`),
  CONSTRAINT `Heritage_ibfk_1` FOREIGN KEY (`ancestor`) REFERENCES `Heritage` (`id`),
  CONSTRAINT `Heritage_ibfk_2` FOREIGN KEY (`decendant`) REFERENCES `Heritage` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Heritage`
--

LOCK TABLES `Heritage` WRITE;
/*!40000 ALTER TABLE `Heritage` DISABLE KEYS */;
/*!40000 ALTER TABLE `Heritage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MetaData`
--

DROP TABLE IF EXISTS `MetaData`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `MetaData` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `localPath` varchar(255) NOT NULL,
  `modifiedDate` datetime NOT NULL,
  `downloadDate` datetime NOT NULL,
  `sourceDomain` varchar(255) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `hashedName` varchar(32) NOT NULL,
  `title` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MetaData`
--

LOCK TABLES `MetaData` WRITE;
/*!40000 ALTER TABLE `MetaData` DISABLE KEYS */;
/*!40000 ALTER TABLE `MetaData` ENABLE KEYS */;
UNLOCK TABLES;
