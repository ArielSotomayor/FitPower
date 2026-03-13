-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         8.0.30 - MySQL Community Server - GPL
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.1.0.6537
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para fitpower_db
CREATE DATABASE IF NOT EXISTS `fitpower_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `fitpower_db`;

-- Volcando estructura para tabla fitpower_db.trainer_profiles
CREATE TABLE IF NOT EXISTS `trainer_profiles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `certification` varchar(255) NOT NULL,
  `experience_years` int NOT NULL,
  `bio` text,
  `profile_completed` tinyint(1) DEFAULT '0',
  `phone` varchar(30) DEFAULT NULL,
  `location` varchar(150) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `height` decimal(5,2) DEFAULT NULL,
  `weight` decimal(5,2) DEFAULT NULL,
  `gender` enum('male','female','other') DEFAULT NULL,
  `specialty_id` int DEFAULT NULL,
  `profile_photo` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `fk_trainer_specialty` (`specialty_id`),
  CONSTRAINT `fk_trainer_specialty` FOREIGN KEY (`specialty_id`) REFERENCES `trainer_specialties` (`id`) ON DELETE SET NULL,
  CONSTRAINT `trainer_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla fitpower_db.trainer_profiles: ~2 rows (aproximadamente)
DELETE FROM `trainer_profiles`;
INSERT INTO `trainer_profiles` (`id`, `user_id`, `certification`, `experience_years`, `bio`, `profile_completed`, `phone`, `location`, `age`, `height`, `weight`, `gender`, `specialty_id`, `profile_photo`) VALUES
	(3, 17, 'asdafafaef', 10, 'fdfsggrazgagragragafdg', 1, '+503 7451-0678', 'Santa Ana, El Salvadir', 24, 1.82, 17.50, 'male', 6, 'Captura.PNG'),
	(4, 19, 'asdafafaef', 10, 'fluf,yifv,jyuhvujycv,ujyck,', 1, '+503 7451-0678', 'Santa Ana, El Salvadir', 25, 1.65, 143.00, 'female', 8, 'FP EN.png');

-- Volcando estructura para tabla fitpower_db.trainer_specialties
CREATE TABLE IF NOT EXISTS `trainer_specialties` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla fitpower_db.trainer_specialties: ~8 rows (aproximadamente)
DELETE FROM `trainer_specialties`;
INSERT INTO `trainer_specialties` (`id`, `name`) VALUES
	(1, 'Cardio'),
	(3, 'Crossfit'),
	(2, 'Fuerza'),
	(7, 'Funcional'),
	(6, 'HIIT'),
	(4, 'Musculación'),
	(5, 'Rehabilitación'),
	(8, 'Yoga');

-- Volcando estructura para tabla fitpower_db.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(150) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `verification_token` varchar(255) DEFAULT NULL,
  `role` enum('cliente','entrenador','admin') NOT NULL,
  `is_email_verified` tinyint(1) DEFAULT '0',
  `status` enum('pending','approved','rejected','active') DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `verification_code` varchar(6) DEFAULT NULL,
  `verification_expires` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_verification_token` (`verification_token`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla fitpower_db.users: ~4 rows (aproximadamente)
DELETE FROM `users`;
INSERT INTO `users` (`id`, `full_name`, `email`, `password_hash`, `verification_token`, `role`, `is_email_verified`, `status`, `created_at`, `verification_code`, `verification_expires`) VALUES
	(14, 'Jacinto Sotomayor', 'vanesotomayor0411@gmail.com', '$argon2id$v=19$m=65536,t=3,p=4$OIeQspbSGkNISan1vleKUQ$0kRi6rTn+y2Dd7OMu/xZjOK59WVGeGFJ4ujuZNSfUtI', NULL, 'cliente', 1, 'active', '2026-03-06 20:33:25', NULL, '2026-03-06 15:24:33'),
	(17, 'Roberto Mario Urbina', 'rmario.urbina@gmail.com', '$argon2id$v=19$m=65536,t=3,p=4$Z6zVWosx5rw3BoDwHkOIkQ$cgPR8qP7XHP96DYofnUoG92i+40lx9qf/HyN0LqQkQI', NULL, 'entrenador', 1, 'approved', '2026-03-10 02:33:56', NULL, NULL),
	(18, 'Midence Luna', 'yo891894@gmail.com', '$argon2id$v=19$m=65536,t=3,p=4$rDVGSGktxVhL6Z0zRkip9Q$AoJtC49GP3y4IREwB0PXT/HdkiOmU9e7qIpmJxQpsU8', NULL, 'cliente', 1, 'active', '2026-03-10 02:35:53', NULL, NULL),
	(19, 'Ariel Alejandro Sotomayor', 'rmugxd@gmail.com', '$argon2id$v=19$m=65536,t=3,p=4$oLT2PgdA6D0nJKT0Xoux1g$cdPsMQFWHQM9Yf0y60DV+pAQrJ7rRKF625lIf8SQ2tk', NULL, 'entrenador', 1, 'approved', '2026-03-11 21:49:05', NULL, NULL);

-- Volcando estructura para tabla fitpower_db.user_profiles
CREATE TABLE IF NOT EXISTS `user_profiles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `age` int NOT NULL,
  `height` decimal(5,2) NOT NULL,
  `weight` decimal(5,2) NOT NULL,
  `occupation` enum('estudiante','trabajador','desempleado') NOT NULL,
  `schedule` enum('am','pm','flexible') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla fitpower_db.user_profiles: ~0 rows (aproximadamente)
DELETE FROM `user_profiles`;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
