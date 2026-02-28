function main_Q3_demo(population, expLosses, DIs)
%MAIN_Q3_DEMO  Q3 — Impact of gambling: projected R over time, social-harm
%  mapping, and intervention effectiveness.
%
%  Plots produced:
%    1  R distribution histogram
%    2  R projected over 10 years by AGE group
%    3  R projected over 10 years by GENDER
%    4  R projected over 10 years by COUNTRY/REGION
%    5  Social-impact dose-response curves (debt, depression, divorce, etc.)
%    6  Current mean social-harm rates by age group
%    7  Intervention effectiveness: before / after R reduction
%    8  Cascaded outcome improvement from a combined intervention

    fprintf('\n===== Q3: Impact of Gambling — What''s at Stake =====\n');

    % ---------- setup ----------
    N = numel(expLosses);
    R      = nan(N, 1);
    ages   = zeros(N, 1);
    genders = cell(N, 1);
    countries = cell(N, 1);
    regions = cell(N, 1);

    for i = 1:N
        p = population(i).person;
        ages(i)      = p.age;
        genders{i}   = p.gender;
        countries{i}  = p.country;
        regions{i}    = p.region;
        if DIs(i) > 0
            R(i) = -expLosses(i) / DIs(i);
        end
    end

    valid = ~isnan(R) & R > 0;
    Rv    = R(valid);
    fprintf('Mean R:   %.2f%%\n', 100*mean(Rv));
    fprintf('Median R: %.2f%%\n', 100*median(Rv));
    fprintf('High-risk (R>=15%%): %.1f%%\n', ...
        100*sum(R >= 0.15 & valid)/sum(valid));

    % ============================================================
    %  PLOT 1 — Distribution of R
    % ============================================================
    figure('Name','Q3-1: R Distribution');
    histogram(100*Rv, 40, 'FaceColor', [0.20 0.56 0.87]);
    xlabel('Gambling Loss as % of Disposable Income');
    ylabel('Count'); grid on;
    title('Q3: Distribution of R = Gambling Expense / DI');

    % ============================================================
    %  HELPER: Projection parameters
    % ============================================================
    years     = 2024:2034;
    nYears    = numel(years);
    annualGrowth = 0.09;  % online-gambling market ~9% CAGR
    growthCurve  = (1 + annualGrowth) .^ (0:nYears-1);

    % ============================================================
    %  PLOT 2 — R over time by AGE GROUP
    % ============================================================
    ageEdges   = [18 30 45 65 76];
    ageLabels  = {'18-29','30-44','45-64','65+'};
    nAgeGroups = numel(ageLabels);
    ageSensitivity = [1.25, 1.10, 0.95, 0.80];

    R_age_time = zeros(nAgeGroups, nYears);
    for g = 1:nAgeGroups
        mask = valid & ages >= ageEdges(g) & ages < ageEdges(g+1);
        if sum(mask) > 0
            baseR = mean(R(mask));
        else
            baseR = mean(Rv);
        end
        R_age_time(g,:) = baseR * growthCurve * ageSensitivity(g);
    end

    figure('Name','Q3-2: R Over Time by Age');
    colors = lines(nAgeGroups);
    hold on;
    for g = 1:nAgeGroups
        plot(years, 100*R_age_time(g,:), '-o', 'LineWidth', 2, ...
            'Color', colors(g,:), 'MarkerSize', 4, ...
            'DisplayName', ageLabels{g});
    end
    hold off;
    xlabel('Year'); ylabel('R (%)');
    title('Q3: Projected Gambling-to-DI Ratio by Age Group');
    legend('Location','northwest'); grid on;

    % ============================================================
    %  PLOT 3 — R over time by GENDER
    % ============================================================
    genderLabels = {'male','female'};
    genderSens   = [1.15, 0.85];
    R_gen_time   = zeros(2, nYears);

    for g = 1:2
        mask = valid & strcmpi(genders, genderLabels{g});
        if sum(mask) > 0
            baseR = mean(R(mask));
        else
            baseR = mean(Rv);
        end
        R_gen_time(g,:) = baseR * growthCurve * genderSens(g);
    end

    figure('Name','Q3-3: R Over Time by Gender');
    hold on;
    plot(years, 100*R_gen_time(1,:), '-s', 'LineWidth', 2, ...
        'Color', [0.15 0.45 0.72], 'MarkerSize', 5, 'DisplayName', 'Male');
    plot(years, 100*R_gen_time(2,:), '-d', 'LineWidth', 2, ...
        'Color', [0.85 0.33 0.10], 'MarkerSize', 5, 'DisplayName', 'Female');
    hold off;
    xlabel('Year'); ylabel('R (%)');
    title('Q3: Projected Gambling-to-DI Ratio by Gender');
    legend('Location','northwest'); grid on;

    % ============================================================
    %  PLOT 4 — R over time by COUNTRY / REGION
    % ============================================================
    allRegions  = {'Northeast','Midwest','South','West', ...
                   'England','Wales','Scotland','Northern Ireland'};
    regSens     = [1.05, 0.95, 1.10, 1.12, ...
                   1.08, 0.90, 0.95, 0.88];
    nRegs       = numel(allRegions);
    R_reg_time  = zeros(nRegs, nYears);

    for j = 1:nRegs
        mask = valid & strcmpi(regions, allRegions{j});
        if sum(mask) > 0
            baseR = mean(R(mask));
        else
            baseR = mean(Rv);
        end
        R_reg_time(j,:) = baseR * growthCurve * regSens(j);
    end

    figure('Name','Q3-4: R Over Time by Region');
    cmap = [lines(4); lines(4)*0.7 + 0.3];
    hold on;
    lineStyles = {'-o','-s','-d','-^', '--o','--s','--d','--^'};
    for j = 1:nRegs
        plot(years, 100*R_reg_time(j,:), lineStyles{j}, 'LineWidth', 1.5, ...
            'Color', cmap(j,:), 'MarkerSize', 4, ...
            'DisplayName', allRegions{j});
    end
    hold off;
    xlabel('Year'); ylabel('R (%)');
    title('Q3: Projected R by Country / Region');
    legend('Location','northwest','NumColumns',2); grid on;

    % ============================================================
    %  Social-Impact Dose-Response Functions
    %  Each maps R -> probability of harmful outcome (logistic)
    %    rate = L / (1 + exp(-k*(R - R_mid)))
    %  Calibrated to epidemiological estimates:
    %    R~5% -> mild, R~20% -> severe
    % ============================================================
    outcomes = struct( ...
        'name',  {'Debt','Depression','Divorce','Drug Addiction','School Decline'}, ...
        'L',     { 0.40,     0.45,      0.30,       0.25,           0.50  }, ...
        'k',     { 25,       22,        28,         30,             25    }, ...
        'Rmid',  { 0.12,     0.13,      0.14,       0.15,           0.10  });
    nOutcomes = numel(outcomes);

    impactRate = @(R_in, L, k, Rmid) L ./ (1 + exp(-k*(R_in - Rmid)));

    % ============================================================
    %  PLOT 5 — Dose-response curves
    % ============================================================
    Rsweep = linspace(0, 0.30, 200);
    figure('Name','Q3-5: Dose-Response Curves');
    hold on;
    oColors = [0.84 0.15 0.16; 0.17 0.63 0.17; 0.58 0.40 0.74; ...
               0.55 0.34 0.29; 0.89 0.47 0.76];
    for j = 1:nOutcomes
        y = 100*impactRate(Rsweep, outcomes(j).L, outcomes(j).k, outcomes(j).Rmid);
        plot(100*Rsweep, y, 'LineWidth', 2.5, 'Color', oColors(j,:), ...
            'DisplayName', outcomes(j).name);
    end
    hold off;
    xlabel('R = Gambling Expense / DI (%)');
    ylabel('Probability of Harm (%)');
    title('Q3: How Gambling Ratio Drives Social Harm');
    legend('Location','northwest'); grid on;
    xlim([0 30]);

    % ============================================================
    %  PLOT 6 — Current social-harm rates by age group (bar chart)
    % ============================================================
    harmByAge = zeros(nAgeGroups, nOutcomes);
    for g = 1:nAgeGroups
        mask = valid & ages >= ageEdges(g) & ages < ageEdges(g+1);
        if sum(mask) == 0, continue; end
        meanR_g = mean(R(mask));
        for j = 1:nOutcomes
            harmByAge(g,j) = 100 * impactRate(meanR_g, ...
                outcomes(j).L, outcomes(j).k, outcomes(j).Rmid);
        end
    end

    figure('Name','Q3-6: Current Harm by Age Group');
    b = bar(harmByAge);
    for j = 1:nOutcomes
        b(j).FaceColor = oColors(j,:);
    end
    set(gca, 'XTickLabel', ageLabels);
    xlabel('Age Group'); ylabel('Estimated Harm Rate (%)');
    title('Q3: Social Harm Rates by Age Group (Current R)');
    legend({outcomes.name}, 'Location', 'northeastoutside'); grid on;

    % ============================================================
    %  PLOT 7 — Intervention effectiveness
    %  Each intervention reduces R by a multiplicative factor.
    % ============================================================
    interventions = struct( ...
        'name',      {'Spending Caps','Self-Exclusion','Ad Bans', ...
                      'Education','Combined'}, ...
        'reduction', { 0.30,           0.25,            0.15, ...
                       0.10,           0.60 });
    nInt = numel(interventions);

    R_baseline = mean(Rv);
    R_after    = zeros(1, nInt);
    for k = 1:nInt
        R_after(k) = R_baseline * (1 - interventions(k).reduction);
    end

    figure('Name','Q3-7: Intervention Effect on R');
    barData = [100*R_baseline*ones(1,nInt); 100*R_after];
    bh = bar(barData');
    bh(1).FaceColor = [0.85 0.33 0.10];
    bh(2).FaceColor = [0.17 0.63 0.17];
    set(gca, 'XTickLabel', {interventions.name});
    ylabel('Mean R (%)');
    title('Q3: Gambling Ratio Before vs After Intervention');
    legend({'Before','After'}, 'Location','northeast'); grid on;

    fprintf('\nInterventions (baseline R = %.2f%%):\n', 100*R_baseline);
    for k = 1:nInt
        fprintf('  %-18s  R -> %.2f%%  (%.0f%% reduction)\n', ...
            interventions(k).name, 100*R_after(k), ...
            100*interventions(k).reduction);
    end

    % ============================================================
    %  PLOT 8 — Cascaded outcome improvement (combined intervention)
    % ============================================================
    R_combined = R_baseline * (1 - 0.60);
    harm_before = zeros(1, nOutcomes);
    harm_after  = zeros(1, nOutcomes);
    for j = 1:nOutcomes
        harm_before(j) = 100*impactRate(R_baseline, ...
            outcomes(j).L, outcomes(j).k, outcomes(j).Rmid);
        harm_after(j)  = 100*impactRate(R_combined, ...
            outcomes(j).L, outcomes(j).k, outcomes(j).Rmid);
    end

    figure('Name','Q3-8: Cascaded Outcome Improvement');
    X = 1:nOutcomes;
    bh2 = bar(X, [harm_before; harm_after]');
    bh2(1).FaceColor = [0.85 0.33 0.10];
    bh2(2).FaceColor = [0.17 0.63 0.17];
    set(gca, 'XTickLabel', {outcomes.name});
    ylabel('Estimated Harm Rate (%)');
    title('Q3: Social Harm Before vs After Combined Intervention');
    legend({'Before (current R)','After (60% R reduction)'}, ...
        'Location','northeast'); grid on;

    fprintf('\nCascaded outcome improvement (combined intervention, 60%% R cut):\n');
    for j = 1:nOutcomes
        fprintf('  %-20s  %.1f%%  ->  %.1f%%  (%.1f pp reduction)\n', ...
            outcomes(j).name, harm_before(j), harm_after(j), ...
            harm_before(j) - harm_after(j));
    end

    % ============================================================
    %  PLOT 9 — Projected harm trajectories over time (no intervention
    %           vs with combined intervention)
    % ============================================================
    figure('Name','Q3-9: Harm Trajectories Over Time');
    tiledlayout(2, 3, 'TileSpacing', 'compact', 'Padding', 'compact');

    for j = 1:nOutcomes
        nexttile;
        R_t_none = R_baseline * growthCurve;
        R_t_int  = R_combined * growthCurve;
        h_none = 100*impactRate(R_t_none, outcomes(j).L, outcomes(j).k, outcomes(j).Rmid);
        h_int  = 100*impactRate(R_t_int,  outcomes(j).L, outcomes(j).k, outcomes(j).Rmid);
        hold on;
        plot(years, h_none, '-o', 'LineWidth', 2, ...
            'Color', [0.85 0.33 0.10], 'MarkerSize', 3);
        plot(years, h_int,  '-s', 'LineWidth', 2, ...
            'Color', [0.17 0.63 0.17], 'MarkerSize', 3);
        hold off;
        title(outcomes(j).name);
        xlabel('Year'); ylabel('Rate (%)');
        grid on;
        if j == 1
            legend({'No action','Combined intervention'}, ...
                'Location','northwest','FontSize',7);
        end
    end
    sgtitle('Q3: Projected Social-Harm Trajectories (2024-2034)');

    fprintf('\nQ3 demo complete — 9 figures generated.\n');
end
