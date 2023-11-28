CREATE DATABASE IF NOT EXISTS studentfinance;
USE studentfinance;


-- CREATE DATABASE IF NOT EXISTS sf;
-- use sf

CREATE TABLE `login` (
  `username` varchar(255) NOT NULL,
  `password` varchar(255) DEFAULT NULL,
  `user_type` enum('admin','student','vendor') NOT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `student` (
  `student_id` int NOT NULL,
  `username` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `points_owned` int DEFAULT NULL,
  `year_of_study` int DEFAULT NULL,
  `daily_limit` int DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `username` (`username`),
  CONSTRAINT `student_ibfk_1` FOREIGN KEY (`username`) REFERENCES `login` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `service` (
  `service_id` int NOT NULL,
  `type` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `student_id` int DEFAULT NULL,
  PRIMARY KEY (`service_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `service_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `recharge_point` (
  `admin_id` int NOT NULL,
  `username` varchar(15) NOT NULL,
  `location` varchar(255) NOT NULL,
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `location` (`location`),
  CONSTRAINT `recharge_point_ibfk_1` FOREIGN KEY (`username`) REFERENCES `login` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `student_recharge` (
  `admin_id` int NOT NULL,
  `student_id` int NOT NULL,
  `recharge_id` int NOT NULL AUTO_INCREMENT,
  `points_added` int NOT NULL,
  `recharge_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`recharge_id`),
  KEY `admin_id` (`admin_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `student_recharge_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `recharge_point` (`admin_id`),
  CONSTRAINT `student_recharge_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `student_transactions` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `from_id` int DEFAULT NULL,
  `to_id` int DEFAULT NULL,
  `from_entity` enum('student','admin','vendor') NOT NULL,
  `to_entity` enum('student','admin','vendor') NOT NULL,
  `item_id` int NOT NULL DEFAULT '0',
  `points` int DEFAULT NULL,
  `transaction_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `from_name` varchar(255) DEFAULT NULL,
  `to_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `from_id` (`from_id`),
  KEY `to_id` (`to_id`),
  CONSTRAINT `fk_student_transactions_from` FOREIGN KEY (`from_id`) REFERENCES `student` (`student_id`),
  CONSTRAINT `fk_student_transactions_to` FOREIGN KEY (`to_id`) REFERENCES `student` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `stall` (
  `stall_id` int NOT NULL,
  `type` varchar(255) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `stall_name` varchar(255) DEFAULT NULL,
  `open_time` datetime DEFAULT NULL,
  `close_time` datetime DEFAULT NULL,
  PRIMARY KEY (`stall_id`),
  UNIQUE KEY `stall_name` (`stall_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `vendor` (
  `vendor_id` int NOT NULL,
  `username` varchar(255) DEFAULT NULL,
  `vendor_name` varchar(255) DEFAULT NULL,
  `stall_id` int DEFAULT NULL,
  `profits` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`vendor_id`),
  UNIQUE KEY `username` (`username`),
  KEY `stall_id` (`stall_id`),
  CONSTRAINT `vendor_ibfk_1` FOREIGN KEY (`username`) REFERENCES `login` (`username`),
  CONSTRAINT `vendor_ibfk_2` FOREIGN KEY (`stall_id`) REFERENCES `stall` (`stall_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



CREATE TABLE `item` (
  `item_id` int NOT NULL,
  `item_name` varchar(255) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `stall_item` (
  `stall_id` int NOT NULL,
  `item_id` int NOT NULL AUTO_INCREMENT,
  `quantity` int DEFAULT '0',
  PRIMARY KEY (`stall_id`,`item_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `stall_item_ibfk_1` FOREIGN KEY (`stall_id`) REFERENCES `stall` (`stall_id`),
  CONSTRAINT `stall_item_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `vendor_transactions` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `from_id` int DEFAULT NULL,
  `to_id` int DEFAULT NULL,
  `from_entity` enum('student','admin','vendor') NOT NULL,
  `to_entity` enum('student','admin','vendor') NOT NULL,
  `item_id` int NOT NULL DEFAULT '0',
  `points` int DEFAULT NULL,
  `transaction_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `from_name` varchar(255) DEFAULT NULL,
  `to_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `from_id` (`from_id`),
  KEY `to_id` (`to_id`),
  CONSTRAINT `fk_vendor_transactions_from` FOREIGN KEY (`from_id`) REFERENCES `student` (`student_id`),
  CONSTRAINT `fk_vendor_transactions_to` FOREIGN KEY (`to_id`) REFERENCES `vendor` (`vendor_id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `event` (
  `event_id` int NOT NULL,
  `no_of_hours` int DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `eligible_points` int DEFAULT NULL,
  `entry_fee` int NOT NULL DEFAULT '0',
  `event_name` varchar(255) DEFAULT NULL,
  `num_of_participants` int DEFAULT NULL,
  `no_of_volunteers` int DEFAULT NULL,
  `place` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `has_registered` (
  `event_id` int NOT NULL,
  `student_id` int NOT NULL,
  PRIMARY KEY (`event_id`,`student_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `has_registered_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `event` (`event_id`),
  CONSTRAINT `has_registered_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `event_volunteers` (
  `student_id` int NOT NULL,
  `event_id` int NOT NULL,
  PRIMARY KEY (`student_id`,`event_id`),
  KEY `fk_event` (`event_id`),
  CONSTRAINT `event_volunteers_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`),
  CONSTRAINT `event_volunteers_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `event` (`event_id`),
  CONSTRAINT `fk_event` FOREIGN KEY (`event_id`) REFERENCES `event` (`event_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `old_events` (
  `event_id` int NOT NULL,
  `event_name` varchar(255) DEFAULT NULL,
  `event_type` varchar(255) DEFAULT NULL,
  `event_date` date DEFAULT NULL,
  `entry_fee` int DEFAULT NULL,
  PRIMARY KEY (`event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


--function creation

-- Function to calculate total points for a student
DELIMITER //
CREATE FUNCTION calculate_total_points_spent_student(student_id INT) RETURNS DECIMAL(10, 2) DETERMINISTIC
BEGIN
    DECLARE total_points DECIMAL(10, 2);
    SELECT COALESCE(SUM(points), 0) INTO total_points FROM student_transactions WHERE to_id = student_id;
    RETURN total_points;
END;
//
DELIMITER ;

-- Function to calculate total points for a vendor
DELIMITER //
CREATE FUNCTION calculate_total_points_vendor(vendor_id INT) RETURNS DECIMAL(10, 2) DETERMINISTIC
BEGIN
    DECLARE total_points DECIMAL(10, 2);
    SELECT COALESCE(SUM(points), 0) INTO total_points FROM vendor_transactions WHERE to_id = vendor_id;
    RETURN total_points;
END;
//
DELIMITER ;

--procedure creation
DELIMITER //

CREATE PROCEDURE AddPointsAndRecordTransaction(
    IN p_student_id INT,
    IN p_points_to_add INT,
    IN p_admin_id INT
)
BEGIN
    DECLARE v_transaction_time DATETIME;
    DECLARE v_recharge_id INT;

    SET v_transaction_time = NOW();

    UPDATE student
    SET points_owned = points_owned + p_points_to_add
    WHERE student_id = p_student_id;

    INSERT INTO student_recharge (admin_id, student_id, points_added, recharge_time)
    VALUES (p_admin_id, p_student_id, p_points_to_add, v_transaction_time);

    SET v_recharge_id = LAST_INSERT_ID();

    UPDATE student_recharge
    SET recharge_id = v_recharge_id
    WHERE recharge_id = v_recharge_id;
END //

CREATE PROCEDURE AddPointsToVendor(
    IN p_vendor_id INT,
    IN p_points INT
)
BEGIN
    DECLARE v_profits INT;

    SELECT profits INTO v_profits FROM vendor WHERE vendor_id = p_vendor_id LIMIT 1;

    IF v_profits IS NOT NULL THEN
        UPDATE vendor SET profits = v_profits + p_points WHERE vendor_id = p_vendor_id LIMIT 1;
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Vendor does not exist', MYSQL_ERRNO = 20000;
    END IF;
END //

CREATE PROCEDURE buy_item_procedure(
    IN student_id INT,
    IN item_id INT,
    IN points DECIMAL(10, 2),
    OUT message VARCHAR(255)
)
BEGIN
    DECLARE vendor_id INT;
    DECLARE vendor_name VARCHAR(255);

    IF EXISTS (SELECT 1 FROM stall_item WHERE item_id = item_id) THEN
        START TRANSACTION;

        UPDATE student SET points_owned = points_owned - points WHERE student_id = student_id;

        SELECT v.vendor_id, v.vendor_name
        INTO vendor_id, vendor_name
        FROM stall s
        JOIN vendor v ON s.stall_id = v.stall_id
        JOIN stall_item si ON s.stall_id = si.stall_id
        WHERE si.item_id = item_id;

        IF vendor_id IS NOT NULL THEN
            UPDATE vendor SET profits = profits + points WHERE vendor_id = vendor_id;

            INSERT INTO vendor_transactions (from_id, to_id, from_entity, to_entity, points, from_name, to_name, transaction_time)
            VALUES (student_id, vendor_id, 'student', 'vendor', points, (SELECT name FROM student WHERE student_id = student_id), vendor_name, NOW());

            COMMIT;
            SET message = 'Item purchased successfully!';
        ELSE
            ROLLBACK;
            SET message = 'Failed to purchase item. Vendor information not found.';
        END IF;
    ELSE
        SET message = 'Failed to purchase item. Item information not found.';
    END IF;
END //

CREATE PROCEDURE buy_service_procedure(
    IN student_id INT,
    IN service_id INT,
    IN points DECIMAL(10, 2),
    OUT message VARCHAR(255)
)
BEGIN
    DECLARE service_name VARCHAR(255);

    IF EXISTS (SELECT 1 FROM service WHERE service_id = service_id) THEN
        START TRANSACTION;

        UPDATE student SET points_owned = points_owned - points WHERE student_id = student_id;

        SELECT name INTO service_name FROM service WHERE service_id = service_id LIMIT 1;

        UPDATE student SET points_owned = points_owned + points WHERE student_id = (SELECT student_id FROM service WHERE service_id = service_id LIMIT 1);

        INSERT INTO student_transactions (from_id, to_id, from_entity, to_entity, points, from_name, to_name, transaction_time)
        VALUES (student_id, (SELECT student_id FROM service WHERE service_id = service_id LIMIT 1), 'student', 'service', points, (SELECT name FROM student WHERE student_id = student_id), service_name, NOW());

        COMMIT;
        SET message = 'Service purchased successfully!';
    ELSE
        ROLLBACK;
        SET message = 'Failed to purchase service. Service information not found.';
    END IF;
END //

CREATE PROCEDURE calculate_total_points_spent_student(
    IN student_id INT,
    OUT total_points DECIMAL(10, 2)
)
BEGIN
    SELECT COALESCE(SUM(points), 0) INTO total_points FROM student_transactions WHERE to_id = student_id;
END //

CREATE PROCEDURE calculate_total_points_vendor(
    IN vendor_id INT,
    OUT total_points DECIMAL(10, 2)
)
BEGIN
    SELECT COALESCE(SUM(points), 0) INTO total_points FROM vendor_transactions WHERE to_id = vendor_id;
END //

CREATE PROCEDURE DeductPointsFromBuyerAndAddPointsToSeller(
    IN buyer_id INT,
    IN seller_id INT,
    IN points INT
)
BEGIN
    DECLARE buyer_points INT;
    DECLARE seller_points INT;

    SELECT points_owned INTO buyer_points FROM student WHERE student_id = buyer_id;

    IF buyer_points >= points THEN
        UPDATE student SET points_owned = buyer_points - points WHERE student_id = buyer_id;

        SELECT points_owned INTO seller_points FROM student WHERE student_id = seller_id;

        UPDATE student SET points_owned = seller_points + points WHERE student_id = seller_id;
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Insufficient points';
    END IF;
END //

CREATE PROCEDURE DeductPointsFromStudent(
    IN in_student_id INT,
    IN in_points INT
)
BEGIN
    DECLARE current_points INT;

    SELECT points_owned INTO current_points FROM student WHERE student_id = in_student_id LIMIT 1;

    IF current_points >= in_points THEN
        UPDATE student SET points_owned = current_points - in_points WHERE student_id = in_student_id;
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Insufficient points';
    END IF;
END //

CREATE PROCEDURE RecordServiceTransaction(
    IN buyer_id INT,
    IN seller_id INT,
    IN service_id INT,
    IN points INT
)
BEGIN
    DECLARE buyer_name VARCHAR(255);
    DECLARE seller_name VARCHAR(255);

    SELECT name INTO buyer_name FROM student WHERE student_id = buyer_id;
    SELECT name INTO seller_name FROM student WHERE student_id = seller_id;

    INSERT INTO student_transactions (from_id, to_id, from_entity, to_entity, points, from_name, to_name, transaction_time)
    VALUES (buyer_id, seller_id, 'student', 'student', points, buyer_name, seller_name, NOW());
END //

CREATE PROCEDURE RecordVendorTransaction(
    IN from_id INT,
    IN to_id INT,
    IN points INT
)
BEGIN
    DECLARE from_name VARCHAR(255);
    DECLARE to_name VARCHAR(255);

    SELECT name INTO from_name FROM student WHERE student_id = from_id;
    SELECT vendor_name INTO to_name FROM vendor WHERE vendor_id = to_id;

    INSERT INTO vendor_transactions (from_id, to_id, from_entity, to_entity, points, from_name, to_name)
    VALUES (from_id, to_id, 'student', 'vendor', points, from_name, to_name);
END //

DELIMITER ;

--view creation
-- Available Services View
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER
VIEW `available_services` AS
  SELECT
    `service`.`service_id` AS `service_id`,
    `service`.`type` AS `type`,
    `service`.`name` AS `name`,
    `service`.`price` AS `price`,
    `service`.`student_id` AS `student_id`
  FROM
    `service`
  WHERE
    `service`.`service_id` NOT IN (
      SELECT
        `service`.`service_id`
      FROM
        `student_transactions`
      WHERE
        ((`student_transactions`.`from_entity` = 'student')
         AND (DATE(`student_transactions`.`transaction_time`) = CURDATE()))
    );

-- Available Items View
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER
VIEW `available_items` AS
  SELECT
    `i`.`item_id` AS `item_id`,
    `i`.`item_name` AS `item_name`,
    `i`.`price` AS `price`,
    `si`.`quantity` AS `quantity_in_stall`,
    `s`.`stall_name` AS `stall_name`
  FROM
    `item` `i`
    LEFT JOIN `stall_item` `si` ON `i`.`item_id` = `si`.`item_id`
    LEFT JOIN `stall` `s` ON `si`.`stall_id` = `s`.`stall_id`;

