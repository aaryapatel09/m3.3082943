function [DI, DI_lo, DI_hi, Y, E] = disposableIncome_CI(S, age, h, country, region, usData, ukData)
%DISPOSABLEINCOME_CI  Disposable income with 95% confidence interval.
%
%   [DI, DI_lo, DI_hi, Y, E] = disposableIncome_CI(S, age, h, country,
%       region, usData, ukData)
%
%   Propagates uncertainty in three model parameters:
%     theta  (essential share)    — CV = 0.20  (individual spending varies)
%     f_r    (region multiplier)  — CV = 0.10  (regional cost-of-living)
%     gamma  (household exponent) — sigma = 0.10 around 0.70
%
%   E = theta * S * f_r * f_h   =>   DI = Y - E
%   The CI comes from the combined relative uncertainty in E.

    [DI, Y, E] = disposableIncome(S, age, h, country, region, usData, ukData);

    cv_theta = 0.20;
    cv_fr    = 0.10;
    cv_fh    = 0.15;

    cv_E = sqrt(cv_theta^2 + cv_fr^2 + cv_fh^2);

    E_lo = E * (1 - 1.96 * cv_E);
    E_hi = E * (1 + 1.96 * cv_E);

    E_lo = max(E_lo, 0);
    E_hi = min(E_hi, Y);

    DI_hi = max(Y - E_lo, 0);
    DI_lo = max(Y - E_hi, 0);
end
