function [population, expLosses, DIs] = main_Q2_demo(usData, ukData, usBetData)
%MAIN_Q2_DEMO Monte Carlo simulation of gambling outcomes for N=1000 individuals.

    rng(42);
    N = 1000;

    countries  = {'US', 'UK'};
    usRegions  = {'Northeast','Midwest','South','West'};
    ukRegions  = {'England','Wales','Scotland','Northern Ireland'};
    genders    = {'male', 'female'};
    educations = {'nocollege', 'college'};
    risks      = {'low', 'medium', 'high'};
    styles     = {'conservative', 'mixed', 'highrisk'};

    population = struct([]);
    expLosses  = zeros(N, 1);
    DIs        = zeros(N, 1);

    for i = 1:N
        p.salary = 20000 + rand * 180000;
        p.age    = randi([18, 75]);
        p.hhsize = randi([1, 5]);
        p.country = countries{randi(2)};

        if strcmpi(p.country, 'US')
            p.region = usRegions{randi(4)};
        else
            p.region = ukRegions{randi(4)};
        end

        p.gender        = genders{randi(2)};
        p.education     = educations{randi(2)};
        p.riskTolerance = risks{randi(3)};
        p.style         = styles{randi(3)};

        [expLoss, ~, ~, ~] = gamblingOutcome(p, usData, ukData, usBetData);
        DI = disposableIncome(p.salary, p.age, p.hhsize, ...
            p.country, p.region, usData, ukData);

        population(i).person = p;
        expLosses(i) = expLoss;
        DIs(i)       = DI;
    end

    % ---- Plots ----
    figure('Name', 'Q2: Expected Annual Loss Histogram');
    histogram(expLosses, 40);
    xlabel('Expected Annual Net Outcome ($)');
    ylabel('Count');
    title('Q2: Distribution of Expected Annual Gambling Losses');
    grid on;

    figure('Name', 'Q2: DI vs Annual Loss');
    scatter(DIs/1000, -expLosses/1000, 8, 'filled', 'MarkerFaceAlpha', 0.4);
    xlabel('Disposable Income ($k)');
    ylabel('Expected Annual Loss ($k)');
    title('Q2: Disposable Income vs Expected Annual Loss');
    grid on;

    fprintf('\n===== Q2: Gambling Outcome Simulation (N=%d) =====\n', N);
    fprintf('Mean expected loss:  $%.0f\n', mean(expLosses));
    fprintf('Median expected loss: $%.0f\n', median(expLosses));
    fprintf('Max expected loss:   $%.0f\n', min(expLosses));
    fprintf('Q2 demo complete.\n');
end
