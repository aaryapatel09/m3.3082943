function main_Q1_demo(usData, ukData)
%MAIN_Q1_DEMO Demonstrate Q1 disposable income model with examples and a plot.

    % ---- Example individuals ----
    examples = {
        'US', 'West',    28,  70000, 1;
        'US', 'Midwest', 42, 110000, 4;
        'UK', 'England', 35,  60000, 2;
    };

    fprintf('\n===== Q1: Disposable Income Model =====\n');
    fprintf('%-8s %-12s %5s %10s %10s %10s %10s\n', ...
        'Country','Region','Age','Salary','Y','E','DI');
    fprintf('%s\n', repmat('-', 1, 70));

    for i = 1:size(examples, 1)
        c   = examples{i,1};
        r   = examples{i,2};
        a   = examples{i,3};
        sal = examples{i,4};
        hh  = examples{i,5};

        [DI, Y, E] = disposableIncome(sal, a, hh, c, r, usData, ukData);
        fprintf('%-8s %-12s %5d %10.0f %10.0f %10.0f %10.0f\n', ...
            c, r, a, sal, Y, E, DI);
    end

    % ---- Line chart: DI vs salary for different household sizes ----
    salaries = linspace(20000, 200000, 200);
    hhSizes  = [1, 2, 4];
    fixedAge = 35;
    fixedCountry = 'US';
    fixedRegion  = 'West';

    figure('Name', 'Q1: Disposable Income vs Salary');
    hold on;
    colors = {'b', 'r', 'k'};
    for j = 1:numel(hhSizes)
        diVec = zeros(size(salaries));
        for k = 1:numel(salaries)
            diVec(k) = disposableIncome(salaries(k), fixedAge, hhSizes(j), ...
                fixedCountry, fixedRegion, usData, ukData);
        end
        plot(salaries/1000, diVec/1000, colors{j}, 'LineWidth', 1.5, ...
            'DisplayName', sprintf('h = %d', hhSizes(j)));
    end
    hold off;
    xlabel('Annual Gross Salary ($k)');
    ylabel('Disposable Income ($k)');
    title(sprintf('Q1: DI vs Salary (US West, age %d)', fixedAge));
    legend('Location', 'northwest');
    grid on;

    fprintf('\nQ1 demo complete.\n');
end
