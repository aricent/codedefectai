-- --------------------------------------------------------
-- Host:                         10.0.0.4
-- Server version:               10.1.38-MariaDB-0ubuntu0.18.04.1 - Ubuntu 18.04
-- Server OS:                    debian-linux-gnu
-- HeidiSQL Version:             9.5.0.5196
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Dumping database structure for cdp
CREATE DATABASE IF NOT EXISTS `cdp` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `cdp`;

-- Dumping structure for table cdp.explainablecdp
CREATE TABLE IF NOT EXISTS `explainablecdp` (
  `ExplainableCDPId` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `FeatureName` varchar(50) DEFAULT NULL,
  `FeatureKey` varchar(50) DEFAULT NULL,
  `FeatureValue` float DEFAULT NULL,
  `FeatureUnits` varchar(10) DEFAULT NULL,
  `FeatureLabel` int(11) NOT NULL,
  `FeatureCoefficient` double DEFAULT NULL,
  `PredictionListingId` int(10) unsigned NOT NULL,
  `CreateTimestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ProjectId` int(11) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`ExplainableCDPId`),
  KEY `FK_ExplainableCDP_predictionlisting` (`PredictionListingId`),
  KEY `FK_ExplainableCDP_projects` (`ProjectId`),
  CONSTRAINT `FK_ExplainableCDP_predictionlisting` FOREIGN KEY (`PredictionListingId`) REFERENCES `predictionlisting` (`PredictionListingId`),
  CONSTRAINT `FK_ExplainableCDP_projects` FOREIGN KEY (`ProjectId`) REFERENCES `projects` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table cdp.predctionfeaturetrend
CREATE TABLE IF NOT EXISTS `predctionfeaturetrend` (
  `featuretrendid` int(11) NOT NULL AUTO_INCREMENT,
  `Date` date DEFAULT NULL,
  `featurename` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `median` float DEFAULT NULL,
  `firstquartile` float DEFAULT NULL,
  `thirdquartile` float DEFAULT NULL,
  `minimum` float DEFAULT NULL,
  `maximum` float DEFAULT NULL,
  `prediction` int(11) DEFAULT NULL,
  `projectid` int(10) unsigned NOT NULL,
  `createtime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`featuretrendid`),
  KEY `FK__projects` (`projectid`),
  CONSTRAINT `FK__projects` FOREIGN KEY (`projectid`) REFERENCES `projects` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Data exporting was unselected.
-- Dumping structure for table cdp.predictionlisting
CREATE TABLE IF NOT EXISTS `predictionlisting` (
  `PredictionListingId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `COMMIT_ID` varchar(50) NOT NULL,
  `TimeStamp` datetime NOT NULL,
  `FILE_NAME` varchar(150) NOT NULL,
  `FILE_PARENT` varchar(255) NOT NULL,
  `FILE_STATUS` char(10) NOT NULL,
  `Prediction` tinyint(4) NOT NULL,
  `ConfidenceScore` float NOT NULL,
  `Project_Id` int(10) unsigned NOT NULL,
  KEY `Index 1` (`PredictionListingId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='prediction listing';

-- Data exporting was unselected.
-- Dumping structure for table cdp.predictionrawdata
CREATE TABLE IF NOT EXISTS `predictionrawdata` (
  `PredictionRawDataId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `DAY` date NOT NULL,
  `RAW_DATA` longtext,
  `ProjectId` int(10) unsigned NOT NULL DEFAULT '0',
  `TIMESTAMP` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`PredictionRawDataId`),
  UNIQUE KEY `Index 1` (`DAY`,`ProjectId`),
  KEY `FK_predictionrawdata_projects` (`ProjectId`),
  CONSTRAINT `FK_predictionrawdata_projects` FOREIGN KEY (`ProjectId`) REFERENCES `projects` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table cdp.projects
CREATE TABLE IF NOT EXISTS `projects` (
  `Id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ProjectName` varchar(50) NOT NULL,
  `GithubProjectName` varchar(50) NOT NULL,
  `CodingLanguage` varchar(50) NOT NULL,
  `Description` varchar(50) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='contains project details';

-- Data exporting was unselected.
-- Dumping structure for table cdp.projectsummary
CREATE TABLE IF NOT EXISTS `projectsummary` (
  `Id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ProjectId` int(10) unsigned NOT NULL,
  `TotalFilesForPrediction` int(11) NOT NULL,
  `TotalCommitsForPrediction` int(11) NOT NULL,
  `BuggyPredictions` int(11) NOT NULL,
  PRIMARY KEY (`Id`),
  KEY `FK__projectsummary__projects` (`ProjectId`),
  CONSTRAINT `FK__projectsummary__projects` FOREIGN KEY (`ProjectId`) REFERENCES `projects` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='contains project summary';

-- Data exporting was unselected.
-- Dumping structure for table cdp.scheduler
CREATE TABLE IF NOT EXISTS `scheduler` (
  `SchedulerId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `CronInterval` int(10) unsigned NOT NULL DEFAULT '0',
  `CreatedTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `UpdatedTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `JobName` varchar(50) NOT NULL DEFAULT '0',
  `Status` varchar(10) NOT NULL DEFAULT '0',
  `System` varchar(50) NOT NULL DEFAULT '0',
  PRIMARY KEY (`SchedulerId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;