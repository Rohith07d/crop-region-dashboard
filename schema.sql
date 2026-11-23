-- =============================================================================
-- Crop Regional Water Intelligence Database Schema
-- Database: crop_regional_db
-- =============================================================================

CREATE DATABASE IF NOT EXISTS crop_regional_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE crop_regional_db;

-- -----------------------------------------------------------------------------
-- 1. Agricultural Regions Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS regions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL UNIQUE,
    state VARCHAR(50) NOT NULL,
    latitude DECIMAL(8, 4) NOT NULL,
    longitude DECIMAL(8, 4) NOT NULL,
    soil_type ENUM('Black_Clay', 'Red_Sandy', 'Alluvial_Loam') NOT NULL,
    available_water_liters DOUBLE NOT NULL DEFAULT 500000.0,
    -- Fallback/cached weather parameters if live Open-Meteo is unreachable
    temp_max FLOAT NOT NULL DEFAULT 34.0,
    temp_min FLOAT NOT NULL DEFAULT 24.0,
    humidity FLOAT NOT NULL DEFAULT 55.0,
    wind_speed FLOAT NOT NULL DEFAULT 2.5,
    solar_radiation FLOAT NOT NULL DEFAULT 18.0,
    rainfall_10d FLOAT NOT NULL DEFAULT 5.0,
    et0_10d FLOAT NOT NULL DEFAULT 45.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_region_name (region_name)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 2. Farmer Plots Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS region_plots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    region_id INT NOT NULL,
    plot_code VARCHAR(50) NOT NULL,
    farmer_name VARCHAR(100) NOT NULL,
    crop_type VARCHAR(50) NOT NULL,
    growth_stage ENUM('Initial', 'Development', 'Mid_Season', 'Late_Season') NOT NULL DEFAULT 'Mid_Season',
    area_acres FLOAT NOT NULL DEFAULT 1.5,
    soil_moisture_top FLOAT NOT NULL DEFAULT 0.35,
    soil_moisture_root FLOAT NOT NULL DEFAULT 0.38,
    soil_moisture_prof FLOAT NOT NULL DEFAULT 0.42,
    prev_soil_moisture_root FLOAT NOT NULL DEFAULT 0.38,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (region_id) REFERENCES regions(id) ON DELETE CASCADE,
    UNIQUE KEY uq_region_plot (region_id, plot_code),
    INDEX idx_crop_type (crop_type),
    INDEX idx_growth_stage (growth_stage)
) ENGINE=InnoDB;
