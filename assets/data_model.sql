-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: xtrack
-- ------------------------------------------------------
-- Server version	8.0.34

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `annotation`
--

DROP TABLE IF EXISTS `annotation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `annotation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(200) DEFAULT NULL,
  `probability` double DEFAULT NULL,
  `normalized_text` varchar(400) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `type` (`type`),
  KEY `normalized_text` (`normalized_text`)
) ENGINE=InnoDB AUTO_INCREMENT=187626 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `annotation_prediction_tweet`
--

DROP TABLE IF EXISTS `annotation_prediction_tweet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `annotation_prediction_tweet` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tweet_id` int NOT NULL,
  `annotation_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_id` (`tweet_id`),
  KEY `annotation_id` (`annotation_id`),
  CONSTRAINT `annotation_prediction_tweet_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `annotation_prediction_tweet_ibfk_2` FOREIGN KEY (`annotation_id`) REFERENCES `annotation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11345205 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `annotation_tweet`
--

DROP TABLE IF EXISTS `annotation_tweet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `annotation_tweet` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tweet_id` int NOT NULL,
  `domain_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_id` (`tweet_id`),
  KEY `domain_id` (`domain_id`),
  CONSTRAINT `annotation_tweet_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `annotation_tweet_ibfk_2` FOREIGN KEY (`domain_id`) REFERENCES `domain` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8121870 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `campaign_analysis`
--

DROP TABLE IF EXISTS `campaign_analysis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `campaign_analysis` (
  `id` int NOT NULL,
  `campaign` varchar(200) DEFAULT NULL,
  `hashtags` varchar(400) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_campaign_analysis_campaign` (`campaign`) /*!80000 INVISIBLE */,
  KEY `idx_campaign_analysis_hashtags` (`hashtags`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domain`
--

DROP TABLE IF EXISTS `domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `domain` (
  `id` int NOT NULL AUTO_INCREMENT,
  `annotation_id` varchar(400) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(250) DEFAULT NULL,
  `description` text,
  `category` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `category` (`category`),
  KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=18153 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `emotion`
--

DROP TABLE IF EXISTS `emotion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emotion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tweet_id` int NOT NULL,
  `anger` float NOT NULL,
  `disgust` float NOT NULL,
  `fear` float NOT NULL,
  `joy` float NOT NULL,
  `sadness` float NOT NULL,
  `surprise` float NOT NULL,
  `others` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tweet_id_UNIQUE` (`tweet_id`)
) ENGINE=InnoDB AUTO_INCREMENT=470518 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `emotion_analysis_results`
--

DROP TABLE IF EXISTS `emotion_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emotion_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `emotion` varchar(10) NOT NULL,
  `probability` float NOT NULL,
  `language` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `emotion_campaign_analysis_id` (`campaign_analysis_id`),
  KEY `idx_emotion_language` (`language`),
  CONSTRAINT `emotion_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hashtag`
--

DROP TABLE IF EXISTS `hashtag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hashtag` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hashtag` varchar(250) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `hashtag` (`hashtag`)
) ENGINE=InnoDB AUTO_INCREMENT=210510 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hashtagt_tweet`
--

DROP TABLE IF EXISTS `hashtagt_tweet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hashtagt_tweet` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hashtag_id` int NOT NULL,
  `tweet_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_id` (`tweet_id`),
  KEY `hashtagt_tweet_ibfk_2` (`hashtag_id`),
  CONSTRAINT `hashtagt_tweet_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `hashtagt_tweet_ibfk_2` FOREIGN KEY (`hashtag_id`) REFERENCES `hashtag` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7287359 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hate_speech`
--

DROP TABLE IF EXISTS `hate_speech`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hate_speech` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tweet_id` int NOT NULL,
  `hate` double NOT NULL,
  `non_hate` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_id` (`tweet_id`),
  CONSTRAINT `hate_speech_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11118069 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lda_topics_analysis_results`
--

DROP TABLE IF EXISTS `lda_topics_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lda_topics_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `word` text,
  `probability` float NOT NULL,
  `topic` int NOT NULL,
  `spacy_model_name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `lda_topics_campaign_analysis_id` (`campaign_analysis_id`),
  KEY `idx_lda_topics_spacy_model_name` (`spacy_model_name`),
  CONSTRAINT `lda_topics_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `liwc_2007`
--

DROP TABLE IF EXISTS `liwc_2007`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `liwc_2007` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Funct` int DEFAULT NULL,
  `TotPron` int DEFAULT NULL,
  `Yo` int DEFAULT NULL,
  `PronPer` int DEFAULT NULL,
  `Nosotro` int DEFAULT NULL,
  `TuUtd` int DEFAULT NULL,
  `ElElla` int DEFAULT NULL,
  `Ellos` int DEFAULT NULL,
  `PronImp` int DEFAULT NULL,
  `Articulo` int DEFAULT NULL,
  `Verbos` int DEFAULT NULL,
  `VerbAux` int DEFAULT NULL,
  `Pasado` int DEFAULT NULL,
  `Present` int DEFAULT NULL,
  `Futuro` int DEFAULT NULL,
  `Adverb` int DEFAULT NULL,
  `Prepos` int DEFAULT NULL,
  `Conjunc` int DEFAULT NULL,
  `Negacio` int DEFAULT NULL,
  `Cuantif` int DEFAULT NULL,
  `Numeros` int DEFAULT NULL,
  `Maldec` int DEFAULT NULL,
  `verbYO` int DEFAULT NULL,
  `verbTU` int DEFAULT NULL,
  `verbNOS` int DEFAULT NULL,
  `verbosEL` int DEFAULT NULL,
  `verbELLOS` int DEFAULT NULL,
  `Subjuntiv` int DEFAULT NULL,
  `VosUtds` int DEFAULT NULL,
  `formal` int DEFAULT NULL,
  `informal` int DEFAULT NULL,
  `verbVos` int DEFAULT NULL,
  `Social` int DEFAULT NULL,
  `Familia` int DEFAULT NULL,
  `Amigos` int DEFAULT NULL,
  `Humanos` int DEFAULT NULL,
  `Afect` int DEFAULT NULL,
  `EmoPos` int DEFAULT NULL,
  `EmoNeg` int DEFAULT NULL,
  `Ansiedad` int DEFAULT NULL,
  `Enfado` int DEFAULT NULL,
  `Triste` int DEFAULT NULL,
  `MecCog` int DEFAULT NULL,
  `Insight` int DEFAULT NULL,
  `Causa` int DEFAULT NULL,
  `Discrep` int DEFAULT NULL,
  `Tentat` int DEFAULT NULL,
  `Certeza` int DEFAULT NULL,
  `Inhib` int DEFAULT NULL,
  `Incl` int DEFAULT NULL,
  `Excl` int DEFAULT NULL,
  `Percept` int DEFAULT NULL,
  `Ver` int DEFAULT NULL,
  `Oir` int DEFAULT NULL,
  `Sentir` int DEFAULT NULL,
  `Biolog` int DEFAULT NULL,
  `Cuerpo` int DEFAULT NULL,
  `Salud` int DEFAULT NULL,
  `Sexual` int DEFAULT NULL,
  `Ingerir` int DEFAULT NULL,
  `Relativ` int DEFAULT NULL,
  `Movim` int DEFAULT NULL,
  `Espacio` int DEFAULT NULL,
  `Tiempo` int DEFAULT NULL,
  `Trabajo` int DEFAULT NULL,
  `Logro` int DEFAULT NULL,
  `Placer` int DEFAULT NULL,
  `Hogar` int DEFAULT NULL,
  `Dinero` int DEFAULT NULL,
  `Relig` int DEFAULT NULL,
  `Muerte` int DEFAULT NULL,
  `Asentir` int DEFAULT NULL,
  `NoFluen` int DEFAULT NULL,
  `Relleno` int DEFAULT NULL,
  `tweet_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_id` (`tweet_id`),
  CONSTRAINT `liwc_2007_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3435672 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `liwc_2015`
--

DROP TABLE IF EXISTS `liwc_2015`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `liwc_2015` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tweet_id` int NOT NULL,
  `pronoun` int DEFAULT NULL,
  `ppron` int DEFAULT NULL,
  `i` int DEFAULT NULL,
  `we` int DEFAULT NULL,
  `you` int DEFAULT NULL,
  `shehe` int DEFAULT NULL,
  `they` int DEFAULT NULL,
  `ipron` int DEFAULT NULL,
  `article` int DEFAULT NULL,
  `prep` int DEFAULT NULL,
  `auxverb` int DEFAULT NULL,
  `adverb` int DEFAULT NULL,
  `conj` int DEFAULT NULL,
  `negate` int DEFAULT NULL,
  `othergram` int DEFAULT NULL,
  `verb` int DEFAULT NULL,
  `adj` int DEFAULT NULL,
  `compare` int DEFAULT NULL,
  `interrog` int DEFAULT NULL,
  `number` int DEFAULT NULL,
  `quant` int DEFAULT NULL,
  `affect` int DEFAULT NULL,
  `posemo` int DEFAULT NULL,
  `negemo` int DEFAULT NULL,
  `anx` int DEFAULT NULL,
  `anger` int DEFAULT NULL,
  `sad` int DEFAULT NULL,
  `social` int DEFAULT NULL,
  `family` int DEFAULT NULL,
  `friend` int DEFAULT NULL,
  `female` int DEFAULT NULL,
  `male` int DEFAULT NULL,
  `cogproc` int DEFAULT NULL,
  `insight` int DEFAULT NULL,
  `cause` int DEFAULT NULL,
  `discrep` int DEFAULT NULL,
  `tentat` int DEFAULT NULL,
  `certain` int DEFAULT NULL,
  `differ` int DEFAULT NULL,
  `percept` int DEFAULT NULL,
  `see` int DEFAULT NULL,
  `hear` int DEFAULT NULL,
  `feel` int DEFAULT NULL,
  `bio` int DEFAULT NULL,
  `body` int DEFAULT NULL,
  `health` int DEFAULT NULL,
  `sexual` int DEFAULT NULL,
  `ingest` int DEFAULT NULL,
  `drives` int DEFAULT NULL,
  `affiliation` int DEFAULT NULL,
  `achieve` int DEFAULT NULL,
  `power` int DEFAULT NULL,
  `reward` int DEFAULT NULL,
  `risk` int DEFAULT NULL,
  `timeorient` int DEFAULT NULL,
  `focuspast` int DEFAULT NULL,
  `focuspresent` int DEFAULT NULL,
  `focusfuture` int DEFAULT NULL,
  `relativ` int DEFAULT NULL,
  `motion` int DEFAULT NULL,
  `space` int DEFAULT NULL,
  `time` int DEFAULT NULL,
  `persconc` int DEFAULT NULL,
  `work` int DEFAULT NULL,
  `leisure` int DEFAULT NULL,
  `home` int DEFAULT NULL,
  `money` int DEFAULT NULL,
  `relig` int DEFAULT NULL,
  `death` int DEFAULT NULL,
  `informal` int DEFAULT NULL,
  `swear` int DEFAULT NULL,
  `netspeak` int DEFAULT NULL,
  `assent` int DEFAULT NULL,
  `nonflu` int DEFAULT NULL,
  `filler` int DEFAULT NULL,
  `funct` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_id` (`tweet_id`),
  CONSTRAINT `liwc_2015_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `liwc_analysis_results`
--

DROP TABLE IF EXISTS `liwc_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `liwc_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `liwc_category` varchar(10) NOT NULL,
  `frequency` float NOT NULL,
  `liwc_dict` varchar(500) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `liwc_campaign_analysis_id` (`campaign_analysis_id`),
  KEY `idx_liwc_dict` (`liwc_dict`),
  CONSTRAINT `liwc_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `media_domain_analysis_results`
--

DROP TABLE IF EXISTS `media_domain_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `media_domain_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `domain` varchar(300) NOT NULL,
  `frequency` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_media_domain_campaign_analysis_id` (`campaign_analysis_id`),
  CONSTRAINT `fk_media_domain_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `media_headline_analysis_results`
--

DROP TABLE IF EXISTS `media_headline_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `media_headline_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `headline` text NOT NULL,
  `frequency` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_media_headline_campaign_analysis_id` (`campaign_analysis_id`),
  CONSTRAINT `fk_media_headline_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mention`
--

DROP TABLE IF EXISTS `mention`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mention` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tweet_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_id` (`tweet_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `mention_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `mention_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12787763 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `motto_analysis_results`
--

DROP TABLE IF EXISTS `motto_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `motto_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `motto` varchar(250) NOT NULL,
  `frequency` int NOT NULL,
  `sentiment` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_campaign_analysis_id` (`campaign_analysis_id`),
  KEY `idx_sentiment` (`sentiment`),
  CONSTRAINT `fk_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `network_analysis_results`
--

DROP TABLE IF EXISTS `network_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `network_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `source` varchar(300) NOT NULL,
  `target` varchar(300) NOT NULL,
  `weight` int NOT NULL,
  `source_sentiment` float NOT NULL,
  `source_activity` float NOT NULL,
  `target_sentiment` float NOT NULL,
  `target_activity` float NOT NULL,
  `network_type` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `network_campaign_analysis_id` (`campaign_analysis_id`),
  KEY `idx_network_network_type` (`network_type`),
  CONSTRAINT `network_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=172 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `network_metric_analysis_results`
--

DROP TABLE IF EXISTS `network_metric_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `network_metric_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `network_metric` varchar(30) NOT NULL,
  `value` float NOT NULL,
  `date` date NOT NULL,
  `network_type` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `network_metric_campaign_analysis_id` (`campaign_analysis_id`),
  KEY `idx_network_metric_network_type` (`network_type`),
  KEY `idx_network_metric_metric_name` (`network_metric`),
  CONSTRAINT `network_metric_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quoted`
--

DROP TABLE IF EXISTS `quoted`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quoted` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tweet_id` int NOT NULL,
  `quoted` varchar(400) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_id` (`tweet_id`),
  KEY `quoted` (`quoted`),
  CONSTRAINT `quoted_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=221027 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reply`
--

DROP TABLE IF EXISTS `reply`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reply` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tweet_id` int NOT NULL,
  `reply_to` varchar(400) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_id` (`tweet_id`),
  KEY `reply_to` (`reply_to`),
  CONSTRAINT `reply_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1029771 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `retweet`
--

DROP TABLE IF EXISTS `retweet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `retweet` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tweet_id` int NOT NULL,
  `retweeted` varchar(250) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `retweeted` (`retweeted`),
  KEY `tweet_id` (`tweet_id`),
  CONSTRAINT `retweet_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8391826 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sentiment`
--

DROP TABLE IF EXISTS `sentiment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sentiment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tweet_id` int NOT NULL,
  `positive` float NOT NULL,
  `negative` float NOT NULL,
  `neutral` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tweet_id_UNIQUE` (`tweet_id`),
  CONSTRAINT `fk_sentiment_tweet_tweet_id` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=470518 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sentiment_analysis_results`
--

DROP TABLE IF EXISTS `sentiment_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sentiment_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `sentiment` varchar(10) NOT NULL,
  `probability` float NOT NULL,
  `language` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sentiment_campaign_analysis_id` (`campaign_analysis_id`),
  KEY `idx_sentiment_language` (`language`),
  CONSTRAINT `sentiment_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `topic_assignment_analysis_results`
--

DROP TABLE IF EXISTS `topic_assignment_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `topic_assignment_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `tweet_text` text,
  `impact` int NOT NULL,
  `topic` int NOT NULL,
  `topic_x_coord` float NOT NULL,
  `topic_y_coord` float NOT NULL,
  `topic_tags` varchar(100) NOT NULL,
  `spacy_model_name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `topic_campaign_analysis_id` (`campaign_analysis_id`),
  KEY `idx_topic_spacy_model_name` (`spacy_model_name`),
  CONSTRAINT `topic_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=434463 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tweet`
--

DROP TABLE IF EXISTS `tweet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tweet` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tweet_id` varchar(200) NOT NULL,
  `source` varchar(200) DEFAULT NULL,
  `reply_settings` varchar(200) DEFAULT NULL,
  `possibly_sensitive` tinyint(1) DEFAULT NULL,
  `author_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `lang` varchar(4) DEFAULT NULL,
  `conversation_id` varchar(200) DEFAULT NULL,
  `text` varchar(800) NOT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `trending_topic` varchar(200) NOT NULL,
  `campaign` varchar(200) NOT NULL,
  `in_reply_to_user_id` varchar(250) DEFAULT NULL,
  `mentions_psoe` tinyint(1) DEFAULT NULL,
  `mentions_pp` tinyint(1) DEFAULT NULL,
  `mentions_vox` tinyint(1) DEFAULT NULL,
  `mentions_liberal` tinyint(1) DEFAULT NULL,
  `mentions_conservative` tinyint(1) DEFAULT NULL,
  `mentions_podemos` tinyint(1) DEFAULT NULL,
  `mentions_communism` tinyint(1) DEFAULT NULL,
  `mentions_gender` tinyint(1) DEFAULT NULL,
  `mentions_cs` tinyint(1) DEFAULT NULL,
  `mentions_independentism` tinyint(1) DEFAULT NULL,
  `mentions_spain` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `campaign` (`campaign`),
  KEY `trending_topic` (`trending_topic`),
  KEY `conversation_id` (`conversation_id`),
  KEY `tweet_id` (`tweet_id`),
  KEY `author_id` (`author_id`),
  KEY `in_reply_to_user_id` (`in_reply_to_user_id`),
  CONSTRAINT `tweet_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11118073 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tweet_creation_time_analysis_results`
--

DROP TABLE IF EXISTS `tweet_creation_time_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tweet_creation_time_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `dayhour` varchar(30) NOT NULL,
  `tweet_volume` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_creation_time_analysis_campaign_analysis_id` (`campaign_analysis_id`),
  CONSTRAINT `tweet_creation_time_analysis_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=133 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tweet_entity_analysis_results`
--

DROP TABLE IF EXISTS `tweet_entity_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tweet_entity_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `category` varchar(250) NOT NULL,
  `entity` varchar(250) NOT NULL,
  `frequency` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_entity_analysis_campaign_analysis_id` (`campaign_analysis_id`),
  CONSTRAINT `tweet_entity_analysis_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tweet_impact_analysis_results`
--

DROP TABLE IF EXISTS `tweet_impact_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tweet_impact_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `tweet` text NOT NULL,
  `user` varchar(300) NOT NULL,
  `impact` int NOT NULL,
  `tweet_impact_mode` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_impact_campaign_analysis_id` (`campaign_analysis_id`),
  KEY `idx_tweet_impact_mode` (`tweet_impact_mode`),
  CONSTRAINT `tweet_impact_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tweet_language_analysis_results`
--

DROP TABLE IF EXISTS `tweet_language_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tweet_language_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `language` varchar(10) NOT NULL,
  `tweet_volume` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_language_campaign_analysis_id` (`campaign_analysis_id`),
  CONSTRAINT `tweet_language_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tweet_metrics`
--

DROP TABLE IF EXISTS `tweet_metrics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tweet_metrics` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tweet_id` int NOT NULL,
  `date` datetime DEFAULT CURRENT_TIMESTAMP,
  `retweet_count` int NOT NULL,
  `reply_count` int NOT NULL,
  `like_count` int NOT NULL,
  `quote_count` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_id` (`tweet_id`),
  CONSTRAINT `tweet_metrics_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11118070 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tweet_redundancy_analysis_results`
--

DROP TABLE IF EXISTS `tweet_redundancy_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tweet_redundancy_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `tweet` text NOT NULL,
  `user` varchar(300) NOT NULL,
  `frequency` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_redundancy_campaign_analysis_id` (`campaign_analysis_id`),
  CONSTRAINT `tweet_redundancy_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tweet_sentiment_creation_time_analysis_results`
--

DROP TABLE IF EXISTS `tweet_sentiment_creation_time_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tweet_sentiment_creation_time_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `dayhour` varchar(30) NOT NULL,
  `tweet_volume` int NOT NULL,
  `sentiment` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_sentiment_creation_time_analysis_campaign_analysis_id` (`campaign_analysis_id`),
  KEY `idx_tweet_sentiment_creation` (`sentiment`),
  CONSTRAINT `tweet_sentiment_creation_time_analysis_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=265 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tweet_wordcloud_analysis_results`
--

DROP TABLE IF EXISTS `tweet_wordcloud_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tweet_wordcloud_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `tweet_text` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_wordcloud_analysis_campaign_analysis_id` (`campaign_analysis_id`),
  CONSTRAINT `tweet_wordcloud_analysis_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=470518 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `url`
--

DROP TABLE IF EXISTS `url`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `url` (
  `id` int NOT NULL AUTO_INCREMENT,
  `url` varchar(400) NOT NULL,
  `expanded_url` text,
  `domain` varchar(300) DEFAULT NULL,
  `title` text,
  `description` text,
  `unwound_url` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1328868 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `url_tweet`
--

DROP TABLE IF EXISTS `url_tweet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `url_tweet` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tweet_id` int NOT NULL,
  `url_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tweet_id` (`tweet_id`),
  KEY `url_id` (`url_id`),
  CONSTRAINT `url_tweet_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `url_tweet_ibfk_2` FOREIGN KEY (`url_id`) REFERENCES `url` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3182017 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `user_id` varchar(200) NOT NULL,
  `description` text,
  `creation_date` datetime DEFAULT NULL,
  `followers_num` int DEFAULT NULL,
  `following_num` int DEFAULT NULL,
  `url` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `location` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_user_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2678361 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_account_creation_analysis_results`
--

DROP TABLE IF EXISTS `user_account_creation_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_account_creation_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `month` varchar(300) NOT NULL,
  `accounts` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_account_creation_analysis__campaign_analysis_id` (`campaign_analysis_id`),
  CONSTRAINT `user_account_creation_analysis__campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_bot_analysis_results`
--

DROP TABLE IF EXISTS `user_bot_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_bot_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `bot` varchar(10) NOT NULL,
  `frequency` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_bot_analysis_campaign_analysis_id` (`campaign_analysis_id`),
  CONSTRAINT `user_bot_analysis_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_botometer`
--

DROP TABLE IF EXISTS `user_botometer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_botometer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `bot_score` float NOT NULL,
  `bot` tinyint NOT NULL,
  `retrieved_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_user_botometer_user_user_id_idx` (`user_id`),
  CONSTRAINT `fk_user_botometer_user_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=742 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_influence_analysis_results`
--

DROP TABLE IF EXISTS `user_influence_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_influence_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `user` varchar(300) NOT NULL,
  `top_k_appareances` int NOT NULL,
  `network_type` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_influence_analysis_campaign_analysis_id` (`campaign_analysis_id`),
  KEY `idx_network_type` (`network_type`),
  CONSTRAINT `user_influence_analysis_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_multicriteria_influence_analysis_results`
--

DROP TABLE IF EXISTS `user_multicriteria_influence_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_multicriteria_influence_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `user` varchar(300) NOT NULL,
  `top_k_appareances` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_multicriteria_influence_analysis_campaign_analysis_id` (`campaign_analysis_id`),
  CONSTRAINT `user_multicriteria_influence_analysis_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_reply_activity_analysis_results`
--

DROP TABLE IF EXISTS `user_reply_activity_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_reply_activity_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `user` varchar(300) NOT NULL,
  `frequency` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_reply_activity__analysis__campaign_analysis_id` (`campaign_analysis_id`),
  CONSTRAINT `user_reply_activity__analysis__campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_tweet_activity_analysis_results`
--

DROP TABLE IF EXISTS `user_tweet_activity_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_tweet_activity_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `user` varchar(300) NOT NULL,
  `frequency` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_tweet_activity_analysis_campaign_analysis_id` (`campaign_analysis_id`),
  CONSTRAINT `user_tweet_activity_analysis_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_tweet_impact_analysis_results`
--

DROP TABLE IF EXISTS `user_tweet_impact_analysis_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_tweet_impact_analysis_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_analysis_id` int NOT NULL,
  `user` varchar(300) NOT NULL,
  `interactions` int NOT NULL,
  `tweet_impact_mode` varchar(15) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_tweet_impact_analysis_campaign_analysis_id` (`campaign_analysis_id`),
  KEY `idx_tweet_impact_mode` (`tweet_impact_mode`),
  CONSTRAINT `user_tweet_impact_analysis_campaign_analysis_id` FOREIGN KEY (`campaign_analysis_id`) REFERENCES `campaign_analysis` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-25  8:58:44
