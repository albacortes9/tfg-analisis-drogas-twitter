-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema twitter_analysis
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `twitter_analysis` DEFAULT CHARACTER SET utf8 ;
USE `twitter_analysis` ;

-- -----------------------------------------------------
-- Table `twitter_analysis`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `twitter_analysis`.`user` (
  `id` BIGINT NOT NULL,
  `name` VARCHAR(255) NULL,
  `username` VARCHAR(255) NULL,
  `location` VARCHAR(255) NULL,
  `verified` TINYINT NULL,
  `profile_image_url` VARCHAR(255) NULL,
  `followers_count` INT NULL,
  `following_count` INT NULL,
  `tweet_count` INT NULL,
  `listed_count` INT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `twitter_analysis`.`tweet`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `twitter_analysis`.`tweet` (
  `id` BIGINT NOT NULL,
  `text` TEXT NULL,
  `author_id` BIGINT  NULL,
  `created_at` DATETIME NULL,
  `media` TINYINT NULL,
  PRIMARY KEY (`id`),
    FOREIGN KEY (`author_id`)
    REFERENCES `twitter_analysis`.`user` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `twitter_analysis`.`tweet_metrics`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `twitter_analysis`.`tweet_metrics` (
  `tweet_id` BIGINT NOT NULL,
  `retweet_count` INT NULL,
  `reply_count` INT NULL,
  `like_count` INT NULL,
  `quote_count` INT NULL
  PRIMARY KEY (`tweet_id`),
    FOREIGN KEY (`tweet_id`)
    REFERENCES `twitter_analysis`.`tweet` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `twitter_analysis`.`mention`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `twitter_analysis`.`mention` (
  `tweet_id` BIGINT NOT NULL,
  `username` VARCHAR(255) NULL,
  `start_pos` INT NULL,
  `end_pos` INT NULL,
  PRIMARY KEY (`tweet_id`),
    FOREIGN KEY (`tweet_id`)
    REFERENCES `twitter_analysis`.`tweet` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `twitter_analysis`.`referenced_tweet`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `twitter_analysis`.`referenced_tweet` (
  `tweet_id` BIGINT NOT NULL,
  `referenced_tweet_id` BIGINT NOT NULL,
  `reference_type` ENUM('replied_to', 'quoted') NULL,
  PRIMARY KEY (`referenced_tweet_id`, `tweet_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `twitter_analysis`.`drug`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `twitter_analysis`.`drug` (
  `id` INT NOT NULL,
  `name` VARCHAR(100) NULL,
  `description` TEXT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `twitter_analysis`.`drug_keyword`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `twitter_analysis`.`drug_keyword` (
  `id` INT NOT NULL,
  `drug_id` INT NULL,
  `keyword` VARCHAR(100) NULL,
  PRIMARY KEY (`id`),
    FOREIGN KEY (`drug_id`)
    REFERENCES `twitter_analysis`.`drug` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `twitter_analysis`.`tweet_keyword`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `twitter_analysis`.`tweet_keyword` (
  `tweet_id` BIGINT NOT NULL,
  `keyword_id` INT NOT NULL,
  PRIMARY KEY (`tweet_id`, `keyword_id`),
    FOREIGN KEY (`tweet_id`)
    REFERENCES `twitter_analysis`.`tweet` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
    FOREIGN KEY (`keyword_id`)
    REFERENCES `twitter_analysis`.`drug_keyword` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `twitter_analysis`.`ubication`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `twitter_analysis`.`ubication` (
  `tweet_id` BIGINT NOT NULL,
  `id` VARCHAR(255) NULL,
  `name` VARCHAR(255) NULL,
  `full_name` VARCHAR(255) NULL,
  `country_code` CHAR(2) NULL,
  `country` VARCHAR(255) NULL,
  `place_type` VARCHAR(255) NULL,
  `bbox` JSON NULL,
  PRIMARY KEY (`tweet_id`),
    FOREIGN KEY (`tweet_id`)
    REFERENCES `twitter_analysis`.`tweet` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `twitter_analysis`.`slang` (
  `id` INT NOT NULL,
  `concept` VARCHAR(255) NULL,
  `annotation1` VARCHAR(10) NULL,
  `annotation2` VARCHAR(10) NULL,
  `annotation3` VARCHAR(10) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `twitter_analysis`.`metamap` (
  `cui` CHAR(8) NOT NULL,
  `term` VARCHAR(255) NULL,
  `tui` CHAR(4) NULL,
  `annotation1` VARCHAR(10) NULL,
  `annotation2` VARCHAR(10) NULL,
  `annotation3` VARCHAR(10) NULL,
  PRIMARY KEY (`cui`),
   FOREIGN KEY (`tui`)
    REFERENCES `twitter_analysis`.`semantic_type` (`tui`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `twitter_analysis`.`semantic_type` (
  `tui` CHAR(4) NOT NULL,
  `abbreviation` CHAR(4) NULL,
  `description` VARCHAR(50) NULL,
  `annotation` VARCHAR(45) NULL,
  PRIMARY KEY (`tui`))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `twitter_analysis`.`tweet_metamap` (
  `tweet_id` BIGINT(20) NOT NULL,
  `cui` CHAR(8) NOT NULL,
  `tui`CHAR(4) NOT NULL,
  `matched_words` TEXT NULL,
  `positional_info` TEXT NULL,
  PRIMARY KEY (`cui`, `tweet_id`, `tui`),
    FOREIGN KEY (`tweet_id`)
      REFERENCES `twitter_analysis`.`tweet` (`id`)
      ON DELETE RESTRICT
      ON UPDATE CASCADE,
    FOREIGN KEY (`cui`)
      REFERENCES `twitter_analysis`.`metamap` (`cui`)
      ON DELETE RESTRICT
      ON UPDATE CASCADE,
	FOREIGN KEY (`tui`)
	  REFERENCES `twitter_analysis`.`semantic_type` (`tui`))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `twitter_analysis`.`tweet_slang` (
  `tweet_id` bigint NOT NULL,
  `slang_id` INT NOT NULL,
	PRIMARY KEY (`tweet_id`, `slang_id`),
    FOREIGN KEY (`tweet_id`)
    REFERENCES `twitter_analysis`.`tweet` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
    FOREIGN KEY (`slang_id`)
    REFERENCES `twitter_analysis`.`slang` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
