function main_Q3_demo(population, expLosses, DIs)
%MAIN_Q3_DEMO Compute and visualise impact metrics from Q2 outputs.
%   R       = fraction of DI lost to gambling
%   DeltaW  = missed wealth if losses had been invested over 20 years
%   High-risk flag when R >= 0.15

    r_inv = 0.04;   % real annual return
    T     = 20;     % investment horizon (years)

    N = numel(expLosses);
    R      = nan(N, 1);
    DeltaW = nan(N, 1);
    ages   = zeros(N, 1);

    for i = 1:N
        ages(i) = population(i).person.age;
        if DIs(i) > 0
            R(i)      = -expLosses(i) / DIs(i);
            DeltaW(i) = -expLosses(i) * ((1 + r_inv)^T - 1) / r_inv;
        end
    end

    fprintf('\n===== Q3: Impact Metrics =====\n');
    validR = R(~isnan(R) & R > 0 & R < 1);
    fprintf('Mean loss as %% of DI: %.1f%%\n', 100*mean(validR));
    fprintf('Median loss as %% of DI: %.1f%%\n', 100*median(validR));
    highRiskAll = sum(R >= 0.15 & ~isnan(R)) / sum(~isnan(R));
    fprintf('Share of high-risk individuals (R>=15%%): %.1f%%\n', 100*highRiskAll);

    % ---- Plot 1: Histogram of R (%) ----
    figure('Name', 'Q3: Loss as % of DI');
    Rpct = 100 * R(~isnan(R) & R > 0 & R < 1);
    histogram(Rpct, 40);
    xlabel('Gambling Loss as % of Disposable Income');
    ylabel('Count');
    title('Q3: Distribution of Gambling Loss Relative to DI');
    grid on;

    % ---- Plot 2: High-risk share by age group ----
    ageEdges  = [18, 30, 45, 65, 76];
    ageLabels = {'18-29', '30-44', '45-64', '65+'};
    nGroups = numel(ageLabels);
    highRiskFrac = zeros(1, nGroups);
    for g = 1:nGroups
        mask = ages >= ageEdges(g) & ages < ageEdges(g+1) & ~isnan(R);
        if sum(mask) > 0
            highRiskFrac(g) = sum(R(mask) >= 0.15) / sum(mask);
        end
    end

    figure('Name', 'Q3: High-Risk Share by Age Group');
    bar(100 * highRiskFrac);
    set(gca, 'XTickLabel', ageLabels);
    xlabel('Age Group');
    ylabel('High-Risk Share (%)');
    title('Q3: Percentage with Gambling Loss >= 15% of DI');
    grid on;

    % ---- Plot 3: Scatter of annual loss vs missed wealth ----
    validIdx = ~isnan(DeltaW) & DeltaW > 0;
    figure('Name', 'Q3: Missed Wealth Scatter');
    scatter(-expLosses(validIdx)/1000, DeltaW(validIdx)/1000, 8, ...
        'filled', 'MarkerFaceAlpha', 0.4);
    xlabel('Annual Gambling Loss ($k)');
    ylabel(sprintf('Missed Wealth After %d Years ($k)', T));
    title('Q3: Annual Loss vs Missed Compound Wealth');
    grid on;

    fprintf('Q3 demo complete.\n');
end
