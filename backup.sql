-- MySQL dump 10.13  Distrib 8.0.37, for Win64 (x86_64)
--
-- Host: 52.86.139.21    Database: surveydb
-- ------------------------------------------------------
-- Server version	5.5.5-10.11.8-MariaDB-0ubuntu0.24.04.1-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `optional_terms`
--

DROP TABLE IF EXISTS `optional_terms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `optional_terms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `optional_code` varchar(100) NOT NULL,
  `version` char(4) NOT NULL,
  `content` text NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `is_current` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `optional_code` (`optional_code`,`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `optional_terms`
--

LOCK TABLES `optional_terms` WRITE;
/*!40000 ALTER TABLE `optional_terms` DISABLE KEYS */;
/*!40000 ALTER TABLE `optional_terms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `survey_responses`
--

DROP TABLE IF EXISTS `survey_responses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `survey_responses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `question` text NOT NULL,
  `answer` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `survey_responses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_login` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=187 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `survey_responses`
--

LOCK TABLES `survey_responses` WRITE;
/*!40000 ALTER TABLE `survey_responses` DISABLE KEYS */;
INSERT INTO `survey_responses` VALUES (145,26,'Quantos anos você tem?','22'),(146,26,'Com que frequência você faz compras em supermercados?','1'),(147,26,'Qual a distância do supermercado mais próximo?','2'),(148,26,'Quantas pessoas existem na família incluindo você?','22'),(149,26,'Quanto costuma ficar sua compra no supermercado?','3'),(150,26,'Quanto gasta por mês em mercearia, açougue e sacolão do seu bairro (fora supermercado)?','2'),(163,30,'Quantos anos você tem?','22'),(164,30,'Com que frequência você faz compras em supermercados?','2'),(165,30,'Qual a distância do supermercado mais próximo?','2'),(166,30,'Quantas pessoas existem na família incluindo você?','22'),(167,30,'Quanto costuma ficar sua compra no supermercado?','1'),(168,30,'Quanto gasta por mês em mercearia, açougue e sacolão do seu bairro (fora supermercado)?','2'),(169,31,'Quantos anos você tem?','22'),(170,31,'Com que frequência você faz compras em supermercados?','1'),(171,31,'Qual a distância do supermercado mais próximo?','2'),(172,31,'Quantas pessoas existem na família incluindo você?','22'),(173,31,'Quanto costuma ficar sua compra no supermercado?','2'),(174,31,'Quanto gasta por mês em mercearia, açougue e sacolão do seu bairro (fora supermercado)?','1'),(175,32,'Quantos anos você tem?','4'),(176,32,'Com que frequência você faz compras em supermercados?','0'),(177,32,'Qual a distância do supermercado mais próximo?','1'),(178,32,'Quantas pessoas existem na família incluindo você?','4'),(179,32,'Quanto costuma ficar sua compra no supermercado?','2'),(180,32,'Quanto gasta por mês em mercearia, açougue e sacolão do seu bairro (fora supermercado)?','1');
/*!40000 ALTER TABLE `survey_responses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `terms_and_privacy_policy`
--

DROP TABLE IF EXISTS `terms_and_privacy_policy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `terms_and_privacy_policy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `version` char(4) NOT NULL,
  `type` enum('terms','privacy','optional') NOT NULL,
  `content` text NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `is_current` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `version` (`version`,`type`),
  UNIQUE KEY `type` (`type`,`is_current`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `terms_and_privacy_policy`
--

LOCK TABLES `terms_and_privacy_policy` WRITE;
/*!40000 ALTER TABLE `terms_and_privacy_policy` DISABLE KEYS */;
INSERT INTO `terms_and_privacy_policy` VALUES (1,'0000','terms','Você ainda não possui uma versão de termo obrigatório no banco de dados.','2024-11-25 17:39:45',1),(2,'0000','optional','Você ainda não possui uma versão de termo opcional no banco de dados.','2024-11-25 17:39:45',1),(3,'0000','privacy','Você ainda não possui uma versão de política de privacidade no banco de dados.','2024-11-25 17:39:45',1);
/*!40000 ALTER TABLE `terms_and_privacy_policy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_login`
--

DROP TABLE IF EXISTS `user_login`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_login` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `sobrenome` varchar(100) NOT NULL,
  `telefone` varchar(15) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) DEFAULT NULL,
  `bairro` varchar(100) NOT NULL,
  `role` enum('user','admin') NOT NULL DEFAULT 'user',
  `is_default_admin` tinyint(1) DEFAULT 0,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `provider` enum('local','google') NOT NULL DEFAULT 'local',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_login`
--

LOCK TABLES `user_login` WRITE;
/*!40000 ALTER TABLE `user_login` DISABLE KEYS */;
INSERT INTO `user_login` VALUES (1,'admin','system','00000000000','admin@system.com','$2b$12$0h1df7OSHkzwqKRlzFIYD.DYlc67siTOBKmpTt3x/6uxYjA.0CuGi','NENHUM','admin',1,'2024-11-25 17:39:45','local'),(26,'rodrigo','goulart','12988370248','rodrigo@email.com','$2b$12$3MfwwGJyPU8aii/Kqr0gDOnWiiM3ylJkL9IymwqxeRyeBrP0uDnNS','JARDIM AMERICANO','user',0,'2024-11-26 17:28:22','local'),(29,'eliana','moreira','12988370248','eliana@gmail.com','$2b$12$TmgypPpnfpUQ66NHxAHE9.lrqZQgmgC9wYnlOuawuX55YZ6WIZ0am','JARDIM ITAPUÃ','user',0,'2024-11-26 23:08:28','local'),(30,'eliana','moreira','12988370248','exemplo@email.com','$2b$12$L9/eJwWLyP/JiX2H6tZ8IeeYgbsJHCZcjLsTl4D.DNgMtb.xsmwji','JARDIM MARIANA','user',0,'2024-11-26 23:12:21','local'),(31,'Wallace','Silva','12988370248','wallace.marinhosouzas@gmail.com','$2b$12$.cL4hfo81pCwoiOZex5vM.ySwSdCZu7aklAZ6wL6KMTcVQVgEMtl.','JARDIM MOTORAMA','user',0,'2024-11-27 01:57:41','local'),(32,'jean','carlos','12988370248','jean@email.com','$2b$12$vXM3fG.4mz3yJGsWJ39s3.WNjurXPDkQYWzSELeCrJ79QS.8aSoGS','JARDIM MARIANA II','user',0,'2024-11-27 01:58:31','local');
/*!40000 ALTER TABLE `user_login` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_optional_terms_acceptance`
--

DROP TABLE IF EXISTS `user_optional_terms_acceptance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_optional_terms_acceptance` (
  `user_id` int(11) NOT NULL,
  `optional_term_id` int(11) NOT NULL,
  `accepted_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`user_id`,`optional_term_id`),
  KEY `optional_term_id` (`optional_term_id`),
  CONSTRAINT `user_optional_terms_acceptance_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_login` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_optional_terms_acceptance_ibfk_2` FOREIGN KEY (`optional_term_id`) REFERENCES `optional_terms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_optional_terms_acceptance`
--

LOCK TABLES `user_optional_terms_acceptance` WRITE;
/*!40000 ALTER TABLE `user_optional_terms_acceptance` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_optional_terms_acceptance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_terms_and_privacy_acceptance`
--

DROP TABLE IF EXISTS `user_terms_and_privacy_acceptance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_terms_and_privacy_acceptance` (
  `user_id` int(11) NOT NULL,
  `terms_version` char(4) NOT NULL,
  `privacy_version` char(4) NOT NULL,
  `optional_version` char(4) DEFAULT NULL,
  `accepted_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`user_id`),
  KEY `terms_version` (`terms_version`),
  KEY `privacy_version` (`privacy_version`),
  KEY `optional_version` (`optional_version`),
  CONSTRAINT `user_terms_and_privacy_acceptance_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_login` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_terms_and_privacy_acceptance_ibfk_2` FOREIGN KEY (`terms_version`) REFERENCES `terms_and_privacy_policy` (`version`) ON DELETE CASCADE,
  CONSTRAINT `user_terms_and_privacy_acceptance_ibfk_3` FOREIGN KEY (`privacy_version`) REFERENCES `terms_and_privacy_policy` (`version`) ON DELETE CASCADE,
  CONSTRAINT `user_terms_and_privacy_acceptance_ibfk_4` FOREIGN KEY (`optional_version`) REFERENCES `terms_and_privacy_policy` (`version`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_terms_and_privacy_acceptance`
--

LOCK TABLES `user_terms_and_privacy_acceptance` WRITE;
/*!40000 ALTER TABLE `user_terms_and_privacy_acceptance` DISABLE KEYS */;
INSERT INTO `user_terms_and_privacy_acceptance` VALUES (1,'0000','0000','0000','2024-11-25 17:39:45'),(26,'0000','0000','0000','2024-11-26 17:28:23'),(29,'0000','0000','0000','2024-11-26 23:08:29'),(30,'0000','0000','0000','2024-11-26 23:12:21'),(31,'0000','0000','0000','2024-11-27 01:57:41'),(32,'0000','0000','0000','2024-11-27 01:58:31');
/*!40000 ALTER TABLE `user_terms_and_privacy_acceptance` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-27  9:56:17
