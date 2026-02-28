%% main_m3.m -- M3 Challenge 2026: The Rise of Online Gambling
%  Driver script for Q1 (Disposable Income), Q2 (Gambling Gain/Loss),
%  and Q3 (Impact Metrics).
%
%  Run this file to produce all tables and figures.

clear; clc; close all;

dataFile = 'M3-Challenge-Problem-Data-2026.xlsx';

fprintf('Loading U.S. expenditure data...\n');
usData = loadUSExpenditureData(dataFile);

fprintf('Loading U.K. expenditure data...\n');
ukData = loadUKExpenditureData(dataFile);

fprintf('Loading U.S. betting survey data...\n');
usBetData = loadUSBettingData(dataFile);

fprintf('Data loaded successfully.\n');

%% Q1 -- Disposable Income
main_Q1_demo(usData, ukData);

%% Q2 -- Gambling Gain/Loss
[population, expLosses, DIs] = main_Q2_demo(usData, ukData, usBetData);

%% Q3 -- Impact Metrics
main_Q3_demo(population, expLosses, DIs);

fprintf('\n===== All M3 demos complete. =====\n');
