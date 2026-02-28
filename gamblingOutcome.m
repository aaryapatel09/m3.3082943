function [expLoss, sigma, fracDI, G] = gamblingOutcome(person, usData, ukData, usBetData)
%GAMBLINGOUTCOME Predict one-year expected gain/loss from sports betting.
%   [expLoss, sigma, fracDI, G] = gamblingOutcome(person, usData, ukData, usBetData)
%
%   person is a struct with fields:
%     salary, age, hhsize, region, country, gender, education,
%     riskTolerance ('low'|'medium'|'high'),
%     style ('conservative'|'mixed'|'highrisk')
%
%   Returns:
%     expLoss - expected annual net outcome (negative = loss)
%     sigma   - 1-sigma spread approximation
%     fracDI  - |expLoss| / DI
%     G       - annual amount staked

    DI = disposableIncome(person.salary, person.age, person.hhsize, ...
        person.country, person.region, usData, ukData);

    % --- Monthly stake from risk tolerance, shifted by demographics ---
    M_base = struct('low', 50, 'medium', 300, 'high', 800);
    M = M_base.(lower(person.riskTolerance));

    ageFactor = 1.0;
    if person.age < 35,      ageFactor = 1.15;
    elseif person.age >= 65,  ageFactor = 0.70;
    end
    genderFactor = 1.0;
    if strcmpi(person.gender, 'male'),   genderFactor = 1.10;
    elseif strcmpi(person.gender, 'female'), genderFactor = 0.85;
    end

    edFactor = 1.0;
    if strcmpi(person.education, 'college'), edFactor = 1.05; end

    M = M * ageFactor * genderFactor * edFactor;
    G_raw = 12 * M;

    % Risk-dependent cap: high-risk gamblers may wager most of their DI
    switch lower(person.riskTolerance)
        case 'low',    capFrac = 0.15;
        case 'medium', capFrac = 0.40;
        case 'high',   capFrac = 1.00;
        otherwise,     capFrac = 0.40;
    end
    G = min(G_raw, capFrac * max(DI, 0));

    % --- Bookmaker edge by style ---
    switch lower(person.style)
        case 'conservative', baseEdge = 0.04;
        case 'mixed',        baseEdge = 0.07;
        case 'highrisk',     baseEdge = 0.12;
        otherwise,           baseEdge = 0.07;
    end

    % Chase-bet escalation: survey data shows 52% of bettors chase losses,
    % which compounds the effective house edge for riskier gamblers.
    switch lower(person.riskTolerance)
        case 'low',    chaseMult = 1.00;
        case 'medium', chaseMult = 1.20;
        case 'high',   chaseMult = 1.50;
        otherwise,     chaseMult = 1.20;
    end
    edge = baseEdge * chaseMult;

    expLoss = -edge * G;
    sigma   =  edge * G;
    fracDI  = -expLoss / max(DI, 1);
end
