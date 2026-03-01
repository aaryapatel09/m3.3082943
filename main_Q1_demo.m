function main_Q1_demo(usData, ukData)
%MAIN_Q1_DEMO Demonstrate Q1 disposable income model with 95% CI.

    % ---- Example individuals ----
    examples = {
        'US', 'West',    28,  70000, 1;
        'US', 'Midwest', 42, 110000, 4;
        'UK', 'England', 35,  60000, 2;
    };

    fprintf('\n===== Q1: Disposable Income Model (with 95%% CI) =====\n');
    fprintf('%-8s %-12s %5s %10s %10s %10s %14s\n', ...
        'Country','Region','Age','Salary','Y','DI','95% CI');
    fprintf('%s\n', repmat('-', 1, 75));

    for i = 1:size(examples, 1)
        c   = examples{i,1};
        r   = examples{i,2};
        a   = examples{i,3};
        sal = examples{i,4};
        hh  = examples{i,5};

        [DI, DI_lo, DI_hi, Y, ~] = disposableIncome_CI(sal, a, hh, c, r, usData, ukData);
        fprintf('%-8s %-12s %5d %10.0f %10.0f %10.0f  [%6.0f, %6.0f]\n', ...
            c, r, a, sal, Y, DI, DI_lo, DI_hi);
    end

    % ---- Line chart: DI vs salary with 95% CI shading ----
    salaries = linspace(20000, 200000, 200);
    hhSizes  = [1, 2, 4];
    fixedAge = 35;
    fixedCountry = 'US';
    fixedRegion  = 'West';

    figure('Name', 'Q1: Disposable Income vs Salary (with 95% CI)');
    hold on;
    colors = [0.12 0.47 0.71;  0.84 0.15 0.16;  0.17 0.63 0.17];

    for j = 1:numel(hhSizes)
        diVec   = zeros(size(salaries));
        diLo    = zeros(size(salaries));
        diHi    = zeros(size(salaries));
        for k = 1:numel(salaries)
            [diVec(k), diLo(k), diHi(k)] = disposableIncome_CI( ...
                salaries(k), fixedAge, hhSizes(j), ...
                fixedCountry, fixedRegion, usData, ukData);
        end

        fill([salaries/1000, fliplr(salaries/1000)], ...
             [diHi/1000, fliplr(diLo/1000)], ...
             colors(j,:), 'FaceAlpha', 0.15, 'EdgeColor', 'none', ...
             'HandleVisibility', 'off');
        plot(salaries/1000, diVec/1000, 'Color', colors(j,:), ...
            'LineWidth', 2, 'DisplayName', sprintf('h = %d', hhSizes(j)));
    end
    hold off;
    xlabel('Annual Gross Salary ($k)');
    ylabel('Disposable Income ($k)');
    title(sprintf('Q1: DI vs Salary with 95%% CI (US West, age %d)', fixedAge));
    legend('Location', 'northwest');
    grid on;

    fprintf('\nQ1 demo complete.\n');
end
