function [Y, tau_eff] = afterTaxIncome(S, country)
%AFTERTAXINCOME Compute after-tax income using progressive marginal brackets.
%   [Y, tau_eff] = afterTaxIncome(S, country)
%   S       - annual gross salary (pre-tax)
%   country - 'US' or 'UK'
%
%   Uses marginal rates so that Y is continuous and monotonically increasing.

    brackets = [0, 30000, 80000, 150000, Inf];

    if strcmpi(country, 'US')
        rates = [0.10, 0.18, 0.24, 0.30];
    else
        rates = [0.12, 0.20, 0.26, 0.32];
    end

    tax = 0;
    for k = 1:numel(rates)
        lo = brackets(k);
        hi = brackets(k+1);
        taxable = max(0, min(S, hi) - lo);
        tax = tax + rates(k) * taxable;
    end

    Y = S - tax;
    if S > 0
        tau_eff = tax / S;
    else
        tau_eff = 0;
    end
end
