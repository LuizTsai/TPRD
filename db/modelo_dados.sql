
#
# Copyright 2013 Leandro Dybal Bertoni - All Rights Reserved
#

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

DROP SCHEMA IF EXISTS `dados` ;
CREATE SCHEMA IF NOT EXISTS `dados` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci ;
USE `dados` ;

-- -----------------------------------------------------
-- Table `dados`.`Bolsa`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`Bolsa` (
  `idBolsa` TINYINT NOT NULL AUTO_INCREMENT,
  `mnemonico` VARCHAR(15) NOT NULL ,
  `nome` VARCHAR(256) NOT NULL ,
  `URL` VARCHAR(512) NULL ,
  PRIMARY KEY (`idBolsa`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `dados`.`SubBolsa`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`SubBolsa` (
  `idSubBolsa` TINYINT NOT NULL ,
  `bolsa_id` TINYINT NOT NULL ,
  `mnemonico` VARCHAR(45) NULL ,
  `nome` VARCHAR(256) NULL ,
  `pais` VARCHAR(24) NULL,
  `country` VARCHAR(24) NULL,
  PRIMARY KEY (`idSubBolsa`) ,
  CONSTRAINT `fk_SubBolsa_Bolsa`
    FOREIGN KEY (`bolsa_id` )
    REFERENCES `dados`.`Bolsa` (`idBolsa` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `dados`.`TipoAtivo`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`TipoAtivo` (
  `idTipoAtivo` TINYINT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(45) NULL ,
  PRIMARY KEY (`idTipoAtivo`) )
ENGINE = InnoDB
COMMENT = 'Por enquanto, \"Futuro\"';


-- -----------------------------------------------------
-- Table `dados`.`Categoria`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`Categoria` (
  `idCategoria` SMALLINT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(45) NOT NULL ,
  `pai` SMALLINT NULL ,
  `raiz` SMALLINT NULL ,
  `dimensoes` VARCHAR(5) NULL COMMENT 'Dimensões das unidades de contrato válidas (E=energia, M=massa e V=volume)' ,
  `densidade` DOUBLE NULL,
  `unidade_preco_default` SMALLINT NULL ,
  `unidade_volume` SMALLINT NULL ,
   nome_en varchar(45),
  PRIMARY KEY (`idCategoria`) ,
  CONSTRAINT `fk_Categoria_Categoria_pai`
    FOREIGN KEY (`pai` )
    REFERENCES `dados`.`Categoria` (`idCategoria` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Categoria_raiz`
    FOREIGN KEY (`raiz` )
    REFERENCES `dados`.`Categoria` (`idCategoria` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = 'Arvore de classificacao dos ativos';



-- -----------------------------------------------------
-- Table `dados`.`Moeda`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`Moeda` (
  `idMoeda` SMALLINT NOT NULL AUTO_INCREMENT,
  `simbolo` VARCHAR(15) NULL ,
  `mnemonico` VARCHAR(15) NULL ,
  `acronym` VARCHAR(15) NULL ,
  `nome` VARCHAR(45) NULL ,
  `name` VARCHAR(45) NULL ,
  `derivada` TINYINT(1) NULL ,
  `moeda_pai` SMALLINT NULL ,
  `qtdade_um_pai` DOUBLE NULL COMMENT 'quantiadde da moeda equivalente a uma unidade da moeda pai\n' ,
  PRIMARY KEY (`idMoeda`) ,
  CONSTRAINT `fk_Moeda_Pai`
    FOREIGN KEY (`moeda_pai` )
    REFERENCES `dados`.`Moeda` (`idMoeda` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



-- -----------------------------------------------------
-- Table `dados`.`Unidade`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`Unidade` (
  `idUnidade` SMALLINT NOT NULL AUTO_INCREMENT,
  `tipo` CHAR NOT NULL COMMENT 'P: peso, V: volume' ,
  `simbolo` VARCHAR(15) NULL ,
  `nome` VARCHAR(45) NULL ,
  `name` VARCHAR(45) NULL ,
  `display` TINYINT(1) NULL,
  PRIMARY KEY (`idUnidade`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `dados`.`FamiliaContratos`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`FamiliaContratos` (
  `idFamiliaContratos` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(256) NOT NULL ,
  `nome_res` VARCHAR(128) NOT NULL ,
  `subbolsa_id` TINYINT NOT NULL ,
  `tipo_id` TINYINT NULL ,
  `fisico` TINYINT NULL ,
  `cod_arq` VARCHAR(15) NULL ,
  `URL` VARCHAR(256) NULL ,
  `unidade_cotacao` SMALLINT NULL ,
  `moeda_cotacao` SMALLINT NULL ,
  `unidade_contrato_principal` SMALLINT NULL ,
  `unidade_contrato_secundaria` SMALLINT NULL ,
  `qtdade_contrato_principal` DOUBLE NULL ,
  `densidade` DOUBLE NULL,
  `tick_size` DOUBLE NULL ,
  `delta_venc_m` TINYINT NULL COMMENT 'delta em meses da data de vencimento' ,
  `delta_venc_d` TINYINT NULL COMMENT 'delta em dias da data de vencimento' ,
  `tipo_delta` CHAR NULL COMMENT 'C=dias corridos, U=dias úteis' ,
  `ajuste_fds` TINYINT NULL COMMENT 'O que fazer se vencimento nao cai em dia útil: 1=dia posterior, -1=dia anterior' ,
  `tipo_vencimento` char(1) COLLATE utf8_unicode_ci NOT NULL DEFAULT 'V',
  PRIMARY KEY (`idFamiliaContratos`) ,
  CONSTRAINT `fk_FamiliaContratos_SubBolsa`
    FOREIGN KEY (`subbolsa_id` )
    REFERENCES `dados`.`SubBolsa` (`idSubBolsa` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_FamiliaContratos_Tipo_Ativo`
    FOREIGN KEY (`tipo_id` )
    REFERENCES `dados`.`TipoAtivo` (`idTipoAtivo` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_FamiliaContratos_Moeda`
    FOREIGN KEY (`moeda_cotacao` )
    REFERENCES `dados`.`Moeda` (`idMoeda` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_FamiliaContratos_Unidade_Cotacao`
    FOREIGN KEY (`unidade_cotacao` )
    REFERENCES `dados`.`Unidade` (`idUnidade` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_FamiliaContratos_Unidade_Principal`
    FOREIGN KEY (`unidade_contrato_principal` )
    REFERENCES `dados`.`Unidade` (`idUnidade` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_FamiliaContratos_Unidade_Secundaria`
    FOREIGN KEY (`unidade_contrato_secundaria` )
    REFERENCES `dados`.`Unidade` (`idUnidade` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `idx_FamiliaContratos_cod_arq` ON `dados`.`FamiliaContratos` (`cod_arq` ASC) ;


-- -----------------------------------------------------
-- Table `dados`.`Ativo`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`Ativo` (
  `idAtivo` INT NOT NULL AUTO_INCREMENT,
  `subbolsa_id` TINYINT NULL ,
  `familia_contratos_id` INT NULL ,
  `tipo_id` TINYINT NULL ,
  `vencimento` varchar(15) NULL COMMENT 'Mes do vencimento na forma AAAA-MM' ,
  `data_vencimento` DATE NULL ,
  `pri_neg` DATE NULL COMMENT 'data do primeiro negocio na base' ,
  `ult_neg` DATE NULL COMMENT 'data do ultimo negocio na base' ,
  `unidade_cotacao` SMALLINT NULL ,
  `moeda_cotacao` SMALLINT NULL ,
  `unidade_contrato_principal` SMALLINT NULL ,
  `unidade_contrato_secundaria` SMALLINT NULL ,
  `qtdade_contrato_principal` DOUBLE NULL ,
 -- `fator_principal_secundaria` DOUBLE NULL ,
  `densidade` DOUBLE NULL,
  `tick_size` DOUBLE NULL ,
  `tipo_vencimento` char(1) COLLATE utf8_unicode_ci NOT NULL DEFAULT 'V',
  `delta_vencimento` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`idAtivo`) ,
  CONSTRAINT `fk_Ativos_SubBolsa`
    FOREIGN KEY (`subbolsa_id` )
    REFERENCES `dados`.`SubBolsa` (`idSubBolsa` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Ativo_FamiliaContratos`
    FOREIGN KEY (`familia_contratos_id` )
    REFERENCES `dados`.`FamiliaContratos` (`idFamiliaContratos` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Ativo_Tipo_Ativo`
    FOREIGN KEY (`tipo_id` )
    REFERENCES `dados`.`TipoAtivo` (`idTipoAtivo` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Ativo_Moeda`
    FOREIGN KEY (`moeda_cotacao` )
    REFERENCES `dados`.`Moeda` (`idMoeda` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Ativo_Unidade_Cotacao`
    FOREIGN KEY (`unidade_cotacao` )
    REFERENCES `dados`.`Unidade` (`idUnidade` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Ativo_Unidade_Principal`
    FOREIGN KEY (`unidade_contrato_principal` )
    REFERENCES `dados`.`Unidade` (`idUnidade` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Ativo_Unidade_Secundaria`
    FOREIGN KEY (`unidade_contrato_secundaria` )
    REFERENCES `dados`.`Unidade` (`idUnidade` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `idx_Ativo_Familia_vencimento` ON `dados`.`Ativo` (`familia_contratos_id` ASC, `vencimento` ASC, `delta_vencimento` ASC) ;

CREATE UNIQUE INDEX `idx_Ativo_Familia_data_vencimento` ON `dados`.`Ativo` (`familia_contratos_id` ASC, `data_vencimento` ASC, `delta_vencimento` ASC) ;



-- -----------------------------------------------------
-- Table `dados`.`ConversaoUnidade`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`ConversaoUnidade` (
  `origem` SMALLINT NOT NULL ,
  `destino` SMALLINT NOT NULL ,
  `fator_multi` DOUBLE NOT NULL ,
  PRIMARY KEY (`origem`, `destino`) ,
  CONSTRAINT `fk_Conversao_Unidade_Unidade_Origem`
    FOREIGN KEY (`origem` )
    REFERENCES `dados`.`Unidade` (`idUnidade` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Conversao_Unidade_Uniadde_Destino`
    FOREIGN KEY (`destino` )
    REFERENCES `dados`.`Unidade` (`idUnidade` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



-- -----------------------------------------------------
-- Table `dados`.`CotacaoAtivo`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`CotacaoAtivo` (
  `ativo_id` INT NOT NULL ,
  `data` DATE NOT NULL ,
  `abertura` DOUBLE NULL ,
  `fechamento` DOUBLE NULL ,
  `vwap` DOUBLE NULL ,
  `ultimo` DOUBLE NULL ,
  `maximo` DOUBLE NULL ,
  `minimo` DOUBLE NULL ,
  `compra` DOUBLE NULL ,
  `venda` DOUBLE NULL ,
  `negocios` INT NULL ,
  `volume_contratos` INT NULL ,
  `volume_financeiro` DOUBLE NULL ,
  `contratos_aberto` INT NULL ,
  PRIMARY KEY (`ativo_id`, `data`) ,
  CONSTRAINT `fk_CotacaoAtivo_Ativo`
    FOREIGN KEY (`ativo_id` )
    REFERENCES `dados`.`Ativo` (`idAtivo` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



-- -----------------------------------------------------
-- Table `dados`.`CotacaoMoeda`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`CotacaoMoeda` (
  `moeda_id` SMALLINT NOT NULL ,
  `data` DATE NOT NULL ,
  `compra` DOUBLE NULL ,
  `venda` DOUBLE NULL ,
  `par_compra` DOUBLE NULL ,
  `par_venda` DOUBLE NULL ,
  PRIMARY KEY (`moeda_id`, `data`) ,
  CONSTRAINT `fk_CotacaoMoeda_Moeda`
    FOREIGN KEY (`moeda_id` )
    REFERENCES `dados`.`Moeda` (`idMoeda` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



-- -----------------------------------------------------
-- Table `dados`.`CategoriasAtivo`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`CategoriasAtivo` (
  `ativo_id` INT NOT NULL ,
  `categoria_id` SMALLINT NOT NULL ,
  PRIMARY KEY (`ativo_id`, `categoria_id`) ,
  CONSTRAINT `fk_CategoriasAtivo_Ativo`
    FOREIGN KEY (`ativo_id` )
    REFERENCES `dados`.`Ativo` (`idAtivo` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_CategoriasAtivo_Categoria`
    FOREIGN KEY (`categoria_id` )
    REFERENCES `dados`.`Categoria` (`idCategoria` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



-- -----------------------------------------------------
-- Table `dados`.`UnidadePadrao`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`UnidadePadrao` (
  `unidade_id` SMALLINT NOT NULL ,
  `tipo` CHAR NOT NULL ,
  PRIMARY KEY (`unidade_id`, `tipo`) ,
  CONSTRAINT `fk_UnidadePadrao_Unidade`
    FOREIGN KEY (`unidade_id` )
    REFERENCES `dados`.`Unidade` (`idUnidade` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `tipo_UNIQUE` ON `dados`.`UnidadePadrao` (`tipo` ASC) ;




-- -----------------------------------------------------
-- Table `dados`.`CategoriasFamiliaContratos`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `dados`.`CategoriasFamiliaContratos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `familia_contratos_id` INT NOT NULL ,
  `categoria_id` SMALLINT NOT NULL ,
  PRIMARY KEY (`id`) ,
  CONSTRAINT `fk_CategoriasFamiliaContratos_Categoria`
    FOREIGN KEY (`categoria_id` )
    REFERENCES `dados`.`Categoria` (`idCategoria` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_CategoriasFamiliaContratos_FamiliaContratos`
    FOREIGN KEY (`familia_contratos_id` )
    REFERENCES `dados`.`FamiliaContratos` (`idFamiliaContratos` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;




SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
