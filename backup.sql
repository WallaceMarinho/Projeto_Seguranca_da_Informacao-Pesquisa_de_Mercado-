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
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `survey_responses`
--

LOCK TABLES `survey_responses` WRITE;
/*!40000 ALTER TABLE `survey_responses` DISABLE KEYS */;
INSERT INTO `survey_responses` VALUES (7,7,'Quantos anos você tem?','22'),(8,7,'Com que frequência você faz compras em supermercados?','1'),(9,7,'Qual a distância do supermercado mais próximo?','1'),(10,7,'Quantas pessoas existem na família incluindo você?','5'),(11,7,'Quanto costuma ficar sua compra no supermercado?','0'),(12,7,'Quanto gasta por mês em mercearia, açougue e sacolão do seu bairro (fora supermercado)?','1'),(19,9,'Quantos anos você tem?','22'),(20,9,'Com que frequência você faz compras em supermercados?','1'),(21,9,'Qual a distância do supermercado mais próximo?','1'),(22,9,'Quantas pessoas existem na família incluindo você?','11'),(23,9,'Quanto costuma ficar sua compra no supermercado?','1'),(24,9,'Quanto gasta por mês em mercearia, açougue e sacolão do seu bairro (fora supermercado)?','0');
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
  UNIQUE KEY `version` (`version`,`type`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `terms_and_privacy_policy`
--

LOCK TABLES `terms_and_privacy_policy` WRITE;
/*!40000 ALTER TABLE `terms_and_privacy_policy` DISABLE KEYS */;
INSERT INTO `terms_and_privacy_policy` VALUES (1,'0000','terms','Você ainda não possui uma versão de termo obrigatório no banco de dados.','2024-10-29 00:04:01',1),(2,'0000','optional','Você ainda não possui uma versão de termo opcional no banco de dados.','2024-10-29 00:04:01',1),(3,'0000','privacy','Você ainda não possui uma versão de política de privacidade no banco de dados.','2024-10-29 00:04:01',1);
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_login`
--

LOCK TABLES `user_login` WRITE;
/*!40000 ALTER TABLE `user_login` DISABLE KEYS */;
INSERT INTO `user_login` VALUES (1,'admin','system','00000000000','admin@system.com','# Senha do usuário PADRÃO do seu sistema (6 caracteres)','NENHUM','admin',1,'2024-10-29 00:04:01','local'),(3,'exemplo','legal','12988370248','exemplo@email.com','$2b$12$DgRdW.LwwH4o9D1hX6T/XO11L2nmJJx4I/m0dDDD.SdNldxS5VKUG','JARDIM MARIANA II','user',0,'2024-11-05 11:43:55','local'),(4,'exemplo','legal','12988370248','exemplo.legal@gmail.com','$2b$12$kSHqcCmiki0xZdLy5GEOZeOMG/gYeMhv0RgYE3pKvOYB1X8fUVp96','JARDIM MARIANA II','user',0,'2024-11-05 11:44:46','local'),(5,'Wallace','Silva','12988370248','wallace.silva28@fatec.sp.gov.br','$2b$12$FKLSfpPw66DBE9wfA8eIHe7pr8hHEl1kdMdSCNOdbdehsMuPc67jG','JARDIM NOVA FLORIDA','user',0,'2024-11-05 22:30:42','local'),(7,'Wallace','Silva','12988370248','silva.marinho@gmail.com','$2b$12$EkV8dX2hutRLoW.bVkoDIuybSFuWrvSSvwvS/PWUb9MY7JV7MDTKe','JARDIM NOVA DETROIT','user',0,'2024-11-05 22:34:17','local'),(9,'Wallace','Silva','12988370248','wallace.marinhosouzas@gmail.com',NULL,'JARDIM CEREJEIRAS','user',0,'2024-11-06 13:25:56','google');
/*!40000 ALTER TABLE `user_login` ENABLE KEYS */;
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
INSERT INTO `user_terms_and_privacy_acceptance` VALUES (1,'0000','0000','0000','2024-10-29 00:04:01'),(3,'0000','0000','0000','2024-11-05 11:43:55'),(4,'0000','0000','0000','2024-11-05 11:44:46'),(5,'0000','0000','0000','2024-11-05 22:30:42'),(7,'0000','0000','0000','2024-11-05 22:34:17'),(9,'0000','0000',NULL,'2024-11-06 13:25:56');
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

-- Dump completed on 2024-11-13  9:55:20
--
