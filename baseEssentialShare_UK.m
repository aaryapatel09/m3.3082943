function theta = baseEssentialShare_UK(age, salary, ukData)
%BASEESSENTIALSHARE_UK Return essential-spend / income ratio for a UK age/income group.
%   theta = baseEssentialShare_UK(age, salary, ukData)
%   Maps age -> age block, salary -> income quintile, returns ratio.

    bIdx = mapAgeToBlock(age, ukData.ageBounds);

    weeklyIncome = salary / 52;
    qIdx = findQuintile(weeklyIncome, ukData.quintileIncome);

    theta = ukData.essentialWeekly(bIdx, qIdx) / ukData.quintileIncome(qIdx);
end

function idx = mapAgeToBlock(age, bounds)
    idx = size(bounds, 1);
    for k = 1:size(bounds, 1)
        if age >= bounds(k,1) && age <= bounds(k,2)
            idx = k;
            return;
        end
    end
end

function qIdx = findQuintile(weeklyInc, quintileIncome)
    % Assign to the quintile whose midpoint boundary is closest
    boundaries = (quintileIncome(1:end-1) + quintileIncome(2:end)) / 2;
    qIdx = 1;
    for k = 1:numel(boundaries)
        if weeklyInc > boundaries(k)
            qIdx = k + 1;
        end
    end
end
