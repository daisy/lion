-- MySQL dump 10.11
--
-- Host: localhost    Database: lionutf8
-- ------------------------------------------------------
-- Server version	5.0.67

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `application`
--

DROP TABLE IF EXISTS `application`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `application` (
  `name` varchar(255) NOT NULL,
  `version` varchar(255) default NULL,
  `description` text,
  `permanenturi` varchar(255) default NULL,
  `permanenturiparams` varchar(255) default NULL,
  `website` varchar(255) default NULL,
  `addldocsuri` varchar(255) default NULL,
  `addldocsdesc` text
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `application`
--

LOCK TABLES `application` WRITE;
/*!40000 ALTER TABLE `application` DISABLE KEYS */;
/*!40000 ALTER TABLE `application` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eng_US`
--

DROP TABLE IF EXISTS `eng_US`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `eng_US` (
  `id` int(10) unsigned NOT NULL default '0',
  `textstring` text character set utf8,
  `audiouri` varchar(255) character set utf8 default NULL,
  `textflag` int(11) default NULL,
  `remarks` text character set utf8,
  `xmlid` varchar(255) character set utf8 default NULL,
  `role` varchar(11) character set utf8 default NULL,
  `mnemonicgroup` int(11) default NULL,
  `target` varchar(4) character set utf8 default NULL,
  `actualkeys` varchar(100) character set utf8 default NULL,
  `translate` tinyint(1) default '1'
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `eng_US`
--

LOCK TABLES `eng_US` WRITE;
/*!40000 ALTER TABLE `eng_US` DISABLE KEYS */;
/*!40000 ALTER TABLE `eng_US` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `languages`
--

DROP TABLE IF EXISTS `languages`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `languages` (
  `langid` varchar(6) character set utf8 collate utf8_unicode_ci NOT NULL default '',
  `langname` varchar(50) character set utf8 collate utf8_unicode_ci default NULL,
  `audiodir` varchar(255) character set utf8 collate utf8_unicode_ci default NULL,
  `translate_for_keyboard` tinyint(1) default '1'
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `languages`
--

LOCK TABLES `languages` WRITE;
/*!40000 ALTER TABLE `languages` DISABLE KEYS */;
INSERT INTO `languages` VALUES ('eng-US','English (United States)',NULL,1);
/*!40000 ALTER TABLE `languages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `users` (
  `username` varchar(20) character set utf8 collate utf8_unicode_ci default NULL,
  `realname` varchar(100) character set utf8 collate utf8_unicode_ci default NULL,
  `password` varchar(20) character set utf8 collate utf8_unicode_ci default NULL,
  `email` varchar(50) character set utf8 collate utf8_unicode_ci default NULL,
  `langid` varchar(6) character set utf8 collate utf8_unicode_ci default NULL,
  `lastlogin` datetime default NULL,
  `lastactivity` datetime default NULL,
  `sessionid` varchar(36) character set utf8 collate utf8_unicode_ci default NULL,
  `id` int(11) NOT NULL default '0'
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('test','Test account','test',NULL,'eng-US',NULL,NULL,NULL,0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2008-10-08 10:34:02
