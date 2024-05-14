
#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

DROP SCHEMA IF EXISTS `texto` ;
CREATE SCHEMA IF NOT EXISTS `texto` default character set utf8 COLLATE utf8_unicode_ci;
USE `texto` ;


-- -----------------------------------------------------
-- Table `Texto`.`Cadernos`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `texto`.`Cadernos` (
  `id` TINYINT NOT NULL ,
  `nome` VARCHAR(45) NOT NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Texto`.`Artigos`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `texto`.`Artigos` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `cadernos_id` TINYINT NOT NULL ,
  `data` DATE NOT NULL ,
  `nome` VARCHAR(128) NOT NULL ,
  `url` VARCHAR(256) NULL ,
  `sinopse` VARCHAR(512) NULL ,
  PRIMARY KEY (`id`) ,
  CONSTRAINT `fk_Artigos_Cadernos`
    FOREIGN KEY (`cadernos_id` )
    REFERENCES `texto`.`Cadernos` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE INDEX `idx_Artigos_data` ON `texto`.`Artigos` (`data` ASC) ;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

