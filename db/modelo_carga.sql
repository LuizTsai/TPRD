
#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

DROP SCHEMA IF EXISTS `carga` ;
CREATE SCHEMA IF NOT EXISTS `carga`  default character set utf8 COLLATE utf8_unicode_ci;
USE `carga` ;

-- -----------------------------------------------------
-- Table `carga`.`Programa`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `carga`.`Programa` (
  `idPrograma` INT NOT NULL ,
  `nome` VARCHAR(45) NULL ,
  `descricao` VARCHAR(256) NULL ,
  `desativado` TINYINT(1) NULL DEFAULT 0,
  PRIMARY KEY (`idPrograma`) )
ENGINE = InnoDB;

CREATE UNIQUE INDEX `nome_UNIQUE` ON `carga`.`Programa` (`nome` ASC) ;


-- -----------------------------------------------------
-- Table `carga`.`Execucao`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `carga`.`Execucao` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `data` DATETIME NOT NULL ,
  `programa_id` INT NOT NULL ,
  `arq_carregado` VARCHAR(128) NOT NULL ,
  `data_carregada` DATE NOT NULL ,
  `arq_log` VARCHAR(64) NULL ,
  `cot_inseridas` MEDIUMINT NULL ,
  `cot_alteradas` MEDIUMINT NULL ,
  `cot_iguais` MEDIUMINT NULL ,
  `erro` TINYINT(1) NULL ,
  `msg_erro` VARCHAR(256) NULL ,
  PRIMARY KEY (id) ,
  CONSTRAINT `fk_Execucao_Programa`
    FOREIGN KEY (`programa_id` )
    REFERENCES `carga`.`Programa` (`idPrograma` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `idx_execucao_data_carregada` ON `carga`.`Execucao` (`data_carregada` ASC) ;


-- -----------------------------------------------------
-- Table `carga`.`ProgramaSubBolsa`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `carga`.`ProgramaSubBolsa` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `programa_id` INT NOT NULL ,
  `subbolsa_id` TINYINT NOT NULL ,
  PRIMARY KEY (`id`) ,
  CONSTRAINT `fk_Programa_SubBolsa_Programa`
    FOREIGN KEY (`programa_id` )
    REFERENCES `carga`.`Programa` (`idPrograma` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Programa_SubBolsa_SubBolsa`
    FOREIGN KEY (`subbolsa_id` )
    REFERENCES `dados`.`SubBolsa` (`idSubBolsa` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `carga`.`ProgramaFamiliaContratos`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `carga`.`ProgramaFamiliaContratos` (
  `programa_id` INT NOT NULL ,
  `familiacontratos_id` INT NOT NULL ,
  PRIMARY KEY (`programa_id`, `familiacontratos_id`) ,
  CONSTRAINT `fk_Programa_FamiliaContratos_Programa`
    FOREIGN KEY (`programa_id` )
    REFERENCES `carga`.`Programa` (`idPrograma` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Programa_FamiliaContratos_FamiliaContratos`
    FOREIGN KEY (`familiacontratos_id` )
    REFERENCES `dados`.`FamiliaContratos` (`idFamiliaContratos` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

