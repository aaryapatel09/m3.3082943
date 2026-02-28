function [DI, Y, E] = disposableIncome(S, age, h, country, region, usData, ukData)
%DISPOSABLEINCOME Estimate annual disposable income for an individual.
%   [DI, Y, E] = disposableIncome(S, age, h, country, region, usData, ukData)
%
%   Inputs:
%     S       - annual gross salary
%     age     - age in years
%     h       - household size (persons supported)
%     country - 'US' or 'UK'
%     region  - region string (e.g. 'West', 'England')
%     usData  - struct from loadUSExpenditureData
%     ukData  - struct from loadUKExpenditureData
%
%   Outputs:
%     DI - disposable income (Y - E)
%     Y  - after-tax income
%     E  - estimated essential annual expenditures

    Y = afterTaxIncome(S, country);

    if strcmpi(country, 'US')
        theta = baseEssentialShare_US(age, usData);
    else
        theta = baseEssentialShare_UK(age, S, ukData);
    end

    E_base = theta * S;

    f_r = regionMultiplier(region, country, usData, ukData);
    f_h = householdMultiplier(h, age, country, usData, ukData);

    E = E_base * f_r * f_h;
    E = min(E, Y);

    DI = Y - E;
end
